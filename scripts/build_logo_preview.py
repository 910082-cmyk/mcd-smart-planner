# -*- coding: utf-8 -*-
"""生成 100% 自包含的 logo 预览页：SVG 全部内联，零外部文件引用。"""
import io, re, base64, os

D = re.search(r'd="([^"]+)"',
    io.open('assets/mcd-logo.svg', encoding='utf-8').read()).group(1)

png_b64 = base64.b64encode(open(os.path.join(
    os.environ.get('TEMP', '/tmp'), '_logo_nonzero.png'), 'rb').read()).decode()

def gold_m(size, extra=''):
    return ('<svg viewBox="0 0 24 24" width="__s__" height="__s__" '
            'xmlns="http://www.w3.org/2000/svg" __e__>'
            '<path d="__d__" fill="#FFC72C"/></svg>').format(s=size, d=D, e=extra)

def tile_m(size, mfill):
    return ('<svg viewBox="0 0 24 24" width="__s__" height="__s__" '
            'xmlns="http://www.w3.org/2000/svg">'
            '<rect width="24" height="24" rx="5.5" fill="#DA291C"/>'
            '<path d="__d__" fill="__f__" transform="translate(12,12) scale(0.82) translate(-12,-12)"/>'
            '</svg>').format(s=size, d=D, f=mfill)

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>麦当劳 Logo 候选 · 请确认</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
  background:#FFFAF3;color:#2E1B0D;line-height:1.6;padding:28px 20px 60px}
.wrap{max-width:900px;margin:0 auto}
h1{font-size:21px;font-weight:800;margin-bottom:6px}
.sub{font-size:13px;color:#A08D7A;margin-bottom:24px}
.sec{font-size:14px;font-weight:800;margin:26px 0 12px;padding-left:11px;border-left:4px solid #FFC72C}
.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.c{background:#fff;border:1.5px solid #F5E9D8;border-radius:14px;padding:20px;text-align:center}
.cn{font-size:13.5px;font-weight:800;margin:12px 0 4px}
.cd{font-size:11.5px;color:#A08D7A;line-height:1.5}
.big{width:120px;height:120px;margin:0 auto;display:flex;align-items:center;justify-content:center}
.big svg{width:100%;height:100%;display:block}
.onred{background:#DA291C;border-radius:14px;padding:20px;margin-bottom:12px;text-align:center}
.onred .lbl{color:#FFD98A;font-size:11.5px;margin-top:10px}
.sizes{display:flex;gap:22px;align-items:flex-end;justify-content:center;flex-wrap:wrap}
.sz{text-align:center}
.sz span{font-size:10.5px;color:#A08D7A;margin-top:5px;display:block}
.note{background:#FFF4E3;border-left:4px solid #B25A00;color:#7A3E00;padding:13px 16px;
  border-radius:10px;font-size:12.5px;line-height:1.8;margin:18px 0}
.ok{background:#E3F6EC;border-left:4px solid #0B7A4B;color:#0A5537;padding:13px 16px;
  border-radius:10px;font-size:12.5px;line-height:1.8;margin:18px 0}
.proof{background:#fff;border:1.5px dashed #C9B8A3;border-radius:14px;padding:18px;text-align:center}
.proof img{width:220px;height:220px;image-rendering:auto;border-radius:8px}
.cap{font-size:11.5px;color:#A08D7A;margin-top:8px}
.pick{display:flex;gap:10px;justify-content:center;margin-top:14px;flex-wrap:wrap}
.pick a{display:inline-block;background:#DA291C;color:#fff;font-weight:800;font-size:13px;
  padding:9px 22px;border-radius:999px;text-decoration:none}
.pick a.g{background:#2E7D32}
</style>
</head>
<body>
<div class="wrap">
<h1>麦当劳 Logo 候选方案</h1>
<p class="sub">本页零外部文件 —— SVG 全部内联，任何环境（含预览链接）都能正确显示</p>

<div class="ok">
<b>本次自查结论：</b>官方路径本身是对的 —— 我用独立光栅化器把这段路径真实渲染成了位图（见页面底部），
就是标准金色双拱门。你一直看到「错的」，是因为页面用 <code>&lt;img src=assets/…&gt;</code> 相对路径引用，
在预览环境里这些文件全部 404。本页已改为内联，所见即最终效果。
</div>

<div class="sec">三个候选（请选一个）</div>
<div class="row">
  <div class="c"><div class="big">__gold1__</div>
    <div class="cn">方案 1 · 纯金色 M</div>
    <div class="cd">官方几何路径 + 品牌金 #FFC72C<br>透明背景，红底白底都可用</div></div>
  <div class="c"><div class="big">__tile_gold__</div>
    <div class="cn">方案 2 · 红底金 M</div>
    <div class="cd">App 图标风格<br>红圆角方底 + 金色 M</div></div>
  <div class="c"><div class="big">__tile_white__</div>
    <div class="cn">方案 3 · 红底白 M</div>
    <div class="cd">反白风格<br>红底 + 白色 M，深色场景醒目</div></div>
</div>

<div class="sec">放在品牌红底上（对应主页顶栏 #DA291C）</div>
<div class="onred">__gold2__<div class="lbl">方案 1 · 纯金 M 置于品牌红底 —— 标准「红底金拱门」</div></div>
<div class="onred">__tile_gold2__<div class="lbl">方案 2 · 自带红底，与顶栏融为一体</div></div>

<div class="sec">多尺寸清晰度（矢量全程锐利）</div>
<div class="c"><div class="sizes">
  <div class="sz">__s64__<span>64px</span></div>
  <div class="sz">__s44__<span>44px</span></div>
  <div class="sz">__s28__<span>28px</span></div>
  <div class="sz">__s16__<span>16px</span></div>
</div></div>

<div class="sec">渲染证据（位图，非矢量）</div>
<div class="proof">
  <img src="data:image/png;base64,__png__" alt="光栅化渲染结果">
  <div class="cap">上面是我用独立光栅化器把这段 SVG 路径逐像素渲染出的位图 —— 与上方的矢量形状一致，即标准金色双拱门。</div>
</div>

<div class="pick">
  <a class="g" href="#pick1">我选方案 1</a>
  <a class="g" href="#pick2">我选方案 2</a>
  <a class="g" href="#pick3">我选方案 3</a>
</div>

<div class="note">
<b>回复 1 / 2 / 3 即可。</b>确认后我会把选定的 logo 以<b>内联方式</b>替换进主页（不再用相对路径 img），
并把种子数据一并内联修掉「加载失败」的问题。
</div>
</div>
</body>
</html>"""

for k,v in dict(
    gold1=gold_m(120), tile_gold=tile_m(120, '#FFC72C'), tile_white=tile_m(120, '#FFFFFF'),
    gold2=gold_m(100), tile_gold2=tile_m(100, '#FFC72C'),
    s64=gold_m(64), s44=gold_m(44), s28=gold_m(28), s16=gold_m(16),
    png=png_b64, d=D, s='100%', f='#FFC72C', e='').items():
    html = html.replace('__%s__' % k, v)

out = html
io.open('logo-preview.html', 'w', encoding='utf-8').write(out)
print('已生成 %.1f KB' % (len(out.encode('utf-8')) / 1024))
print('外部引用检查:', 'PASS（无）' if not re.search(r'(src|href)="(?!#|data:)[^"]+"', out) else '仍有外部引用!')
