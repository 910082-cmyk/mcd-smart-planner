# -*- coding: utf-8 -*-
"""品牌贴合度打磨（适配当前版本）：票券优惠券 / 全局结算条 / 导航图标化 / SVG 图标替换 / 深色主题 / 分段控件
注意：文件已有 toast 系统与 ARIA Tabs + hash 路由，全部保留，仅做增强不改架构。"""
import sys

P = "index.html"
s = open(P, encoding="utf-8").read()
edits = []

def E(old, new, count=1):
    edits.append((old, new, count))

# ---------- 新 token & 深色主题 ----------
E("""  --ink:#2E1B0D; --ink2:#6B5340; --ink3:#857260;
  --bg:#FFFAF3; --card:#fff; --line:#F5E9D8; --line2:#EEDFC8;""",
"""  --ink:#2E1B0D; --ink2:#6B5340; --ink3:#857260;
  --bg:#FFFAF3; --card:#fff; --card2:#FFFDF9; --card-h:#FFF6E4; --line:#F5E9D8; --line2:#EEDFC8;
  --gold-bg:#FFF6DD; --gold-bd:#F7E2A8; --gold-tx:#8A5B18; --code-bg:rgba(0,0,0,.05);
  --stage-grad:linear-gradient(170deg,#FFFCF5 0%,#FFF4DF 100%);""")

E("""  --r:18px; --sh:0 2px 4px rgba(58,32,16,.04),0 12px 30px rgba(58,32,16,.07);
}""",
"""  --r:18px; --sh:0 2px 4px rgba(58,32,16,.04),0 12px 30px rgba(58,32,16,.07);
}
[data-theme="dark"]{
  --ink:#F3E7D5; --ink2:#CBB79C; --ink3:#A59077;
  --bg:#17110B; --card:#221A12; --card2:#2A2117; --card-h:#332818; --line:#3D3122; --line2:#4C3D29;
  --gold-bg:#3A2C10; --gold-bd:#57421C; --gold-tx:#FFD98A; --code-bg:rgba(255,255,255,.09);
  --stage-grad:linear-gradient(170deg,#2B2114 0%,#211A10 100%);
  --ok:#4ED997; --ok-bg:#0F2B1E; --warn:#FFB35C; --warn-bg:#33230C; --err:#FF6B5E; --err-bg:#3A1712;
  --sh:0 2px 4px rgba(0,0,0,.32),0 12px 30px rgba(0,0,0,.5);
}""")

E(".hstl{font-size:11.5px;color:#FFE9D9;margin-top:4px}",
  ".hstl{font-size:11.5px;color:#FFE3B0;margin-top:4px}")

