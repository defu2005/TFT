# Planning-frame OCR for gold, streak, level and XP (blind sample of ten).
# Reads the frame recorded in each round's planning entry, crops fixed boxes,
# and compares against the master only after OCR. Crops:
#   gold (610,586,640,610), streak (678,586,706,610), level (188,588,206,606), xp (244,588,274,606)
# Sample rounds are fixed below; the crop calibration frame is 2-3 at 604 s (not in the sample).
import json, subprocess, re, os
from PIL import Image
V = '/home/user/campaign/01-boxbox-2924500482-00210.mp4'
MASTER = 'data/hud-audit/match01_full.json'
WORK = os.environ.get('BLIND_WORK', '/tmp/blind_work')
SAMPLE = ['3-5', '3-6', '4-1', '4-2', '4-6', '5-1', '5-2', '5-5', '5-6', '6-2']
CROPS = {'gold': ((610, 586, 640, 610), '0123456789'),
         'streak': ((678, 586, 706, 610), '0123456789'),
         'level': ((188, 588, 206, 606), '0123456789'),
         'xp': ((244, 588, 274, 606), '0123456789/')}
os.makedirs(WORK, exist_ok=True)

def ocr(img, wl):
    p = os.path.join(WORK, '_crop.png'); img.save(p)
    cmd = f"OMP_THREAD_LIMIT=1 tesseract {p} - --psm 7 -c tessedit_char_whitelist='{wl}' 2>/dev/null"
    return subprocess.run(['bash', '-c', cmd], capture_output=True, text=True).stdout.strip()

def read_frame(path):
    im = Image.open(path).convert('RGB')
    out = {}
    for name, (box, wl) in CROPS.items():
        c = im.crop(box); c = c.resize((c.width * 6, c.height * 6), Image.LANCZOS)
        out[name] = ocr(c, wl)
    return out

def master_value(r, key):
    v = r['planning']['value'].get(key)
    return v.get('value') if isinstance(v, dict) else v

d = json.load(open(MASTER))
R = {r['round']: r for r in d['rounds']}
results = {}
for rd in SAMPLE:
    ft = R[rd]['planning']['value'].get('frame_s') or R[rd]['planning'].get('frame_s')
    f = os.path.join(WORK, f'{rd}_{ft}.png')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(ft), '-i', V, '-frames:v', '1', f], check=True)
    raw = read_frame(f)
    results[rd] = {'frame_s': ft, 'raw': raw,
                   'master': {'gold': master_value(R[rd], 'gold'), 'streak': master_value(R[rd], 'streak'),
                              'level': master_value(R[rd], 'level'), 'xp': master_value(R[rd], 'xp')}}
print(json.dumps({rd: {'frame_s': v['frame_s'], 'raw': v['raw'], 'master': v['master']} for rd, v in results.items()}, indent=1))
