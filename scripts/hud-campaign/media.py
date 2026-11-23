"""Fetch an intact Twitch HLS interval and confirm its video duration."""
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import urljoin


def download(source, directory, project):
    cached = Path('/tmp/tft-20-matches') / (source['vod'] + '.json')
    if cached.is_file() and cached.stat().st_size:
        info = json.loads(cached.read_text())
    else:
        env = {**os.environ, 'PYTHONPATH': str(project / '.cache/tft-video-tools')}
        info = json.loads(subprocess.check_output([
            'python3', '-m', 'yt_dlp', '--compat-options', 'no-certifi', '--skip-download',
            '--dump-single-json', source['source'],
        ], env=env, timeout=100))
    fmt = next(f for f in info['formats'] if f.get('height') == source['requestedHeight']
               and f.get('protocol') == 'm3u8_native')
    playlist = subprocess.check_output(['curl', '-fsSL', '--retry', '3', '--max-time', '35', fmt['url']], text=True)
    elapsed = 0.0
    segments = []
    for line in playlist.splitlines():
        if line.startswith('#EXTINF:'):
            length = float(line.split(':', 1)[1].split(',', 1)[0])
        elif line.strip() and not line.startswith('#'):
            if elapsed + length > source['intendedStartSec'] and elapsed < source['intendedEndSec']:
                segments.append((elapsed, elapsed + length, urljoin(fmt['url'], line.strip())))
            elapsed += length
    if not segments or segments[-1][1] < source['intendedEndSec'] - 2:
        raise ValueError('Source does not contain the expected interval')

    def get(url):
        return subprocess.check_output(['curl', '-fsSL', '--retry', '4', '--retry-all-errors',
                                        '--max-time', '65', url])

    file = directory / source['file']
    stage = file.with_suffix('.staging.mp4')
    urls = iter(seg[2] for seg in segments)
    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            with subprocess.Popen(['nice', '-n', '10', 'ffmpeg', '-nostdin', '-v', 'error', '-y',
                                   '-f', 'mpegts', '-i', 'pipe:0', '-map', '0:v:0', '-map', '0:a:0?',
                                   '-c', 'copy', '-movflags', '+faststart', str(stage)], stdin=subprocess.PIPE) as ffmpeg:
                while batch := list(islice(urls, 12)):
                    for data in pool.map(get, batch):
                        ffmpeg.stdin.write(data)
                ffmpeg.stdin.close()
                if ffmpeg.wait():
                    raise RuntimeError('Unable to write playable MP4')
        result = probe(stage)
        a, b = segments[0][0], segments[-1][1]
        if abs(result['duration'] - (b - a)) > 1.5:
            raise ValueError(f"Duration mismatch, source {b - a:.2f}s, file {result['duration']:.2f}s")
        stage.replace(file)
        return {**result, 'mediaStartSec': round(a, 3), 'mediaEndSec': round(b, 3), 'segments': len(segments)}
    except BaseException:
        stage.unlink(missing_ok=True)
        raise


def probe(path):
    result = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,codec_name,avg_frame_rate,nb_frames:format=duration',
        '-of', 'json', str(path)], timeout=45))
    return {**result['streams'][0], 'duration': float(result['format']['duration']), 'bytes': path.stat().st_size}
