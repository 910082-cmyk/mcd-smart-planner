# -*- coding: utf-8 -*-
"""
对 index.html 做四项手术（每项都有断言，未命中即报错）：
  1. hero 3D 场景重做：官方 M 轮廓 -> ExtrudeGeometry 倒角挤出 + 程序化环境反射 + 慢速呼吸
  2. 移除菜单 3D 舞台（canvas/fb2d/initMenu3D/全部建模代码），改为大图精选面板
  3. 菜单区动画全面放缓 + 缩略图条自定义 800ms 缓动滚动
  4. 同步清理 loop/IntersectionObserver/focusAt/render/init 中的 3D 舞台引用
"""
import io, os, re, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
CONTOURS = os.path.join(ROOT, 'assets', 'm-contours.json')

h = io.open(HTML, encoding='utf-8').read()
orig_len = len(h)
poly = json.load(io.open(CONTOURS, encoding='utf-8'))['outer']
M_POLY_JS = 'const M_POLY=' + json.dumps(poly, ensure_ascii=False) + ';'
print('轮廓点: %d，内联 %d 字节' % (len(poly), len(M_POLY_JS)))

def rep(old, new, tag, count=1):
    global h
    n = h.count(old)
    assert n == count, '[%s] 期望 %d 处，实际 %d 处' % (tag, count, n)
    h = h.replace(old, new)
    print('  OK %s' % tag)

