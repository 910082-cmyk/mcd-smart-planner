# -*- coding: utf-8 -*-
"""
修复用户截图反馈的三个问题：
  1. 精选餐品面板：「官方菜单·精选餐品」徽章与餐品名/图片重叠 → 面板加顶部内边距
  2. 菜单网格卡片：无图商品（不素之霸）图片区空白 → 补回真实图片 + 加 emoji 兜底
  3. 饮品图片被裁：原图 427×320（4:3），方/扁容器 + object-fit 行为不可靠 →
     改用 aspect-ratio:4/3 让容器与图片同比例，contain 精确贴合；老浏览器回退 height:auto
  4. 附加：加 no-cache meta，避免用户浏览器拿旧版（解释此前 contain 改了却看不到）
"""
import io, os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
h = io.open(HTML, encoding='utf-8').read()
n0 = len(h)

def rep(old, new, tag, count=1):
    global h
    n = h.count(old)
    assert n == count, '[%s] 期望 %d 处，实际 %d 处' % (tag, count, n)
    h = h.replace(old, new)
    print('  OK ' + tag)

# ============================================================ 1. no-cache meta
rep('<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '''<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">''', 'no-cache meta')

# ============================================================ 2. 补回不素之霸的图片
m = re.search(r'(const SEED = )(\{.*?\})(;\r?\nPromise\.resolve)', h, re.S)
assert m, '未找到 SEED'
data = json.loads(m.group(2))
fixed = 0
for k, v in data['menu'].items():
    if v['name'] == '不素之霸双层牛堡三件套' and not v.get('image'):
        # 源码数据里的 G504961 是错的，正确图码是商品自身编码 9900005411
        v['image'] = 'https://menu-img.mcd.cn/pcm/prod/menu/ProductPool/product/MS_9900005411_320.png'
        fixed += 1
assert fixed == 1, '补图数量不符: %d' % fixed
new_json = json.dumps(data, ensure_ascii=False)
h = h[:m.start()] + m.group(1) + new_json + m.group(3) + h[m.end():]
print('  OK 不素之霸补图（正确图码 9900005411）')

# ============================================================ 3. 菜单网格卡：容器与图片同比例 + 无图兜底
rep(""".mimg{height:148px;background:#fff;position:relative;overflow:hidden}
.mimg img{width:100%;height:100%;object-fit:contain;transition:transform 1s cubic-bezier(.22,.61,.36,1)}
.mi:hover .mimg img{transform:scale(1.04)}""",
""".mimg{aspect-ratio:4/3;height:auto;min-height:132px;background:#fff;position:relative;overflow:hidden}
.mimg img{width:100%;height:100%;object-fit:contain;display:block;
  transition:transform 1s cubic-bezier(.22,.61,.36,1)}
.mimg-fb{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  font-size:46px;background:#fff}
.mi:hover .mimg img{transform:scale(1.04)}""", 'mimg 同比例容器 + 兜底样式')

rep('  .mimg{height:116px}.focus{padding:16px}', '  .mimg{min-height:104px}.focus{padding:44px 16px 16px}', '移动端 mimg + 面板内边距')

# ============================================================ 4. 网格卡无图时显示 emoji 兜底
rep("""    return `<div class="mi"><div class="mimg">${i.image?`<img src="${i.image}" alt="${i.name}" loading="lazy" referrerpolicy="no-referrer">`:''}""",
"""    return `<div class="mi"><div class="mimg">${i.image?`<img src="${i.image}" alt="${i.name}" loading="lazy" referrerpolicy="no-referrer">`:`<div class="mimg-fb">🍔</div>`}""",
    '网格卡无图 emoji 兜底')

# ============================================================ 5. 精选面板：避开左上角徽章
rep('.focus{display:flex;gap:26px;padding:26px 28px;background:transparent;align-items:center;flex-wrap:wrap}',
    '.focus{display:flex;gap:26px;padding:46px 28px 26px;background:transparent;align-items:center;flex-wrap:wrap}',
    '聚焦面板顶部内边距避让徽章')

io.open(HTML, 'w', encoding='utf-8').write(h)
print('\n完成：%d -> %d 字节 (+%d)' % (n0, len(h), len(h) - n0))