# ---------- 导航图标化（保留 ARIA Tabs 结构） + 全局结算条 + 主题钮 + 分段控件 + 票券 ----------
E("""/* ================= 导航 ================= */
nav{display:flex;gap:4px;background:#fff;border-radius:var(--r);padding:6px;box-shadow:var(--sh);
  margin:-16px 0 22px;position:relative;z-index:6;overflow-x:auto}
nav button{flex:1;min-width:max-content;background:none;border:0;padding:12px 13px;border-radius:13px;
  font-family:inherit;font-size:13.5px;color:var(--ink2);cursor:pointer;font-weight:600;transition:.32s;white-space:nowrap}
nav button:hover{background:var(--bg)}
nav button.on{background:var(--mc-red);color:#fff;box-shadow:0 4px 14px rgba(218,41,28,.32)}""",
"""/* ================= 导航（图标 + 标签） ================= */
nav{display:flex;gap:4px;background:var(--card);border-radius:var(--r);padding:6px;box-shadow:var(--sh);
  margin:-16px 0 22px;position:relative;z-index:6;overflow-x:auto}
nav button{flex:1;min-width:max-content;display:inline-flex;align-items:center;justify-content:center;gap:6px;
  background:none;border:0;padding:12px 13px;border-radius:13px;
  font-family:inherit;font-size:13.5px;color:var(--ink2);cursor:pointer;font-weight:600;transition:.32s;white-space:nowrap}
nav button svg{width:17px;height:17px;flex-shrink:0}
nav button:hover{background:var(--bg)}
nav button.on{background:var(--mc-red);color:#fff;box-shadow:0 4px 14px rgba(218,41,28,.32)}
nav button.on svg{stroke:#fff}

/* ================= 全局悬浮结算条 ================= */
#cartbar{position:fixed;left:50%;transform:translateX(-50%);bottom:22px;z-index:45;display:none;
  align-items:center;gap:14px;width:min(680px,calc(100% - 24px));background:var(--mc-yellow);
  border-radius:18px;padding:12px 14px 12px 18px;box-shadow:0 10px 30px rgba(255,199,44,.42)}
#cartbar.show{display:flex}
#cartbar.bump{animation:bump .45s cubic-bezier(.22,.61,.36,1)}
@keyframes bump{0%{transform:translateX(-50%) scale(1)}35%{transform:translateX(-50%) scale(1.05)}100%{transform:translateX(-50%) scale(1)}}
.cb-l{flex:1;min-width:0}
.cb-n{font-size:13px;font-weight:800;color:#4A3000}
.cb-s{font-size:11px;color:#8A5B18;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cb-v{font-size:21px;font-weight:800;color:#3A2010;line-height:1;white-space:nowrap}
#cartbar .btn{padding:11px 18px;font-size:13px;box-shadow:0 3px 10px rgba(218,41,28,.3)}

/* ================= 主题切换 ================= */
#themeBtn{position:fixed;right:16px;top:16px;z-index:70;width:42px;height:42px;border-radius:50%;
  border:1.5px solid var(--line);background:var(--card);color:var(--ink2);cursor:pointer;
  display:flex;align-items:center;justify-content:center;box-shadow:var(--sh);transition:.25s}
#themeBtn:hover{color:var(--mc-red);border-color:var(--mc-yellow)}
#themeBtn svg{width:20px;height:20px;display:block}

/* ================= 分段控件（取餐 / 出行方式） ================= */
.seg{display:flex;gap:6px;flex-wrap:wrap}
.seg button{display:inline-flex;align-items:center;gap:7px;background:var(--card2);border:1.5px solid var(--line);
  border-radius:12px;padding:11px 14px;font-family:inherit;font-size:13px;font-weight:700;color:var(--ink2);
  cursor:pointer;transition:.25s}
.seg button svg{width:18px;height:18px;display:block;flex-shrink:0}
.seg button:hover{border-color:var(--mc-yellow);background:var(--card)}
.seg button.on{background:var(--mc-yellow);border-color:var(--mc-yellow);color:#4A3000}
.seg button.on svg{stroke:#4A3000}

/* ================= 票券形优惠券 ================= */
.cp{position:relative;display:inline-flex;align-items:center;gap:8px;padding:9px 15px;font-size:12.5px;
  font-weight:700;color:var(--ink2);background:var(--card);border:1.5px solid var(--line);border-radius:7px}
.cp::before,.cp::after{content:"";position:absolute;top:50%;width:11px;height:11px;border-radius:50%;
  background:var(--card);border:1.5px solid var(--line);transform:translateY(-50%)}
.cp::before{left:-7px;clip-path:inset(0 0 0 45%)}
.cp::after{right:-7px;clip-path:inset(0 45% 0 0)}
.cp.a{background:var(--gold-bg);border-color:var(--gold-bd);color:var(--gold-tx)}
.cp.a::before,.cp.a::after{background:var(--gold-bg);border-color:var(--gold-bd)}""")

# ---------- 深色模式：硬编码白底改 token ----------
E("""  overflow:hidden;margin-top:13px;background:#fff}""",
  """  overflow:hidden;margin-top:13px;background:var(--card)}""")
E(""".iw{width:64px;height:48px;border-radius:10px;background:#fff;flex-shrink:0;border:1px solid var(--line);""",
  """.iw{width:64px;height:48px;border-radius:10px;background:var(--card);flex-shrink:0;border:1px solid var(--line);""")