# ============================================================ 1. hero 3D 场景
HERO_NEW = '''/* ============================================================
   场景一：品牌区金色双拱门
   官方 SVG 轮廓 -> ExtrudeGeometry 倒角挤出，程序化环境反射，慢速呼吸动画。
   WebGL / THREE 不可用时降级为静态官方矢量标志（见 hero-fb）。
   ============================================================ */
let heroTick=null;
(function(){
  const cv=document.getElementById('gl');
  if(!cv||!window.THREE){fbHero();return}
  const size=()=>({W:cv.clientWidth||innerWidth,H:cv.clientHeight||290});
  let {W,H}=size(), renderer;
  try{renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true,alpha:false,powerPreference:'high-performance'})}
  catch(e){fbHero();return}
  function fbHero(){cv.style.display='none';const f=document.getElementById('heroFb');
    if(f)f.style.display='block';
    const m=document.getElementById('htMode');if(m)m.textContent='官方矢量标志';}

  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.setSize(W,H,false);
  const scene=new THREE.Scene();
  scene.background=new THREE.Color(0xDA291C);
  const cam=new THREE.PerspectiveCamera(42,W/H,.1,120);
  cam.position.set(0,0,17.5);

  scene.add(new THREE.AmbientLight(0xffffff,.5));
  const k1=new THREE.DirectionalLight(0xFFE9C0,1.45);k1.position.set(-6,8,10);scene.add(k1);
  const k2=new THREE.DirectionalLight(0xffffff,.45);k2.position.set(8,2,4);scene.add(k2);
  const rim=new THREE.PointLight(0xFFD98A,1.05,32);rim.position.set(3,-4,6);scene.add(rim);

  /* ---- 程序化环境反射（金属材质需要环境才有质感，无则死黑）---- */
  const ec=document.createElement('canvas');ec.width=512;ec.height=256;
  const g2=ec.getContext('2d');
  const vg=g2.createLinearGradient(0,0,0,256);
  vg.addColorStop(0,'#FFE3A8');vg.addColorStop(.42,'#F0A83A');
  vg.addColorStop(.55,'#DA291C');vg.addColorStop(1,'#4A0B06');
  g2.fillStyle=vg;g2.fillRect(0,0,512,256);
  // 主光斑（暖金）+ 副光斑（冷白）
  for(const [cx,cy,r,col] of [[150,60,70,'rgba(255,240,200,.95)'],[390,90,46,'rgba(255,255,255,.55)']]){
    const rg=g2.createRadialGradient(cx,cy,4,cx,cy,r);
    rg.addColorStop(0,col);rg.addColorStop(1,'rgba(255,255,255,0)');
    g2.fillStyle=rg;g2.beginPath();g2.arc(cx,cy,r,0,6.29);g2.fill();
  }
  const envTex=new THREE.CanvasTexture(ec);
  envTex.mapping=THREE.EquirectangularReflectionMapping;
  scene.environment=envTex;

  /* ---- 官方双拱门轮廓 -> 挤出 3D（倒角让边缘有高光）---- */
  const shape=new THREE.Shape();
  M_POLY.forEach((p,i)=>i===0?shape.moveTo(p[0],p[1]):shape.lineTo(p[0],p[1]));
  shape.closePath();
  const geo=new THREE.ExtrudeGeometry(shape,{
    depth:1.15,bevelEnabled:true,bevelThickness:.10,bevelSize:.10,
    bevelSegments:3,curveSegments:1,steps:1});
  geo.center();
  const mat=new THREE.MeshStandardMaterial({
    color:0xFFC72C,metalness:.86,roughness:.20,
    emissive:0x3D2400,emissiveIntensity:.38});
  const grp=new THREE.Group();
  grp.add(new THREE.Mesh(geo,mat));
  grp.rotation.y=-.34;
  scene.add(grp);

  /* ---- 背后辉光（canvas 径向渐变，避免平面感）---- */
  const gc=document.createElement('canvas');gc.width=gc.height=256;
  const gx=gc.getContext('2d');
  const gr2=gx.createRadialGradient(128,128,8,128,128,128);
  gr2.addColorStop(0,'rgba(255,216,112,.60)');
  gr2.addColorStop(.45,'rgba(255,190,70,.20)');
  gr2.addColorStop(1,'rgba(255,190,70,0)');
  gx.fillStyle=gr2;gx.fillRect(0,0,256,256);
  const glow=new THREE.Mesh(new THREE.PlaneGeometry(18,13),
    new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(gc),transparent:true,depthWrite:false}));
  glow.position.set(0,0,-3.4);scene.add(glow);

  /* ---- 底座双环 ---- */
  const ring=new THREE.Mesh(new THREE.TorusGeometry(3.15,.05,10,72),
    new THREE.MeshBasicMaterial({color:0xFFD98A,transparent:true,opacity:.45}));
  ring.rotation.x=Math.PI/2;ring.position.y=-4.62;scene.add(ring);
  const ring2=new THREE.Mesh(new THREE.TorusGeometry(3.6,.028,10,72),
    new THREE.MeshBasicMaterial({color:0xFFFFFF,transparent:true,opacity:.2}));
  ring2.rotation.x=Math.PI/2;ring2.position.y=-4.66;scene.add(ring2);

  /* ---- 漂浮晶体粒子 ---- */
  const floaters=[],pg=new THREE.OctahedronGeometry(.17,0);
  for(let i=0;i<18;i++){
    const m=new THREE.Mesh(pg,new THREE.MeshStandardMaterial({
      color:i%2?0xFFD98A:0xFFFFFF,metalness:.6,roughness:.3,transparent:true,opacity:.85}));
    m.position.set(-11+Math.random()*22,-4+Math.random()*9,-5+Math.random()*9);
    m.userData={sp:.14+Math.random()*.36,ph:Math.random()*6.28,
      ry:(Math.random()-.5)*.02,rx:(Math.random()-.5)*.014};
    scene.add(m);floaters.push(m);
  }

  /* ---- 响应式布局：宽屏 M 靠右，窄屏居中缩小 ---- */
  function layout(){
    const s=size();
    const wide=s.W/s.H>3;
    grp.position.x=wide?4.7:0;
    grp.position.y=wide?-.05:.2;
    const sc=wide?1:.78;
    grp.scale.setScalar(sc);
    glow.position.x=grp.position.x;
    glow.scale.setScalar(wide?1:1.25);
    ring.position.x=grp.position.x;ring2.position.x=grp.position.x;
  }
  layout();

  let mx=0,my=0;
  cv.addEventListener('pointermove',e=>{const r=cv.getBoundingClientRect();
    mx=((e.clientX-r.left)/r.width-.5)*2;my=((e.clientY-r.top)/r.height-.5)*2});
  cv.addEventListener('pointerleave',()=>{mx=my=0});

  let t=0;
  heroTick=function(){
    t+=.008;                                    // 慢速呼吸
    grp.rotation.y=-.34+Math.sin(t*.42)*.13+mx*.22;
    grp.rotation.x=Math.sin(t*.6)*.03+my*.05;
    grp.position.y=(W/size().H>3?-.05:.2)+Math.sin(t*.8)*.13;
    ring.material.opacity=.4+Math.sin(t*1.1)*.13;
    ring2.material.opacity=.16+Math.sin(t*1.1+.9)*.09;
    ring.rotation.z=t*.16;
    glow.material.opacity=.78+Math.sin(t*.7)*.12;
    floaters.forEach(m=>{
      m.position.y+=Math.sin(t+m.userData.ph)*m.userData.sp*.012;
      m.rotation.y+=m.userData.ry;m.rotation.x+=m.userData.rx;});
    cam.position.x+=(mx*.9-cam.position.x)*.04;
    cam.position.y+=(-my*.6-cam.position.y)*.04;
    cam.lookAt(grp.position.x*.35,0,0);
    renderer.render(scene,cam);
  };
  addEventListener('resize',()=>{const s=size();W=s.W;H=s.H;
    renderer.setSize(W,H,false);cam.aspect=W/H;cam.updateProjectionMatrix();layout()});
})();
'''

