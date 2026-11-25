import json, subprocess, re
from PIL import Image
import numpy as np
V='/home/user/campaign/01-boxbox-2924500482-00210.mp4'
S='/tmp/claude-0/-home-user-TFT/91722103-108d-57a1-a27d-f308a4301820/scratchpad/blind'
pick=json.load(open('/tmp/claude-0/-home-user-TFT/91722103-108d-57a1-a27d-f308a4301820/scratchpad/blind_pick.json'))
GOLD=(604,586,636,610)
def ocr(img):
    p=f'{S}/_m.png'; img.save(p)
    cmd=f"OMP_THREAD_LIMIT=1 tesseract {p} - --psm 7 -c tessedit_char_whitelist=0123456789 2>/dev/null"
    return subprocess.run(['bash','-c',cmd],capture_output=True,text=True).stdout.strip()
out={}
for rnd,ts in pick['frames'].items():
    t=ts[0]
    f=f'{S}/{rnd}_{t}.png'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(t),'-i',V,'-frames:v','1',f])
    im=Image.open(f).convert('RGB').crop(GOLD)
    a=np.asarray(im).astype(int)
    mask=(a.min(axis=2)>200)
    m=np.where(mask[...,None],255,0).astype('uint8').repeat(3,axis=2)
    c=Image.fromarray(m).resize((im.width*4,im.height*4),Image.NEAREST)
    raw=ocr(c)
    nums=re.findall(r'\d+',raw)
    out[rnd]={'frame_s':t,'raw':raw,'value':int(nums[-1]) if nums else None}
json.dump(out,open(f'{S}/blind_reads_masked.json','w'),indent=1)
print('rounds', len(out))
