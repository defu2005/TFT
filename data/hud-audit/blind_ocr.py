import json, subprocess, re
from PIL import Image
V='/home/user/campaign/01-boxbox-2924500482-00210.mp4'
S='/tmp/claude-0/-home-user-TFT/91722103-108d-57a1-a27d-f308a4301820/scratchpad/blind'
pick=json.load(open('/tmp/claude-0/-home-user-TFT/91722103-108d-57a1-a27d-f308a4301820/scratchpad/blind_pick.json'))
CROPS={'gold':(610,586,640,610),'streak':(678,586,706,610)}
def ocr(img, digits=True):
    p=f'{S}/_c.png'; img.save(p)
    cmd=f"OMP_THREAD_LIMIT=1 tesseract {p} - --psm 7 " + ("-c tessedit_char_whitelist=0123456789" if digits else "") + " 2>/dev/null"
    return subprocess.run(['bash','-c',cmd],capture_output=True,text=True).stdout.strip()
out={}
for rnd,ts in pick['frames'].items():
    t=ts[0]
    f=f'{S}/{rnd}_{t}.png'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(t),'-i',V,'-frames:v','1',f])
    im=Image.open(f).convert('RGB')
    rec={}
    for n,b in CROPS.items():
        c=im.crop(b); c=c.resize((c.width*3,c.height*3),Image.LANCZOS)
        raw=ocr(c)
        m=re.findall(r'\d+',raw)
        rec[n]={'raw':raw,'value':int(m[-1]) if m else None}
    out[rnd]={'frame_s':t,**rec}
json.dump(out,open(f'{S}/blind_reads.json','w'),indent=1)
print(json.dumps(out,indent=0)[:1500])