HDR = '/* ' + '='*60
start = h.find(HDR + '\n   场景一：品牌区双拱门')
assert start >= 0, '未找到场景一代码块'
end = h.find('\n})();\n\n' + HDR + '\n   场景二', start)
assert end >= 0, '未找到场景二锚点'
h = h[:start] + HERO_NEW.rstrip('\n') + '\n' + h[end+1:]
print('  OK 场景一替换')

# ============================================================ 2. 移除场景二（3D 食物舞台）
s2 = h.find(HDR + '\n   场景二：3D 食物模型舞台')
assert s2 >= 0, '未找到场景二代码块'
e2 = h.find('window.__menu3d={setFocus:setFocus,ok:true};\n}', s2)
assert e2 >= 0, '未找到场景二结尾'
h = h[:s2] + h[e2+len('window.__menu3d={setFocus:setFocus,ok:true};\n}'):]
print('  OK 场景二整体移除（含全部建模代码）')

# ============================================================ 3. 菜单舞台 HTML -> 大图精选面板
rep('''  <div class="stage">
    <canvas id="menu3d"></canvas>
    <div class="fb2d" id="fb2d"><img id="fb2dImg" src="" alt=""></div>
    <div class="stage-hint" id="stageHint">悬停或点击缩略图 · 模型将浮现并聚焦</div>
    <div class="stage-cat" id="stageCat">人气热卖</div>
    <div class="focus" id="focusPanel"></div>
  </div>''',
'''  <div class="stage">
    <div class="stage-badge">官方菜单 · 精选餐品</div>
    <div class="focus" id="focusPanel"></div>
  </div>''', '菜单舞台 HTML 替换')

# ============================================================ 4. CSS：舞台/聚焦面板 + 动画放缓
rep('''/* ================= 3D 舞台（含 2D 降级） ================= */
.stage{background:linear-gradient(170deg,#FFFCF5 0%,#FFF4DF 100%);border:1.5px solid var(--line);
  border-radius:var(--r);overflow:hidden;margin-bottom:16px;position:relative}
#menu3d{width:100%;height:400px;display:block}
.stage-hint{position:absolute;left:16px;top:14px;font-size:11.5px;color:var(--ink3);
  background:rgba(255,255,255,.85);padding:4px 10px;border-radius:999px;border:1px solid var(--line);pointer-events:none;z-index:3}
.stage-cat{position:absolute;right:16px;top:14px;font-size:11.5px;font-weight:700;color:var(--mc-red-d);
  background:rgba(255,255,255,.88);padding:4px 11px;border-radius:999px;border:1px solid #F7E2A8;pointer-events:none;z-index:3}
/* 2D 降级视图：大图 + CSS 动画 */
.fb2d{display:none;height:400px;align-items:center;justify-content:center;position:relative}
.fb2d img{width:250px;height:250px;object-fit:contain;animation:fbFloat 3.2s ease-in-out infinite;
  filter:drop-shadow(0 18px 28px rgba(138,91,24,.28))}
.fb2d::after{content:"";position:absolute;bottom:52px;left:50%;transform:translateX(-50%);
  width:190px;height:22px;border-radius:50%;background:rgba(138,91,24,.14);animation:fbShadow 3.2s ease-in-out infinite}
@keyframes fbFloat{0%,100%{transform:translateY(0) rotate(-1.5deg)}50%{transform:translateY(-16px) rotate(1.5deg)}}
@keyframes fbShadow{0%,100%{width:190px;opacity:.16}50%{width:150px;opacity:.09}}''',
'''/* ================= 精选餐品面板 ================= */
.stage{background:linear-gradient(170deg,#FFFCF5 0%,#FFF4DF 100%);border:1.5px solid var(--line);
  border-radius:var(--r);overflow:hidden;margin-bottom:16px;position:relative}
.stage-badge{position:absolute;left:16px;top:14px;font-size:11.5px;font-weight:800;color:#8A5B18;
  background:rgba(255,255,255,.9);padding:5px 12px;border-radius:999px;border:1px solid #F7E2A8;
  pointer-events:none;z-index:3;letter-spacing:.5px}''', '舞台 CSS 重写')

