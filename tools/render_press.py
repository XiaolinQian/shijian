"""Render editable, deterministic campaign layouts using real app assets.
Usage: python3 promo-site/tools/render_press.py
Requires Pillow. Fonts are resolved locally and are never distributed.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'press'
OUT.mkdir(exist_ok=True)
W, H = 1080, 1920
PAPER = '#f4f5ed'
INK = '#203b30'
GREEN = '#33735b'
MUTED = '#6d806c'
SAGE = '#dce7d4'
LIME = '#d8e3ae'
WHITE = '#fafbf5'
FONT = os.getenv('PROMO_FONT')
if not FONT:
    candidates = list(Path('/System/Library/AssetsV2').glob('com_apple_MobileAsset_Font*/*/AssetData/PingFang.ttc'))
    FONT = str(candidates[0]) if candidates else '/System/Library/Fonts/STHeiti Medium.ttc'
PING = 'PingFang' in FONT

def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=(11 if bold else 3) if PING else 1)

def txt(im, x, y, text, size, color=INK, bold=False, spacing=12):
    d = ImageDraw.Draw(im)
    d.multiline_text((x,y), text, font=font(size,bold), fill=color, spacing=spacing)

def rr(im, box, fill, radius=24, outline=None, width=1):
    ImageDraw.Draw(im).rounded_rectangle(box, radius, fill, outline, width)

def line(im, coords, fill, width=2):
    ImageDraw.Draw(im).line(coords, fill=fill, width=width)

def check(im,x,y,color=GREEN,scale=1):
    line(im,[(x,y+9*scale),(x+7*scale,y+16*scale),(x+23*scale,y)],color,max(2,int(4*scale)))

def base(bg=PAPER, dark=False, number='01'):
    im=Image.new('RGB',(W,H),bg)
    icon=Image.open(ROOT/'assets/app-icon-large.png').convert('RGBA').resize((62,62),Image.Resampling.LANCZOS)
    im.paste(icon,(86,120),icon)
    txt(im,166,116,'时笺',40,WHITE if dark else INK,True)
    txt(im,168,166,'SHIJIAN',16,LIME if dark else MUTED)
    txt(im,846,137,number,23,LIME if dark else MUTED)
    line(im,[(88,1680),(900,1680)],'#50654b' if dark else '#ccd7c3',2)
    txt(im,90,1704,'把每一天，过成自己的节奏。',23,'#bdcbb0' if dark else MUTED)
    return im

def pill(im, x, y, text, bg=SAGE, fg=GREEN, size=25):
    width=int(ImageDraw.Draw(im).textlength(text,font=font(size)))+40
    rr(im,(x,y,x+width,y+56),bg,28)
    txt(im,x+20,y+10,text,size,fg)
    return width

def shadow_card(im,box,radius=24):
    s=Image.new('RGBA',im.size)
    ImageDraw.Draw(s).rounded_rectangle((box[0]+4,box[1]+16,box[2]+4,box[3]+16),radius,fill=(18,43,27,28))
    s=s.filter(ImageFilter.GaussianBlur(22))
    im.paste(s,(0,0),s)
    rr(im,box,WHITE,radius)

def save(im,name):
    im.save(OUT/f'{name}.png',optimize=True)
    im.resize((360,640),Image.Resampling.LANCZOS).save(OUT/f'{name}.jpg',quality=92,optimize=True)

# 01 — product introduction, actual app screenshot
im=base(number='01')
txt(im,86,272,'把注意力，\n留给重要的事。',84,INK,True,20)
txt(im,90,528,'记录待办 · 每日提醒 · 自动复盘',30,MUTED)
x=90
for label in ['本地优先','离线可用','无需账户']:
    x+=pill(im,x,607,label)+14
# decorative rings behind product frame
D=ImageDraw.Draw(im)
for offset in [0,65,130]:
    D.ellipse((175-offset,790-offset,995+offset,1610+offset),outline='#e0e6d7',width=2)
shadow_card(im,(64,790,1016,1368))
rr(im,(64,790,1016,838),'#e5ebdf',20)
for x,c in [(88,'#be7964'),(108,'#d4b76d'),(128,'#89a87e')]:
    ImageDraw.Draw(im).ellipse((x,808,x+9,817),fill=c)
txt(im,642,799,'v0.1.0 历史界面 · 旧名日序',17,MUTED)
shot=Image.open(ROOT/'assets/app-preview.jpg').convert('RGB').resize((928,522),Image.Resampling.LANCZOS)
im.paste(shot,(76,834))
rr(im,(140,1410,900,1550),INK,20)
check(im,177,1452,LIME,1.3)
txt(im,233,1431,'今天，也要从容有序。',33,WHITE,True)
txt(im,233,1490,'时笺 · SHIJIAN 桌面待办工具',22,'#c1ceb8')
save(im,'01-cover')

# 02 — workflow diagram
im=base(INK,True,'02')
txt(im,88,270,'从一条待办，\n到一天的进展。',80,WHITE,True,18)
txt(im,90,515,'记录、提醒、复盘，一天刚好三步。',29,'#bdcbb0')
cards=[('01','记录','把脑海里的事，先放进清单。'),('02','提醒','重要的事，在合适的时间想起。'),('03','复盘','完成的记录，自动整理成报告。')]
for n,(num,title,desc) in enumerate(cards):
    y=665+n*295
    if n: line(im,[(138,y-50),(138,y)],'#6b855e',3)
    rr(im,(90,y,905,y+248),'#2c4737',24,'#536849',2)
    txt(im,126,y+29,num,23,LIME)
    txt(im,219,y+30,title,52,WHITE,True)
    txt(im,219,y+121,desc,27,'#c5d2bc')
    line(im,[(218,y+193),(856,y+193)],'#4d6647',2)
    if n==0:
        rr(im,(130,y+104,174,y+148),None,9,LIME,3)
        check(im,139,y+115,LIME,.9)
    elif n==1:
        ImageDraw.Draw(im).ellipse((129,y+101,177,y+149),outline=LIME,width=3)
        line(im,[(153,y+110),(153,y+126),(166,y+132)],LIME,3)
    else:
        rr(im,(130,y+100,174,y+154),None,6,LIME,3)
        for h in [115,125,135]: line(im,[(140,y+h),(164,y+h)],LIME,3)
txt(im,90,1590,'从容有序，不需要很复杂。',29,LIME)
save(im,'02-workflow')

# 03 — report types with editorial report card
im=base('#eeeede',False,'03')
txt(im,88,270,'别再从零，\n回想做过的事。',82,INK,True,18)
txt(im,90,515,'日报、周报、月报，从任务记录开始。',28,MUTED)
x=90
for label in ['日报','周报','月报']: x+=pill(im,x,594,label,'#dbe0c9',GREEN,29)+16
# paper stack
rr(im,(166,763,958,1451),'#c8d5bd',26)
rr(im,(127,737,919,1425),'#e2e8d7',26)
shadow_card(im,(90,711,882,1399))
txt(im,132,754,'我的工作报告',43,INK,True)
txt(im,134,827,'从记录中，看见自己的进展。',24,MUTED)
line(im,[(134,900),(833,900)],'#dfe5d6',2)
for y,label,body in [(939,'完成事项','已经推进的每一小步'),(1075,'进展与阻塞','值得记录的变化与思考'),(1211,'下期计划','为下一步留一个清晰方向')]:
    rr(im,(135,y+9,145,y+52),GREEN,5)
    txt(im,174,y,label,30,INK,True)
    txt(im,174,y+56,body,23,MUTED)
txt(im,92,1478,'本地汇总  /  人工补充  /  Markdown 导出',24,GREEN)
txt(im,92,1540,'内容随你的记录生成，不用从空白开始。',26,MUTED)
save(im,'03-reports')

# 04 — closing frame and download CTA
im=base('#e4ecdc',False,'04')
txt(im,88,270,'从第一件\n小事开始。',91,INK,True,20)
txt(im,90,545,'时笺，陪你一步一步来。',32,MUTED)
icon=Image.open(ROOT/'assets/app-icon-large.png').convert('RGBA').resize((244,244),Image.Resampling.LANCZOS)
shadow_card(im,(352,735,644,1027),54)
im.paste(icon,(376,759),icon)
txt(im,357,1100,'时笺 · SHIJIAN',43,INK,True)
txt(im,246,1190,'桌面待办 / 每日提醒 / 自动报告',28,MUTED)
rr(im,(140,1340,900,1456),GREEN,18)
txt(im,255,1370,'下载 macOS 体验版',39,WHITE,True)
txt(im,143,1493,'旧名日序 v0.1.0 · Intel x64 · macOS 13+',25,GREEN)
txt(im,143,1540,'体验包未签名、公证 · Windows 版待发布',22,MUTED)
save(im,'04-download')

# Social preview banner, 1200 × 630, generated from the same visual system.
im=Image.new('RGB',(1200,630),PAPER)
icon=Image.open(ROOT/'assets/app-icon-large.png').convert('RGBA').resize((70,70),Image.Resampling.LANCZOS)
im.paste(icon,(70,66),icon)
txt(im,161,76,'时笺 · SHIJIAN',33,INK,True)
txt(im,70,213,'今天，也要\n从容有序。',72,INK,True,7)
txt(im,73,480,'记录待办 · 每日提醒 · 自动复盘',25,MUTED)
rr(im,(785,110,1125,520),SAGE,35)
for y,label in [(163,'记录'),(277,'提醒'),(391,'复盘')]:
    rr(im,(823,y,1086,y+70),WHITE,14)
    check(im,850,y+25,GREEN,1)
    txt(im,910,y+11,label,33,INK)
im.save(ROOT/'assets/share-cover.jpg',quality=92,optimize=True)
print('Rendered four 1080×1920 PNG posters, JPG thumbnails, and social cover.')
