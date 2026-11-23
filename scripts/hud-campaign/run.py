"""Queue whole VOD intervals, report 4 Hz OCR results and recycle tested media."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import fcntl
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import time

from media import download

BUNDLED = Path(__file__).resolve().parent
ROOT = Path(os.environ.get('TFT_CAMPAIGN_DIR', '/workspace/scratch/tft-test-matches/campaign')).resolve()
MEDIA = ROOT.parent
PROJECT = Path(os.environ.get('TFT_PROJECT_DIR', str(BUNDLED.parents[1]))).resolve()
CGROUP = Path('/sys/fs/cgroup')
RESERVE_BYTES = 4 * 1024**3
INTERVAL = .25
MANIFESTS = (MEDIA / 'manifest.json', MEDIA / 'manifest-final4.json', ROOT / 'source-queue.json')
SNAPSHOT_FILES = ('scripts/hud-reader.py', 'scripts/hud_ocr.py', 'src/data/set18-hud.json')


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def json_file(path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def atomic_json(path, value):
    stage = path.with_suffix('.part')
    stage.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    stage.replace(path)


def sample_key(row):
    return f"{row['vod']}-{round(row['intendedStartSec'] * 1000)}"


def reserve_download(row):
    height = row.setdefault('requestedHeight', row.get('height', 720))
    length = row['intendedEndSec'] - row['intendedStartSec']
    bytes_per_second = 475_000 if height == 720 else 825_000
    row.setdefault('expectedBytes', int((length + 20) * bytes_per_second))


def snapshot():
    blobs = {name: (PROJECT / name).read_bytes() for name in SNAPSHOT_FILES}
    version = hashlib.sha256(b'\0'.join(blobs.values())).hexdigest()[:16]
    folder = ROOT / 'versions' / version
    for name, data in blobs.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return folder / 'scripts' / 'hud-reader.py', version


def stats_file(name):
    return dict((key, int(value)) for key, value in (line.split() for line in
                (CGROUP / name).read_text().splitlines()))


def capacity():
    count = len(os.sched_getaffinity(0))
    cpu, period = (CGROUP / 'cpu.max').read_text().split()
    return min(count, int(cpu) / int(period)) if cpu != 'max' else count


def metrics(raw, duration):
    delays = []
    coverage = Counter()
    distribution = Counter()
    cold = None
    last = None
    for line in raw:
        row = json.loads(line)
        frame = row['frame']
        if row['source'] != 'video' or row['mediaTimeMs'] != frame * 250:
            raise ValueError('Unexpected source or sample time')
        if last is not None and frame <= last['frame']:
            raise ValueError('Sample times must increase')
        last = row
        coverage['samples'] += 1
        delay = row['endToEndLatencyMs']
        if cold is None:
            cold = delay
        else:
            delays.append(delay)
            coverage['over250ms'] += row['deadlineMissed']
        coverage['ocrErrors'] += bool(row.get('error') or row.get('priceOcrError'))
        coverage['hudDetected'] += bool(row['hudDetected'])
        coverage['goldRead'] += row['gold'] is not None
        coverage['levelRead'] += row['level'] is not None
        slots = [slot for slot in row['shopSlots'] if slot is not None]
        coverage['anyShop'] += bool(slots)
        coverage['namedSlots'] += len(slots)
        for slot in slots:
            price = slot['price']
            if price is not None:
                coverage['pricedSlots'] += 1
                distribution[str(slot['cost']), str(price)] += 1
    if last is None or len(delays) < 1:
        raise ValueError('No useful OCR samples')
    coverage['dropped'] = last['droppedFrames']
    expected = round(duration / INTERVAL)
    total = coverage['samples'] + coverage['dropped']
    if total != last['frame'] + 1 or abs(total - expected) > 8:
        raise ValueError(f'Incomplete playback, accounted for {total} of about {expected} frames')
    delays.sort()
    return {**coverage, 'scheduledHz': 4, 'effectiveHz': round(coverage['samples'] / duration, 3),
        'lastSampleSec': last['mediaTimeMs'] / 1000, 'coldStartMs': cold,
        'p50Ms': delays[math.ceil(.5 * len(delays)) - 1], 'p95Ms': delays[math.ceil(.95 * len(delays)) - 1],
        'p99Ms': delays[math.ceil(.99 * len(delays)) - 1], 'maxMs': delays[-1],
        'tierAndPrice': {f'{tier}/{price}': n for (tier, price), n in sorted(distribution.items())},
        'accuracy': None}


def test(row, reader, version):
    name = sample_key(row)
    part = ROOT / 'results' / f'{name}.part.jsonl'
    log = ROOT / 'results' / f'{name}.stderr'
    output = ROOT / 'results' / f'{name}.jsonl.gz'
    started = now()
    started_clock = time.monotonic()
    profile = ROOT / 'profile-1080p.json'
    if not profile.is_file():
        profile = BUNDLED / 'profile-1080p.json'
    args = ['nice', '-n', '4', 'python3', str(reader), '--video', str(MEDIA / row['file']), '--interval', '0.25']
    if row['height'] == 1080 and profile.is_file():
        args.extend(['--profile', str(profile)])
    with part.open('w') as data, log.open('w') as stderr:
        subprocess.run(args, stdout=data, stderr=stderr, check=True, timeout=row['duration'] + 180)
    with part.open() as data:
        numbers = metrics(data, row['duration'])
    stage = output.with_suffix('.part.gz')
    with part.open('rb') as data, gzip.open(stage, 'wb', compresslevel=3) as compressed:
        shutil.copyfileobj(data, compressed)
    stage.replace(output)
    part.unlink()
    result = {'source': row, 'readerVersion': version, 'startedAtUtc': started, 'completedAtUtc': now(),
              'elapsedSeconds': round(time.monotonic() - started_clock, 1), 'concurrentLoadTest': True,
              'frameLog': str(output.relative_to(ROOT)), **numbers}
    atomic_json(ROOT / 'results' / f'{name}.json', result)
    return result


def import_sources(db):
    manifests = MANIFESTS if MANIFESTS[-1].is_file() else (*MANIFESTS[:2], BUNDLED / 'seed-sources.json')
    for manifest in manifests:
        for row in json_file(manifest, []):
            row['vod'] = row['source'].rsplit('/', 1)[1]
            if not row['vod'].isdigit() or Path(row['file']).name != row['file']:
                raise ValueError('Invalid source or filename')
            key = sample_key(row)
            a, b = row['intendedStartSec'], row['intendedEndSec']
            overlap = db.execute('SELECT id FROM samples WHERE vod=? AND start<? AND end>?', (row['vod'], b, a)).fetchone()
            if overlap or b <= a:
                continue
            if manifest in MANIFESTS[:2] and (MEDIA / row['file']).is_file():
                state = 'ready'
            else:
                state = 'queued'
                reserve_download(row)
            db.execute('INSERT INTO samples VALUES (?, ?, ?, ?, ?, ?, 0, NULL, NULL, NULL)',
                       (key, row['vod'], a, b, state, json.dumps(row)))
    db.commit()


def resume(db):
    for key, state, payload in db.execute('SELECT id, state, info FROM samples WHERE state IN ("ready", "testing", "downloading")'):
        row = json.loads(payload)
        summary = json_file(ROOT / 'results' / f'{key}.json', None)
        archived = ROOT / 'results' / f'{key}.jsonl.gz'
        if summary is not None and archived.is_file() and sample_key(summary['source']) == key:
            db.execute('UPDATE samples SET state="tested", result=?, error=NULL WHERE id=?', (json.dumps(summary), key))
        elif state == 'downloading' or not (MEDIA / row['file']).is_file():
            reserve_download(row)
            db.execute('UPDATE samples SET state="queued", info=? WHERE id=?', (json.dumps(row), key))
        else:
            db.execute('UPDATE samples SET state="ready" WHERE id=?', (key,))
    db.commit()


def report_sources(db):
    fields = ['source', 'vod', 'uploader', 'patch', 'intendedStartSec', 'intendedEndSec', 'mediaStartSec',
              'mediaEndSec', 'duration', 'height', 'file', 'readerVersion', 'completedAtUtc', 'deletedAtUtc', 'summary']
    stage = ROOT / 'tested-sources.part'
    with stage.open('w', newline='') as output:
        writer = csv.DictWriter(output, fields)
        writer.writeheader()
        for key, info, result, removed in db.execute(
                'SELECT id, info, result, deleted FROM samples WHERE state="tested" ORDER BY vod, start'):
            details = json.loads(result)
            row = json.loads(info) | {'deletedAtUtc': removed, 'readerVersion': details['readerVersion'],
                'completedAtUtc': details['completedAtUtc'], 'summary': f'results/{key}.json'}
            writer.writerow({field: row.get(field) for field in fields})
    stage.replace(ROOT / 'tested-sources.csv')


def remove_finished(db):
    verified = set(json_file(ROOT / 'verified-matches.json', []))
    for key, info in db.execute('SELECT id, info FROM samples WHERE state="tested" AND deleted IS NULL'):
        row = json.loads(info)
        if 'match' in row and row['match'] not in verified:
            continue
        summary = ROOT / 'results' / f'{key}.json'
        frames = ROOT / 'results' / f'{key}.jsonl.gz'
        if summary.is_file() and frames.is_file():
            (MEDIA / row['file']).unlink(missing_ok=True)
            db.execute('UPDATE samples SET deleted=? WHERE id=?', (now(), key))
    db.commit()


def run(db, pool, reader, version):
    active = {}
    cpu_count = capacity()
    memory_max = int((CGROUP / 'memory.max').read_text())
    target = 2
    previous_cpu = stats_file('cpu.stat')['usage_usec']
    previous_clock = time.monotonic()
    cpu_load = 0.0
    blocked_disk = 0
    while True:
        import_sources(db)
        for key, (future, stage, info) in list(active.items()):
            if not future.done():
                continue
            del active[key]
            try:
                result = future.result()
            except Exception as error:
                retries = db.execute('SELECT retries FROM samples WHERE id=?', (key,)).fetchone()[0] + 1
                state = {'testing': 'ready', 'downloading': 'queued'}[stage] if retries < 3 else 'failed'
                # Exception strings can contain signed media URLs. Keep their type and exit status.
                message = f'{stage}: {type(error).__name__}'
                if isinstance(error, subprocess.CalledProcessError):
                    message += f' (exit {error.returncode})'
                if isinstance(error, ValueError):
                    message += f' ({error})'
                db.execute('UPDATE samples SET state=?, retries=?, error=? WHERE id=?', (state, retries, message, key))
                print(now(), key, state, message, flush=True)
            else:
                if stage == 'testing':
                    db.execute('UPDATE samples SET state="tested", result=?, error=NULL WHERE id=?', (json.dumps(result), key))
                    print(now(), key, 'tested', result['samples'], result['dropped'], result['p95Ms'], flush=True)
                else:
                    db.execute('UPDATE samples SET state="ready", info=?, error=NULL, retries=0 WHERE id=?',
                               (json.dumps(info | result), key))
                    print(now(), key, 'downloaded', result['bytes'], flush=True)
        db.commit()
        remove_finished(db)
        report_sources(db)

        memory = int((CGROUP / 'memory.current').read_text())
        working = max(0, memory - stats_file('memory.stat')['inactive_file'])
        timestamp = time.monotonic()
        current_cpu = stats_file('cpu.stat')['usage_usec']
        if timestamp - previous_clock >= 20:
            cpu_load = (current_cpu - previous_cpu) / 1e6 / (timestamp - previous_clock) / cpu_count
            active_tests = sum(stage == 'testing' for _, stage, _ in active.values())
            if active_tests >= target and cpu_load < .9 and working < .9 * memory_max:
                target += 1
            elif cpu_load >= .98 or working >= .95 * memory_max:
                target = max(1, target - 1)
            previous_clock, previous_cpu = timestamp, current_cpu
        tests = sum(stage == 'testing' for _, stage, _ in active.values())
        downloads = sum(stage == 'downloading' for _, stage, _ in active.values())
        if working < memory_max * .95:
            for key, payload in db.execute('SELECT id,info FROM samples WHERE state="ready" ORDER BY json_extract(info, "$.match") IS NULL, json_extract(info, "$.match"), start'):
                if tests >= target:
                    break
                row = json.loads(payload)
                if (MEDIA / row['file']).is_file():
                    db.execute("UPDATE samples SET state='testing' WHERE id=?", (key,))
                    active[key] = (pool.submit(test, row, reader, version), 'testing', row)
                    tests += 1
                    print(now(), key, 'testing', row['file'], flush=True)

        reserved = 0
        for _, stage, row in active.values():
            if stage == 'downloading':
                partial = (MEDIA / row['file']).with_suffix('.staging.mp4')
                present = partial.stat().st_size if partial.is_file() else 0
                reserved += max(0, row['expectedBytes'] - present)
        disk = shutil.disk_usage(MEDIA)
        blocked_disk = 0
        for key, payload in db.execute('SELECT id,info FROM samples WHERE state="queued" ORDER BY json_extract(info, "$.rank"), start'):
            row = json.loads(payload)
            if disk.free - RESERVE_BYTES - reserved < row['expectedBytes']:
                blocked_disk += 1
                continue
            if working >= .95 * memory_max:
                break
            db.execute('UPDATE samples SET state="downloading" WHERE id=?', (key,))
            active[key] = (pool.submit(download, row, MEDIA, PROJECT), 'downloading', row)
            reserved += row['expectedBytes']
            downloads += 1
            print(now(), key, 'downloading', row['file'], flush=True)
        db.commit()
        counts = dict(db.execute('SELECT state,count(*) FROM samples GROUP BY state'))
        atomic_json(ROOT / 'status.json', {'heartbeatUtc': now(), 'readerVersion': version, 'counts': counts,
            'activeTests': tests, 'activeDownloads': downloads, 'nextTestTarget': target, 'cpuQuotaVcpu': cpu_count,
            'cpuShareUsed': round(cpu_load, 3), 'memoryBytes': memory, 'memoryWorkingBytes': working,
            'memoryMaxBytes': memory_max, 'memoryEvents': stats_file('memory.events'), 'diskTotalBytes': disk.total,
            'diskFreeBytes': disk.free, 'diskReserveBytes': RESERVE_BYTES, 'diskPendingBytes': reserved,
            'downloadsWaitingForDisk': blocked_disk, 'samples': [{'id': key, 'state': stage,
            'file': row['file']} for key, (_, stage, row) in active.items()]})
        time.sleep(5)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    with (ROOT / 'lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        (ROOT / 'results').mkdir(exist_ok=True)
        reader, version = snapshot()
        with sqlite3.connect(ROOT / 'campaign.sqlite3') as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('CREATE TABLE IF NOT EXISTS samples (id TEXT PRIMARY KEY,vod TEXT,start REAL,end REAL,state TEXT,info TEXT,retries INT,result TEXT,deleted TEXT,error TEXT)')
            resume(db)
            with ThreadPoolExecutor(max_workers=48) as pool:
                run(db, pool, reader, version)


if __name__ == '__main__':
    main()