rep('''.focus{display:flex;gap:20px;padding:20px 24px;border-top:1.5px solid var(--line);background:#fff;align-items:center;flex-wrap:wrap}
.focus-img{width:120px;height:120px;border-radius:14px;background:#F7F1E7;flex-shrink:0;overflow:hidden;border:1.5px solid var(--line);position:relative}
.focus-img img{width:100%;height:100%;object-fit:cover}''',
'''.focus{display:flex;gap:26px;padding:26px 28px;background:transparent;align-items:center;flex-wrap:wrap}
.focus-img{width:210px;height:210px;border-radius:18px;background:#F7F1E7;flex-shrink:0;overflow:hidden;
  border:1.5px solid var(--line);position:relative;box-shadow:0 10px 26px rgba(138,91,24,.14)}
.focus-img img{width:100%;height:100%;object-fit:cover;transition:transform 1.1s cubic-bezier(.22,.61,.36,1)}
.focus-img:hover img{transform:scale(1.05)}''', '聚焦面板大图化')

# --- 动画放缓 ---
rep('.tab{display:none;animation:fade .26s ease}', '.tab{display:none;animation:fade .5s ease}', 'tab 切换放缓')
rep('@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}',
    '@keyframes fade{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}', 'fade 关键帧')
rep('''nav button{flex:1;min-width:max-content;background:none;border:0;padding:12px 13px;border-radius:13px;
  font-family:inherit;font-size:13.5px;color:var(--ink2);cursor:pointer;font-weight:600;transition:.16s;white-space:nowrap}''',
'''nav button{flex:1;min-width:max-content;background:none;border:0;padding:12px 13px;border-radius:13px;
  font-family:inherit;font-size:13.5px;color:var(--ink2);cursor:pointer;font-weight:600;transition:.32s;white-space:nowrap}''', '导航按钮过渡放缓')
rep('.mi{background:#fff;border:1.5px solid var(--line);border-radius:15px;overflow:hidden;transition:.2s;display:flex;flex-direction:column}',
    '.mi{background:#fff;border:1.5px solid var(--line);border-radius:15px;overflow:hidden;transition:.5s cubic-bezier(.22,.61,.36,1);display:flex;flex-direction:column}', '卡片过渡放缓')
rep('.mi:hover{border-color:var(--mc-yellow);transform:translateY(-4px);box-shadow:0 14px 32px rgba(255,199,44,.3)}',
    '.mi:hover{border-color:var(--mc-yellow);transform:translateY(-3px);box-shadow:0 14px 32px rgba(255,199,44,.26)}', '卡片悬停放缓')
rep('.mimg img{width:100%;height:100%;object-fit:cover;transition:transform .35s}',
    '.mimg img{width:100%;height:100%;object-fit:cover;transition:transform 1s cubic-bezier(.22,.61,.36,1)}', '商品图放大放缓')
rep('.mi:hover .mimg img{transform:scale(1.07)}', '.mi:hover .mimg img{transform:scale(1.04)}', '放大倍率收敛')
rep('''.tile{flex-shrink:0;width:88px;cursor:pointer;border:2px solid var(--line);border-radius:11px;overflow:hidden;
  background:#fff;transition:.18s;position:relative;padding:0;font-family:inherit}''',
'''.tile{flex-shrink:0;width:88px;cursor:pointer;border:2px solid var(--line);border-radius:11px;overflow:hidden;
  background:#fff;transition:.4s cubic-bezier(.22,.61,.36,1);position:relative;padding:0;font-family:inherit}''', '缩略图过渡放缓')
rep('.tile:hover{border-color:var(--mc-yellow);transform:translateY(-3px)}',
    '.tile:hover{border-color:var(--mc-yellow);transform:translateY(-2px)}', '缩略图悬停放缓')
rep('.tile.on{border-color:var(--mc-red);box-shadow:0 6px 18px rgba(218,41,28,.26);transform:translateY(-3px)}',
    '.tile.on{border-color:var(--mc-red);box-shadow:0 6px 18px rgba(218,41,28,.26);transform:translateY(-2px)}', '缩略图选中态')
rep('.strip-l{display:flex;gap:9px;overflow-x:auto;padding-bottom:6px;scroll-behavior:smooth}',
    '.strip-l{display:flex;gap:9px;overflow-x:auto;padding-bottom:6px}', '移除浏览器默认平滑滚动')
rep('''.chip{background:#FFFDF9;border:1.5px solid var(--line);border-radius:999px;padding:8px 15px;font-size:13px;
  cursor:pointer;color:var(--ink2);transition:.16s;font-family:inherit;font-weight:600}''',
'''.chip{background:#FFFDF9;border:1.5px solid var(--line);border-radius:999px;padding:8px 15px;font-size:13px;
  cursor:pointer;color:var(--ink2);transition:.3s;font-family:inherit;font-weight:600}''', '分类 chip 过渡放缓')