E(""".irow{display:flex;align-items:center;gap:13px;padding:9px 14px;background:#FFFDF9;transition:background .3s}""",
  """.irow{display:flex;align-items:center;gap:13px;padding:9px 14px;background:var(--card2);transition:background .3s}""")
E(".irow:hover{background:#FFF9EC}", ".irow:hover{background:var(--card-h)}")
E(".irow+.irow{border-top:1px solid #FAF4EA}", ".irow+.irow{border-top:1px solid var(--line)}")
E(""".iw .ifb{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  font-size:20px;pointer-events:none;line-height:1}""",
""".iw .ifb{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  pointer-events:none;line-height:1}
.iw .ifb svg{width:22px;height:22px;display:block}""")
E(".stage{background:linear-gradient(170deg,#FFFCF5 0%,#FFF4DF 100%);border:1.5px solid var(--line);",
  ".stage{background:var(--stage-grad);border:1.5px solid var(--line);")
E(".strip{background:#fff;border:1.5px solid var(--line);border-radius:var(--r);padding:14px;margin-bottom:16px}",
  ".strip{background:var(--card);border:1.5px solid var(--line);border-radius:var(--r);padding:14px;margin-bottom:16px}")
E("""  background:#fff;transition:.4s cubic-bezier(.22,.61,.36,1);position:relative;padding:0;font-family:inherit}""",
  """  background:var(--card);transition:.4s cubic-bezier(.22,.61,.36,1);position:relative;padding:0;font-family:inherit}""")
E(".tile img{width:100%;height:66px;object-fit:contain;display:block;background:#fff}",
  ".tile img{width:100%;height:66px;object-fit:contain;display:block;background:var(--card)}")
E("""  border:2px solid var(--line);border-radius:13px;background:#FFFDF9;color:var(--ink);transition:.3s}""",
  """  border:2px solid var(--line);border-radius:13px;background:var(--card2);color:var(--ink);transition:.3s}""")
E("input[type=text]:focus,input[type=number]:focus,select:focus{outline:none;border-color:var(--mc-yellow);background:#fff;box-shadow:0 0 0 4px rgba(255,199,44,.16)}",
  "input[type=text]:focus,input[type=number]:focus,select:focus{outline:none;border-color:var(--mc-yellow);background:var(--card);box-shadow:0 0 0 4px rgba(255,199,44,.16)}")
E(""".chip{background:#FFFDF9;border:1.5px solid var(--line);border-radius:999px;padding:8px 15px;font-size:13px;""",
  """.chip{background:var(--card2);border:1.5px solid var(--line);border-radius:999px;padding:8px 15px;font-size:13px;""")
E(".chip:hover{border-color:var(--mc-yellow);background:#fff}", ".chip:hover{border-color:var(--mc-yellow);background:var(--card)}")
E(".mi{background:#fff;border:1.5px solid var(--line);border-radius:15px;overflow:hidden;transition:.5s cubic-bezier(.22,.61,.36,1);display:flex;flex-direction:column}",
  ".mi{background:var(--card);border:1.5px solid var(--line);border-radius:15px;overflow:hidden;transition:.5s cubic-bezier(.22,.61,.36,1);display:flex;flex-direction:column}")
E(".mimg{aspect-ratio:4/3;height:auto;min-height:132px;background:#fff;position:relative;overflow:hidden}",
  ".mimg{aspect-ratio:4/3;height:auto;min-height:132px;background:var(--card);position:relative;overflow:hidden}")
E(""".mimg-fb{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  font-size:46px;background:#fff}""",
""".mimg-fb{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  background:var(--card)}
.mimg-fb svg{width:62px;height:62px;display:block}""")
E(".focus-img{width:210px;height:210px;border-radius:18px;background:#fff;flex-shrink:0;overflow:hidden;",
  ".focus-img{width:210px;height:210px;border-radius:18px;background:var(--card);flex-shrink:0;overflow:hidden;")
