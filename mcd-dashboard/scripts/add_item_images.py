# -*- coding: utf-8 -*-
"""
配餐方案 / 购物车：纯文字表格 -> 图片+名字+数据 的列表行。
数据核验：配餐候选池 39 项 100% 带商品图，购物车条目同样带图。
"""
import io, os

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

# ============================================================ 1. CSS：带图列表
rep('''/* 聚焦面板 */''',
'''/* ================= 带图列表（配餐方案 / 购物车） ================= */
.ilist{display:flex;flex-direction:column;border:1.5px solid var(--line);border-radius:13px;
  overflow:hidden;margin-top:13px;background:#fff}
.ilist-hd{display:flex;align-items:center;gap:13px;padding:8px 14px;background:var(--bg);
  font-size:11px;font-weight:800;color:var(--ink2);border-bottom:1.5px solid var(--line);letter-spacing:.5px}
.ilist-hd .sp{flex:1}
.irow{display:flex;align-items:center;gap:13px;padding:9px 14px;background:#FFFDF9;transition:background .3s}
.irow+.irow{border-top:1px solid #FAF4EA}
.irow:hover{background:#FFF9EC}
.iw{width:54px;height:54px;border-radius:10px;background:#F7F1E7;flex-shrink:0;border:1px solid var(--line);
  display:flex;align-items:center;justify-content:center;font-size:22px;overflow:hidden}
.iw img{width:100%;height:100%;object-fit:cover;display:block}
.inm{flex:1;min-width:0;font-size:13.5px;font-weight:700;line-height:1.35}
.ikl{font-size:13px;font-weight:800;color:var(--mc-red);white-space:nowrap;min-width:76px;text-align:right}
.ipr{font-size:13.5px;font-weight:800;white-space:nowrap;min-width:56px;text-align:right}
.iq{width:62px;padding:7px 6px;font-size:13px;text-align:center;border:2px solid var(--line);
  border-radius:9px;background:#fff;font-family:inherit;transition:.3s}
.iq:focus{outline:none;border-color:var(--mc-yellow)}
@media (max-width:560px){
  .iw{width:44px;height:44px;font-size:18px}
  .irow,.ilist-hd{gap:10px;padding:8px 11px}
  .ikl{min-width:62px;font-size:12px}
  .ipr{min-width:48px;font-size:12.5px}
  .iq{width:52px}
}

/* 聚焦面板 */''', '带图列表 CSS')

# ============================================================ 2. planKcal：表格 -> 带图列表
rep('''      <table><thead><tr><th>餐品</th><th>热量</th><th>单价</th></tr></thead><tbody>
      ${p.set.map(x=>`<tr><td>${x.name}</td><td style="color:var(--mc-red);font-weight:700">${x.kcal} kcal</td><td>¥${x.currentPrice.toFixed(1)}</td></tr>`).join('')}
      </tbody></table>''',
'''      <div class="ilist">
        <div class="ilist-hd"><span style="width:54px">图片</span><span class="sp">餐品</span>
          <span class="ikl">热量</span><span class="ipr">单价</span></div>
        ${p.set.map(x=>`<div class="irow">
          <div class="iw">🍔<img src="${x.image||''}" alt="${x.name}" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()"></div>
          <div class="inm">${x.name}</div>
          <div class="ikl">${x.kcal} kcal</div>
          <div class="ipr">¥${x.currentPrice.toFixed(1)}</div>
        </div>`).join('')}
      </div>''', '配餐方案带图')

# ============================================================ 3. renderCart：表格 -> 带图列表
rep('''  document.getElementById('cartList').innerHTML=ks.length?
    `<div class="tw"><table><thead><tr><th>餐品</th><th>单价</th><th>数量</th><th>小计</th><th></th></tr></thead><tbody>`+
    ks.map(k=>{const m=D.menu[k],q=CART[k];return `<tr><td><b>${m.name}</b>${m.discountType?`<br><span class="fg gold">${m.discountType}</span>`:''}</td>
      <td>¥${m.currentPrice.toFixed(1)}</td>
      <td><input type="number" value="${q}" min="1" style="width:66px;padding:7px 9px;font-size:13px" onchange="CART['${k}']=+this.value;renderCart()"></td>
      <td><b>¥${(m.currentPrice*q).toFixed(1)}</b></td>
      <td><button class="chip" onclick="delete CART['${k}'];renderCart()">删</button></td></tr>`}).join('')+
    `</tbody></table></div>`:'<div class="empty" style="padding:26px"><div class="emptyi">🛒</div>购物车为空<br>去「菜单看板」加入餐品</div>';''',
'''  document.getElementById('cartList').innerHTML=ks.length?
    `<div class="ilist">
      <div class="ilist-hd"><span style="width:54px">图片</span><span class="sp">餐品</span>
        <span class="ipr">单价</span><span style="width:62px;text-align:center">数量</span>
        <span class="ipr">小计</span><span style="width:44px"></span></div>`+
    ks.map(k=>{const m=D.menu[k],q=CART[k];return `<div class="irow">
      <div class="iw">🍔<img src="${m.image||''}" alt="${m.name}" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()"></div>
      <div class="inm">${m.name}${m.discountType?`<br><span class="fg gold">${m.discountType}</span>`:''}</div>
      <div class="ipr">¥${m.currentPrice.toFixed(1)}</div>
      <input class="iq" type="number" value="${q}" min="1" onchange="CART['${k}']=+this.value;renderCart()">
      <div class="ipr" style="color:var(--mc-red)">¥${(m.currentPrice*q).toFixed(1)}</div>
      <button class="chip" style="min-width:44px;padding:6px 10px;font-size:12px" onclick="delete CART['${k}'];renderCart()">删</button>
    </div>`}).join('')+
    `</div>`:'<div class="empty" style="padding:26px"><div class="emptyi">🛒</div>购物车为空<br>去「菜单看板」加入餐品</div>';''', '购物车带图')

io.open(HTML, 'w', encoding='utf-8').write(h)
print('\n完成：%d -> %d 字节 (+%d)' % (n0, len(h), len(h) - n0))