rep('.madd:hover{background:var(--mc-yellow-d);transform:scale(1.02)}',
    '.madd:hover{background:var(--mc-yellow-d);transform:scale(1.015)}', '加入比价悬停收敛')
rep('.madd{margin-top:auto;background:var(--mc-yellow);border:0;border-radius:9px;padding:9px;font-family:inherit;font-size:12.5px;font-weight:800;color:#4A3000;cursor:pointer;transition:.15s}',
    '.madd{margin-top:auto;background:var(--mc-yellow);border:0;border-radius:9px;padding:9px;font-family:inherit;font-size:12.5px;font-weight:800;color:#4A3000;cursor:pointer;transition:.35s}', '加入比价过渡放缓')

# ============================================================ 5. JS：循环/聚焦/渲染清理
rep('''/* 统一渲染循环：离屏暂停 */
const VIS={hero:true,menu:true};
const io=new IntersectionObserver(es=>es.forEach(e=>{
  const k=e.target.id==='gl'?'hero':(e.target.id==='menu3d'?'menu':null);
  if(k)VIS[k]=e.isIntersecting;
}),{threshold:.02});
['gl','menu3d'].forEach(id=>{const el=document.getElementById(id);if(el)io.observe(el)});
function loop(){requestAnimationFrame(loop);
  if(VIS.hero&&heroTick)heroTick();
  if(VIS.menu&&menuTick)menuTick();}''',
'''/* 统一渲染循环：离屏暂停（仅品牌区 3D） */
const VIS={hero:true};
const io=new IntersectionObserver(es=>es.forEach(e=>{
  if(e.target.id==='gl')VIS.hero=e.isIntersecting;
}),{threshold:.02});
{const el=document.getElementById('gl');if(el)io.observe(el)}
function loop(){requestAnimationFrame(loop);
  if(VIS.hero&&heroTick)heroTick();}''', '渲染循环清理')

rep('''/* 2D 降级视图 */
function renderFb2d(it){
  const box=document.getElementById('fb2d'),img=document.getElementById('fb2dImg');
  if(!it.image){box.style.display='none';return}
  img.src=it.image; img.alt=it.name;
  box.style.display='flex';
}

''', '', '移除 2D 降级函数')

rep('''  focusCode=code;
  renderFocusPanel(it,code);
  renderFb2d(it);
  if(window.__menu3d)window.__menu3d.setFocus(code);
  const strip=document.getElementById('strip');
  [...strip.children].forEach((el,j)=>el.classList.toggle('on',j===i));
  const on=strip.children[i];
  if(on)on.scrollIntoView({block:'nearest',inline:'center',behavior:'smooth'});
}''',
'''  focusCode=code;
  renderFocusPanel(it,code);
  const strip=document.getElementById('strip');
  [...strip.children].forEach((el,j)=>el.classList.toggle('on',j===i));
  const on=strip.children[i];
  if(on)scrollStripTo(on);
}

/* 缩略图条缓动滚动：800ms easeInOutCubic，节奏放慢便于看清 */
function scrollStripTo(el){
  const box=document.getElementById('strip');
  if(!box||!el)return;
  const target=el.offsetLeft-box.clientWidth/2+el.offsetWidth/2;
  const start=box.scrollLeft, d=target-start, dur=800, t0=performance.now();
  const ease=k=>k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;
  (function step(now){
    const k=Math.min(1,(now-t0)/dur);
    box.scrollLeft=start+d*ease(k);
    if(k<1)requestAnimationFrame(step);
  })(t0);
}''', 'focusAt 清理 + 自定义缓动滚动')

rep("  document.getElementById('stageCat').textContent=catName;\n", '', 'render 清理 stageCat')
rep('''  init();
  initMenu3D();          // 3D 舞台（失败自动降级，不影响上面已渲染的面板）''',
'''  init();''', 'init 清理')

# ============================================================ 6. 内联轮廓数据
rep('/* ============================================================\n   场景一：品牌区金色双拱门',
    M_POLY_JS + '\n\n/* ============================================================\n   场景一：品牌区金色双拱门', '内联 M_POLY')

# htMode 文案
rep('<span class="ht" id="htMode">3D 食物模型 · Three.js</span>',
    '<span class="ht" id="htMode">3D 金拱门 · Three.js</span>', '模式标签文案')

io.open(HTML, 'w', encoding='utf-8').write(h)
print('\n完成：%d -> %d 字节 (+%d)' % (orig_len, len(h), len(h) - orig_len))