E("""  border-radius:9px;background:#fff;font-family:inherit;transition:.3s}""",
  """  border-radius:9px;background:var(--card);font-family:inherit;transition:.3s}""")
E(".note code,code{background:rgba(0,0,0,.05);padding:1.5px 5px;border-radius:4px;font-size:11.5px;font-family:ui-monospace,Menlo,Consolas,monospace}",
  ".note code,code{background:var(--code-bg);padding:1.5px 5px;border-radius:4px;font-size:11.5px;font-family:ui-monospace,Menlo,Consolas,monospace}")
E(".feat{background:#fff;border:1.5px solid var(--line);border-radius:15px;padding:18px}",
  ".feat{background:var(--card);border:1.5px solid var(--line);border-radius:15px;padding:18px}")
E(".fo{background:#FBF6EE;border:1.5px solid var(--line);border-radius:11px;padding:14px;margin-bottom:11px}",
  ".fo{background:var(--card2);border:1.5px solid var(--line);border-radius:11px;padding:14px;margin-bottom:11px}")
E("td{padding:12px;border-bottom:1px solid #FAF4EA;vertical-align:top}",
  "td{padding:12px;border-bottom:1px solid var(--line);vertical-align:top}")
E(".fg.gold{background:#FFF6DD;color:#8A5B18;border-color:#F7E2A8;font-weight:700}",
  ".fg.gold{background:var(--gold-bg);color:var(--gold-tx);border-color:var(--gold-bd);font-weight:700}")

# ---------- 空态品牌化 / 搜索图标 ----------
E(".emptyi{font-size:42px;margin-bottom:13px;opacity:.3}",
  """.emptyi{display:flex;justify-content:center;margin-bottom:13px}
.emptyi svg{width:52px;height:52px;opacity:.6}""")
E(".sico{position:absolute;right:16px;top:50%;transform:translateY(-50%);color:var(--mc-yellow);font-size:21px;font-weight:800;pointer-events:none}",
  """.sico{position:absolute;right:16px;top:50%;transform:translateY(-50%);color:var(--mc-yellow-d);
  pointer-events:none;display:flex;align-items:center}
.sico svg{width:19px;height:19px;display:block}""")

# ---------- 底部留白（避开固定结算条） ----------
E(".wrap{max-width:1280px;margin:0 auto;padding:0 20px 90px}",
  ".wrap{max-width:1280px;margin:0 auto;padding:0 20px 120px}")
E(".wrap{padding:0 14px 66px}", ".wrap{padding:0 14px 110px}")

# ---------- 移动端 toast 抬到结算条上方；深色主题适配 ----------
E("""@media(prefers-reduced-motion:reduce){
  .tab{animation:none}
  .tile,.mi,.btn,.madd,.chip,.focus-img img,.mimg img{transition:none!important}
  .nb,.toast{animation:none}
}
</style>""",
"""@media(prefers-reduced-motion:reduce){
  .tab{animation:none}
  .tile,.mi,.btn,.madd,.chip,.focus-img img,.mimg img{transition:none!important}
  .nb,.toast,#cartbar.bump{animation:none}
}
@media(max-width:767px){#toastWrap{bottom:104px}}
</style>""")

# ---------- P0-4 导航图标化（7 个 tab，保留 ARIA/hash 结构） ----------
M_ICON = '<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M17.243 3.006c2.066 0 3.742 8.714 3.742 19.478H24c0-11.588-3.042-20.968-6.766-20.968-2.127 0-4.007 2.81-5.248 7.227-1.241-4.416-3.121-7.227-5.231-7.227C3.031 1.516 0 10.888 0 22.476h3.014c0-10.763 1.658-19.47 3.724-19.47 2.066 0 3.741 8.05 3.741 17.98h2.997c0-9.93 1.684-17.98 3.75-17.98Z"/></svg>'
SEARCH_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5 21 21"/></svg>'
BOWL_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 11h16a8 8 0 0 1-16 0Z"/><path d="M9.2 7.5c0-1.4 1.1-1.4 1.1-2.8M14.6 7.5c0-1.4 1.1-1.4 1.1-2.8"/></svg>'
TICKET_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 8V6.5A1.5 1.5 0 0 1 4.5 5h15A1.5 1.5 0 0 1 21 6.5V8a2.6 2.6 0 0 0 0 8v1.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5V16a2.6 2.6 0 0 0 0-8Z"/><path d="M14 5v14" stroke-dasharray="2.6 2.6"/></svg>'
BAG_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 8h14l-1 12H6L5 8Z"/><path d="M9 10V6a3 3 0 0 1 6 0v4"/></svg>'
COIN_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><path d="M9.2 9.3 12 12.5l2.8-3.2M12 12.5V17M9.8 13.9h4.4"/></svg>'
GRID_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/></svg>'

