# -*- coding: utf-8 -*-
"""
修复种子数据中的死链图片 URL。
背景：121 张商品图中 11 张 404。经 ProductPool 变体探测，10 张可修复，
仅「不素之霸双层牛堡三件套」无可用地址（该项无热量、不在配餐池，去掉图片字段走 emoji 兜底）。
"""
import io, os, re, json, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')

h = io.open(HTML, encoding='utf-8').read()
m = re.search(r'(const SEED = )(\{.*?\})(;\r?\nPromise\.resolve)', h, re.S)
assert m, '未找到 SEED 块'
data = json.loads(m.group(2))

# 原始 URL -> 修复后 URL
FIX = {
    # 日期路径 -> ProductPool 路径
    'https://menu-img.mcd.cn/pcm/prod/menu/20260824/product/MS_G504962_320.png':
        'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_G504962_320.png',
    'https://menu-img.mcd.cn/pcm/prod/menu/20260824/product/MS_9900016309_320.png':
        'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_9900016309_320.png',
    'https://menu-img.mcd.cn/pcm/prod/menu/20260824/product/MS_9900016310_320.png':
        'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_9900016310_320.png',
    'https://menu-img.mcd.cn/pcm/prod/menu/20260309/product/MS_9900003586_320.png':
        'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_9900003586_320.png',
    'https://menu-img.mcd.cn/pcm/prod/menu/20260824/product/MS_521952_320.png':
        'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_521952_320.png',
    # 源码数据 code 笔误：990001953 -> 正确 code 521953
    'https://menu-img.mcd.cn/pcm/prod/menu/20260824/product/MS_990001953_320.png':
        'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_521953_320.png',
    'https://menu-img.mcd.cn/pcm/prod/menu/20260309/product/MS_515280_320.png':
        'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_515280_320.png',
    'https://menu-img.mcd.cn/pcm/prod/menu/20260325/product/MS_1450_320.png':
        'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_1450_320.png',
    'https://menu-img.mcd.cn/pcm/prod/menu/20260101/product/MS_9900005432_320.png':
        'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_9900005432_320.png',
    # 去掉多余的 G 前缀
    'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_G9900008754_320.gif':
        'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_9900008754_320.gif',
}
# 无可用地址：去掉图片字段，让渲染层走 emoji 兜底
NO_IMAGE = {'不素之霸双层牛堡三件套'}

fixed, dropped = 0, 0
for k, v in data['menu'].items():
    if v.get('image') in FIX:
        v['image'] = FIX[v['image']]
        fixed += 1
    elif v['name'] in NO_IMAGE and v.get('image'):
        del v['image']
        dropped += 1
print('URL 修复: %d 项 | 去图字段: %d 项' % (fixed, dropped))
assert fixed == 10 and dropped == 1, '修复数量不符合预期'

# ---- 修复后逐个复验 ----
bad = []
for k, v in data['menu'].items():
    u = v.get('image')
    if not u:
        continue
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        urllib.request.urlopen(req, timeout=20)
    except Exception as e:
        bad.append((v['name'], str(e)[:30]))
print('复验失败: %d 项 %s' % (len(bad), bad))
assert not bad, '仍有死链'

# ---- 回写 ----
new_json = json.dumps(data, ensure_ascii=False)
h = h[:m.start()] + m.group(1) + new_json + m.group(3) + h[m.end():]
io.open(HTML, 'w', encoding='utf-8').write(h)
print('index.html 已更新：%d 字节' % len(h))
