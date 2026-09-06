from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/images'
REG = 'C:/Windows/Fonts/msjh.ttc'
BOLD = 'C:/Windows/Fonts/msjhbd.ttc'
SCALE = 2


def render(slug, number, label, command, headline, subhead, quote, accent):
    raw = (ROOT / f'examples/csv-import/{slug}.md').read_text(encoding='utf-8')
    assert quote in raw, f'Quote must be verbatim: {slug}'
    im = Image.new('RGB', (1440*SCALE, 720*SCALE), '#101820')
    d = ImageDraw.Draw(im)
    def box(x, y, w, h, fill, radius=18, outline=None):
        d.rounded_rectangle(tuple(int(v*SCALE) for v in (x,y,x+w,y+h)), radius=radius*SCALE, fill=fill, outline=outline, width=2*SCALE)
    def txt(x,y,text,size=26,fill='#eef3ef',bold=False):
        f = ImageFont.truetype(BOLD if bold else REG, size*SCALE)
        assert x*SCALE+d.textlength(text,font=f) <= 1400*SCALE, text
        d.text((x*SCALE,y*SCALE),text,font=f,fill=fill)
    def line(x,y,x2,y2,color='#53626b',width=2):
        d.line((x*SCALE,y*SCALE,x2*SCALE,y2*SCALE),fill=color,width=width*SCALE)
    def arrow(x,y,x2,y2,color):
        line(x,y,x2,y2,color,3)
        line(x2-10,y2-7,x2,y2,color,3)
        line(x2-10,y2+7,x2,y2,color,3)
    box(40,40,58,42,accent,10)
    txt(53,44,number,24,'#101820',True)
    txt(115,44,label,26,bold=True)
    txt(700,48,command,22,accent)
    line(48,106,1392,106,'#334049')
    txt(56,145,'這次回答的重點',22,'#9caaaF')
    for i,t in enumerate(headline): txt(52,186+i* seventy,t,58,bold=True)
    txt(56,359,subhead,25,'#abb8bf')
    box(56,422,586,160,'#1e2a33',16)
    txt(78,440,'原文摘錄',19,accent,True)
    # Deliberate short excerpt; wrap by measured width.
    f = ImageFont.truetype(REG,27*SCALE)
    lines=[]; current=''
    for c in quote:
        if d.textlength(current+c,font=f)>535*SCALE:
            lines.append(current); current=''
        current+=c
    lines.append(current)
    assert len(lines)<=3
    for i,t in enumerate(lines): txt(78,477+i*35,t,27)
    box(698,145,686,437,'#18252d',24)
    if slug == 'baseline':
        txt(730,168,'回答順序',21,accent,True)
        items=[('01','重試會覆蓋修正嗎？'),('02','寫入與完成狀態一致嗎？'),('03','定義順序，再縮小方案')]
        for i,(n,t) in enumerate(items):
            y=221+i*104
            box(731,y,618,80,'#26353e',12)
            txt(752,y+20,n,28,accent,True)
            txt(820,y+20,t,30,bold=True)
            if i<2: line(771,y+80,771,y+104,accent,3)
    elif slug == 'single':
        txt(730,168,'具體做法（若以受理順序為準）',21,accent,True)
        box(735,226,263,105,'#26353e',14)
        box(1080,226,263,105,'#26353e',14)
        txt(757,240,'工作',23,'#abb8bf')
        txt(757,273,'固定序號',32,accent,True)
        txt(1102,240,'客戶資料',23,'#abb8bf')
        txt(1102,273,'最後套用序號',29,bold=True)
        arrow(1008,279,1070,279,accent)
        line(1208,332,1208,361,accent,3)
        box(735,369,608,76,accent,12)
        txt(759,388,'更新前，先比較序號',32,'#101820',True)
        txt(750,478,'重試沿用序號，保護新舊順序',26)
        txt(750,521,'先簡化架構，再補必要保護',22,'#abb8bf')
    else:
        txt(730,168,'分開處理的兩個保護與驗證',21,accent,True)
        for i,(a,b) in enumerate([('01','整批交易 → 更新與完成一致'),('02','版本條件 → 拒絕舊工作覆寫'),('03','驗證失敗、重送與交錯')]):
            y=220+i*104
            box(732,y,615,80,'#26353e',12)
            txt(752,y+22,a,27,accent,True)
            txt(812,y+23,b,27,bold=True)
    line(48,619,1392,619,'#334049')
    txt(56,648,'共同發現',23,accent,True)
    txt(190,648,'三組皆指出：架構可簡化、舊工作可能覆寫修正',25)
    txt(1138,651,'單次實測 · 摘要',21,'#abb8bf')
    OUT.mkdir(parents=True, exist_ok=True)
    path=OUT/f'csv-import-{slug}.png'
    im.resize((1440,720),Image.Resampling.LANCZOS).save(path)
    print(path)


seventy=70
if __name__=='__main__':
    render('baseline','01','角色提示（無濾鏡）','只用「你是資深工程師」', ['先抓覆寫，','再查完成狀態。'],'先談兩個失敗風險，再建議縮小方案。','但交易本身不能阻止舊工作晚到覆寫。','#edc183')
    render('single','02','單一濾鏡','$simplicity · 不加角色提示', ['先問必要性，','再具體到序號。'],'先談簡化，再提出有條件的版本方案。','減少層數或只加交易都不能解決此問題。','#8bdbc2')
    render('dual','03','雙濾鏡','$simplicity + $reliability · 不加角色提示', ['先談簡化，','再分開兩種保護。'],'釐清整批成功與新舊順序，各自如何保護。','交易本身不保證新舊順序。','#bca9f4')