E('data-t="menu">菜单看板</button>', 'data-t="menu">' + M_ICON + '菜单看板</button>')
E('data-t="search">食物查询</button>', 'data-t="search">' + SEARCH_ICON + '食物查询</button>')
E('data-t="kcal">热量配餐</button>', 'data-t="kcal">' + BOWL_ICON + '热量配餐</button>')
E('data-t="coupon">优惠最大化<span', 'data-t="coupon">' + TICKET_ICON + '优惠最大化<span')
E('data-t="order">点单建议</button>', 'data-t="order">' + BAG_ICON + '点单建议</button>')
E('data-t="points">积分·领券</button>', 'data-t="points">' + COIN_ICON + '积分·领券</button>')
E('data-t="mcd">功能集成</button>', 'data-t="mcd">' + GRID_ICON + '功能集成</button>')

# ---------- P0-3 搜索图标（两处） ----------
E('<span class="sico">⌕</span>',
  '<span class="sico">' + SEARCH_ICON + '</span>', 2)

# ---------- P1-6 取餐 / 出行方式 → 分段控件 ----------
E("""      <div class="f"><div class="lbl">① 取餐方式</div><select id="mode">
        <option value="1">到店自取</option><option value="5">得来速车道取餐</option><option value="2">麦乐送到家</option>
      </select></div>
      <div class="f"><div class="lbl">② 出行方式</div><select id="tp">
        <option value="walk">步行</option><option value="bike">骑车</option><option value="metro">地铁</option><option value="car" selected>自驾</option>
      </select></div>""",
"""      <div class="f"><div class="lbl">① 取餐方式</div>
        <div class="seg" id="modeSeg">
          <button class="on" data-v="1"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5 5.6 4h12.8L20 9.5M4 9.5h16v10.5H4Z"/><path d="M9.6 20v-6h4.8v6"/></svg>到店自取</button>
          <button data-v="5"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 15.5v-2.5l1.8-4.7A2 2 0 0 1 7.2 7h9.6a2 2 0 0 1 1.9 1.3l1.8 4.7v2.5M3.5 15.5h17"/><circle cx="7.3" cy="17.6" r="1.7"/><circle cx="16.7" cy="17.6" r="1.7"/></svg>得来速</button>
          <button data-v="2"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6.6" cy="16.6" r="1.7"/><circle cx="17.4" cy="16.6" r="1.7"/><path d="M8.3 16.6 11 9.8h4.2l3 6.8M11 9.8H8.6M15.2 9.8V7.2h2.2"/></svg>麦乐送</button>
        </div>
      </div>
      <div class="f"><div class="lbl">② 出行方式</div>
        <div class="seg" id="tpSeg">
          <button data-v="walk">步行</button><button data-v="bike">骑车</button>
          <button data-v="metro">地铁</button><button class="on" data-v="car">自驾</button>
        </div>
      </div>""")

