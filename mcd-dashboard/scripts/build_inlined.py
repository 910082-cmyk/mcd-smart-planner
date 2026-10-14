# -*- coding: utf-8 -*-
"""
把 index.html 改造成「零本地依赖」的自包含页面：
  1) 麦当劳 logo（方案1 纯金 M）内联为 SVG，不再用 <img src="assets/...">
  2) 种子数据 seed-data.json 内联为 JS 常量，不再 fetch 相对路径
  3) 修掉「金底放金 M」导致图标不可见的配色错误
每次运行都会先检查目标串是否存在，避免重复执行破坏文件。
"""
import io, re, json, sys
from urllib.parse import quote

D_PATH = re.search(r'd="([^"]+)"',
    io.open('assets/mcd-logo.svg', encoding='utf-8').read()).group(1)

def gold_m(size, extra=''):
    return ('<svg viewBox="0 0 24 24" width="%d" height="%d" '
            'xmlns="http://www.w3.org/2000/svg" %s>'
            '<path d="%s" fill="#FFC72C"/></svg>') % (size, size, extra, D_PATH)

def white_m(size):
    return ('<svg viewBox="0 0 24 24" width="%d" height="%d" '
            'xmlns="http://www.w3.org/2000/svg">'
            '<path d="%s" fill="#FFFFFF"/></svg>') % (size, size, D_PATH)

def plate_m(size, mfill='#FFC72C'):
    """红圆角方底 + M（用于 favicon：透明金 M 在浏览器标签白底上不可见）"""
    return ('<svg viewBox="0 0 24 24" width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">'
            '<rect width="24" height="24" rx="5.5" fill="#DA291C"/>'
            '<path d="%s" fill="%s" transform="translate(12,12) scale(0.82) translate(-12,-12)"/>'
            '</svg>') % (size, size, D_PATH, mfill)

h = io.open('index.html', encoding='utf-8').read()
orig_len = len(h)
done, skip = [], []

def rep(name, old, new, required=True):
    global h
    if old in h:
        h = h.replace(old, new)
        done.append(name)
    elif required:
        skip.append(name)

# ---------- 1. favicon 内联 ----------
rep('favicon 内联',
    '<link rel="icon" type="image/svg+xml" href="assets/mcd-logo.svg">',
    '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%s">' % quote(plate_m(32)))

# ---------- 2. hero 降级标志（红底 → 金 M） ----------
rep('hero 降级标志',
    '<div class="hero-fb" id="heroFb" style="display:none"><img src="assets/mcd-logo.svg" alt="麦当劳金色双拱门"></div>',
    '<div class="hero-fb" id="heroFb" style="display:none">%s</div>' % gold_m(150))

# ---------- 3. 顶栏品牌标志 ----------
rep('顶栏品牌标志',
    '<img src="assets/mcd-logo.svg" alt="麦当劳双拱门标志">',
    gold_m(44))

# ---------- 4. 功能卡图标 ----------
rep('功能卡图标（已启用）',
    '<div class="fi"><img src="assets/mcd-logo.svg" alt=""></div>',
    '<div class="fi">%s</div>' % gold_m(26), required=False)
rep('功能卡图标（预留）',
    '<div class="fic"><img src="assets/mcd-logo.svg" alt=""></div>',
    '<div class="fic">%s</div>' % white_m(26), required=False)

# ---------- 5. 修掉「金底放金 M」不可见 ----------
rep('.fi 底板金→红',
    '.fi{width:42px;height:42px;border-radius:12px;background:var(--mc-yellow);',
    '.fi{width:42px;height:42px;border-radius:12px;background:var(--mc-red);')
rep('.fic 去掉反色滤镜',
    '.fic img{width:26px;height:26px;filter:brightness(0) invert(1)}',
    '.fic svg{width:26px;height:26px;display:block}')
rep('.fi 内联 svg 尺寸',
    '.fi img{width:26px;height:26px}',
    '.fi img{width:26px;height:26px}.fi svg{width:26px;height:26px;display:block}',
    required=False)

# ---------- 6. 种子数据内联 ----------
seed = json.load(io.open('data/seed-data.json', encoding='utf-8'))
seed_js = json.dumps(seed, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

old_fetch = """fetch('data/seed-data.json').then(r=>r.json()).then(d=>{
  D=d;
  Object.entries(d.menu).forEach(([k,v])=>cache[k]=v);
  init();
  initMenu3D();          // 3D 舞台（失败自动降级，不影响上面已渲染的面板）
}).catch(e=>{
  document.getElementById('list').innerHTML=
    '<div class="empty"><div class="emptyi">⚠</div>数据加载失败<br>请确认 data/seed-data.json 存在</div>';
});"""

new_fetch = """/* 种子数据已内联为常量：不再依赖相对路径，预览链接 / 微信 / GitHub Pages 均可直接打开 */
const SEED = %s;
Promise.resolve(SEED).then(d=>{
  D=d;
  Object.entries(d.menu).forEach(([k,v])=>cache[k]=v);
  init();
  initMenu3D();          // 3D 舞台（失败自动降级，不影响上面已渲染的面板）
}).catch(e=>{
  console.error(e);
  document.getElementById('list').innerHTML=
    '<div class="empty"><div class="emptyi">⚠</div>数据初始化失败</div>';
});""" % seed_js

rep('种子数据内联', old_fetch, new_fetch)

io.open('index.html', 'w', encoding='utf-8').write(h)

print('完成 %d 项，跳过 %d 项' % (len(done), len(skip)))
for d in done: print('  [OK]  ' + d)
for s in skip: print('  [跳过] ' + s)
print('文件 %.1f KB → %.1f KB' % (orig_len/1024, len(h.encode('utf-8'))/1024))