# ---------- JS：图标常量 / 分段控件 / 主题 ----------
E("const cache={};",
"""const cache={};
/* 品牌 SVG 图标（替代 emoji，跨平台渲染一致） */
const ICONS={
  m:'<svg viewBox="0 0 24 24" style="fill:var(--mc-yellow)" xmlns="http://www.w3.org/2000/svg"><path d="M17.243 3.006c2.066 0 3.742 8.714 3.742 19.478H24c0-11.588-3.042-20.968-6.766-20.968-2.127 0-4.007 2.81-5.248 7.227-1.241-4.416-3.121-7.227-5.231-7.227C3.031 1.516 0 10.888 0 22.476h3.014c0-10.763 1.658-19.47 3.724-19.47 2.066 0 3.741 8.05 3.741 17.98h2.997c0-9.93 1.684-17.98 3.75-17.98Z"/></svg>',
  search:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5 21 21"/></svg>',
  bag:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 8h14l-1 12H6L5 8Z"/><path d="M9 10V6a3 3 0 0 1 6 0v4"/></svg>',
  sun:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.4M12 19.1v2.4M2.5 12h2.4M19.1 12h2.4M5.3 5.3l1.7 1.7M17 17l1.7 1.7M18.7 5.3 17 7M7 17l-1.7 1.7"/></svg>',
  moon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5Z"/></svg>'
};
/* 分段控件（取餐 / 出行方式） */
function segVal(id){const el=document.querySelector('#'+id+' .on');return el?el.dataset.v:''}
document.querySelectorAll('.seg').forEach(s=>s.addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;
  s.querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
}));
/* 深色主题 */
function setTheme(t){document.documentElement.dataset.theme=t;
  try{localStorage.setItem('mcd-theme',t)}catch(e){}
  const b=document.getElementById('themeBtn');if(b)b.innerHTML=t==='dark'?ICONS.moon:ICONS.sun}
try{setTheme(localStorage.getItem('mcd-theme')||'light')}catch(e){setTheme('light')}
/* 结算条 → 跳到优惠比价 */
document.getElementById('cbBtn').onclick=function(){
  const t=document.querySelector('[data-t=coupon]');if(t)t.click();
  setTimeout(function(){var c=document.getElementById('cartList');if(c)c.scrollIntoView({behavior:'smooth',block:'center'})},80);
};""")

# ---------- JS：加入比价反馈（复用已有 toast，仅补 bump 动效） ----------
E("""function add(c){CART[c]=(CART[c]||0)+1;renderCart();toast('已加入比价 · '+(D.menu[c]?D.menu[c].name:''))}
function addAll(cs){cs.forEach(c=>CART[c]=(CART[c]||0)+1);renderCart();toast('已加入 '+cs.length+' 项，正在计算最优方案');document.querySelector('[data-t=coupon]').click();calcBest()}""",
"""function add(c){CART[c]=(CART[c]||0)+1;renderCart(true);toast('已加入比价 · '+(D.menu[c]?D.menu[c].name:''))}
function addAll(cs){cs.forEach(c=>CART[c]=(CART[c]||0)+1);renderCart(true);toast('已加入 '+cs.length+' 项，正在计算最优方案');document.querySelector('[data-t=coupon]').click();calcBest()}""")

E("function renderCart(){", "function renderCart(bump){")
E("""    `    </div>`:'<div class="empty" style="padding:26px"><div class="emptyi">\U0001F6D2</div>购物车为空<br>去「菜单看板」加入餐品</div>';
  const badge=document.getElementById('cartBadge');
  const n=ks.reduce((s,k)=>s+CART[k],0);
  if(badge){badge.textContent=n>99?'99+':n;badge.hidden=n===0;}
}""",
"""    `    </div>`:'<div class="empty" style="padding:26px"><div class="emptyi">'+ICONS.bag+'</div>购物车为空<br>去「菜单看板」加入餐品</div>';
  const badge=document.getElementById('cartBadge');
  const n=ks.reduce((s,k)=>s+CART[k],0);
  if(badge){badge.textContent=n>99?'99+':n;badge.hidden=n===0;}
  syncCartBar(bump);
}
/* 全局悬浮结算条：任何页签都能看到购物车状态 */
function syncCartBar(bump){
  const bar=document.getElementById('cartbar');if(!bar)return;
  const ks=Object.keys(CART);
  const n=ks.reduce((s,k)=>s+CART[k],0);
  const total=ks.reduce((s,k)=>s+D.menu[k].currentPrice*CART[k],0);
  const saved=ks.reduce((s,k)=>{const m=D.menu[k];return s+(m.originalPrice>m.currentPrice?(m.originalPrice-m.currentPrice)*CART[k]:0)},0);
  if(!n){bar.classList.remove('show');return}
  bar.classList.add('show');
  document.getElementById('cbN').textContent='购物车 · '+n+' 件';
  document.getElementById('cbS').textContent='已省 ¥'+saved.toFixed(1)+' · 点「去比价」算最优到手价';
  document.getElementById('cbV').textContent='¥'+total.toFixed(1);
  if(bump){bar.classList.remove('bump');void bar.offsetWidth;bar.classList.add('bump')}
}""")

E('<span class="ifb">\U0001F354</span>', '<span class="ifb">${ICONS.m}</span>', 2)
E('<div class="mimg-fb">\U0001F354</div>', '<div class="mimg-fb">${ICONS.m}</div>')
E('<div class="emptyi">\U0001F354</div>', '<div class="emptyi">${ICONS.m}</div>')
E('<div class="emptyi">\U0001F50D</div>', '<div class="emptyi">${ICONS.search}</div>')

E("""  const tp=document.getElementById('tp').value,mode=+document.getElementById('mode').value,
    o=document.getElementById('orderOut');""",
"""  const tp=segVal('tpSeg'),mode=+segVal('modeSeg'),
    o=document.getElementById('orderOut');""")

E("""  document.getElementById('cpC').innerHTML=D.coupons.claimed.map(c=>`<span class="fg">${c}</span>`).join('');
  document.getElementById('cpA').innerHTML=D.coupons.claimable.map(c=>`<span class="fg hot">${c}</span>`).join('');""",
"""  document.getElementById('cpC').innerHTML=D.coupons.claimed.map(c=>`<span class="cp">${c}</span>`).join('');
  document.getElementById('cpA').innerHTML=D.coupons.claimable.map(c=>`<span class="cp a">${c}</span>`).join('');""")

E('style="width:150px;height:150px;object-fit:contain;background:#fff;border-radius:14px"',
  'style="width:150px;height:150px;object-fit:contain;background:var(--card);border-radius:14px"')
E('style="background:#FDFAF4"', 'style="background:var(--card2)"', 6)

# ---------- HTML：全局结算条 + 主题按钮（插在 three.js 脚本前） ----------
E('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>',
"""<!-- ================= 全局悬浮结算条 / 主题切换 ================= -->
<div id="cartbar">
  <div class="cb-l"><div class="cb-n" id="cbN">购物车 · 0 件</div><div class="cb-s" id="cbS">点「去比价」算最优到手价</div></div>
  <div class="cb-v" id="cbV">¥0</div>
  <button class="btn r" id="cbBtn" type="button">去比价</button>
</div>
<button id="themeBtn" type="button" title="切换深色 / 浅色模式" aria-label="切换深色 / 浅色模式"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.4M12 19.1v2.4M2.5 12h2.4M19.1 12h2.4M5.3 5.3l1.7 1.7M17 17l1.7 1.7M18.7 5.3 17 7M7 17l-1.7 1.7"/></svg></button>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>""")

# ---------- 执行 ----------
CHECK_ONLY = "--check" in sys.argv
fails = []
for i, (old, new, cnt) in enumerate(edits):
    actual = s.count(old)
    if actual != cnt:
        fails.append((i, cnt, actual, old[:90].replace("\n", "\\n")))
if CHECK_ONLY or fails:
    for i, cnt, actual, snippet in fails:
        print("EDIT %d FAIL: expected %d, got %d | %s" % (i, cnt, actual, snippet))
    if fails:
        sys.exit(1)
    print("CHECK OK: all %d anchors matched" % len(edits))
    sys.exit(0)
for i, (old, new, cnt) in enumerate(edits):
    s = s.replace(old, new)

open(P, "w", encoding="utf-8").write(s)
print("OK: %d edits applied" % len(edits))
