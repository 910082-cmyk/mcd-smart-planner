# -*- coding: utf-8 -*-
"""第二批：修复主题按钮点击 / P2 三项 / hero 3D 场景升级（Three.js）"""
import sys

P = "index.html"
s = open(P, encoding="utf-8").read()
edits = []
spans = []

def E(old, new, count=1):
    edits.append((old, new, count))

def S(start_marker, end_marker, new):
    spans.append((start_marker, end_marker, new))

# ================= 1. 修复主题按钮：补点击事件 + aria-pressed =================
E("""function setTheme(t){document.documentElement.dataset.theme=t;
  try{localStorage.setItem('mcd-theme',t)}catch(e){}
  const b=document.getElementById('themeBtn');if(b)b.innerHTML=t==='dark'?ICONS.moon:ICONS.sun}
try{setTheme(localStorage.getItem('mcd-theme')||'light')}catch(e){setTheme('light')}""",
"""function setTheme(t){document.documentElement.dataset.theme=t;
  try{localStorage.setItem('mcd-theme',t)}catch(e){}
  const b=document.getElementById('themeBtn');
  if(b){b.innerHTML=t==='dark'?ICONS.moon:ICONS.sun;b.setAttribute('aria-pressed',String(t==='dark'))}}
try{setTheme(localStorage.getItem('mcd-theme')||'light')}catch(e){setTheme('light')}
document.getElementById('themeBtn').onclick=function(){
  setTheme(document.documentElement.dataset.theme==='dark'?'light':'dark');
};""")

# ================= 2. P2-a 积分当钱花 =================
E("""      <div class="stat mc"><div class="statv" id="pLack">1</div><div class="statl">积分不足</div></div>
    </div>
  </div>""",
"""      <div class="stat mc"><div class="statv" id="pLack">1</div><div class="statl">积分不足</div></div>
    </div>
    <div class="ptc">
      <div class="ptc-h"><span>积分当钱花</span><b id="ptcV">—</b></div>
      <div class="bar" style="margin-top:9px"><div class="barf" id="ptcBar" style="width:0%;background:var(--mc-yellow)"></div></div>
      <div class="ptc-s" id="ptcS">正在计算…</div>
    </div>
  </div>""")

E(".pcs{font-size:12.5px;color:#8A5B18;margin-top:7px}",
""".pcs{font-size:12.5px;color:#8A5B18;margin-top:7px}
.ptc{flex-basis:100%;margin-top:14px;background:rgba(255,255,255,.55);border-radius:12px;padding:12px 15px}
.ptc-h{display:flex;justify-content:space-between;align-items:baseline;font-size:12.5px;font-weight:800;color:#7A4E10}
.ptc-h b{font-size:17px;color:#3A2010}
.ptc-s{font-size:11.5px;color:#8A5B18;margin-top:7px;line-height:1.6}""")

E("""  document.getElementById('pLack').textContent=pp.filter(p=>p.point>D.account.availablePoint).length;""",
"""  document.getElementById('pLack').textContent=pp.filter(p=>p.point>D.account.availablePoint).length;

  /* 积分当钱花：当前积分折算价值 + 距最低兑换档进度 */
  if(pp.length){
    const cheap=pp.reduce((a,p)=>p.point<a.point?a:a);
    const bestV=pp.reduce((a,p)=>parseFloat(p.selling.match(/([\\d.]+)元/)[1])>parseFloat(a.selling.match(/([\\d.]+)元/)[1])?p:a);
    const bestPer=parseFloat(bestV.selling.match(/([\\d.]+)元/)[1])/bestV.point;
    const ap=D.account.availablePoint;
    document.getElementById('ptcV').textContent='≈ ¥'+(ap*bestPer).toFixed(1);
    document.getElementById('ptcBar').style.width=Math.min(100,ap/cheap.point*100).toFixed(1)+'%';
    document.getElementById('ptcS').textContent=ap>=cheap.point
      ?'已过最低兑换档（'+cheap.point+' 积分），当前可兑 '+pp.filter(p=>p.point<=ap).length+' 张；按最划算券折算，每积分 ≈ '+bestPer.toFixed(3)+' 元'
      :'再攒 '+(cheap.point-ap).toFixed(1)+' 积分即可兑换「'+cheap.spuName+'」（'+cheap.point+' 积分档）';
  }""")

# ================= 3. P2-b 导航横滑渐隐边缘 =================
E("""nav::-webkit-scrollbar-track{background:transparent}""",
"""nav::-webkit-scrollbar-track{background:transparent}
/* 导航横滑渐隐边缘：提示可左右滑动 */
.navwrap{position:relative}
.navwrap::before,.navwrap::after{content:"";position:absolute;top:20px;bottom:6px;width:46px;z-index:7;pointer-events:none}
.navwrap::before{left:0;background:linear-gradient(90deg,var(--card),transparent)}
.navwrap::after{right:0;background:linear-gradient(270deg,var(--card),transparent)}""")

E("""<nav role="tablist" aria-label="功能模块切换">""",
"""<div class="navwrap">
<nav role="tablist" aria-label="功能模块切换">""")
E("""</nav>""", """</nav>
</div>""")

# ================= 4. P2-c 标题字距收紧 =================
E(""".brand-tx h1{font-size:30px;font-weight:800;color:#fff;letter-spacing:-.8px;line-height:1.1;text-shadow:0 2px 12px rgba(0,0,0,.28)}""",
  """.brand-tx h1{font-size:30px;font-weight:800;color:#fff;letter-spacing:-1.1px;line-height:1.1;text-shadow:0 2px 12px rgba(0,0,0,.28)}""")

E('<span class="ht" id="htMode">3D 金拱门 · Three.js</span>',
  '<span class="ht" id="htMode">3D 金拱门舞台 · Three.js</span>')

# ================= 5. 主题按钮按压反馈 =================
E("""#themeBtn svg{width:20px;height:20px;display:block}""",
"""#themeBtn svg{width:20px;height:20px;display:block}
#themeBtn:active{transform:scale(.92)}""")

# ================= 6. hero 3D 场景升级（整段替换） =================
NEW_HERO = r"""let heroTick=null;
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
  const cam=new THREE.PerspectiveCamera(42,W/H,.1,160);
  cam.position.set(0,0,30);

  scene.add(new THREE.AmbientLight(0xffffff,.5));
  const k1=new THREE.DirectionalLight(0xFFE9C0,1.45);k1.position.set(-6,8,10);scene.add(k1);
  const k2=new THREE.DirectionalLight(0xffffff,.45);k2.position.set(8,2,4);scene.add(k2);
  const rim=new THREE.PointLight(0xFFD98A,1.05,36);rim.position.set(3,-4,6);scene.add(rim);
  const rim2=new THREE.PointLight(0xFFF3D0,.7,30);rim2.position.set(-5,3,5);scene.add(rim2);

  /* ---- 程序化环境反射（金属材质需要环境才有质感）---- */
  const ec=document.createElement('canvas');ec.width=512;ec.height=256;
  const g2=ec.getContext('2d');
  const vg=g2.createLinearGradient(0,0,0,256);
  vg.addColorStop(0,'#FFE3A8');vg.addColorStop(.42,'#F0A83A');
  vg.addColorStop(.55,'#DA291C');vg.addColorStop(1,'#4A0B06');
  g2.fillStyle=vg;g2.fillRect(0,0,512,256);
  for(const [cx,cy,r,col] of [[150,60,70,'rgba(255,240,200,.95)'],[390,90,46,'rgba(255,255,255,.55)'],[60,200,90,'rgba(255,220,150,.35)']]){
    const rg=g2.createRadialGradient(cx,cy,4,cx,cy,r);
    rg.addColorStop(0,col);rg.addColorStop(1,'rgba(255,255,255,0)');
    g2.fillStyle=rg;g2.beginPath();g2.arc(cx,cy,r,0,6.29).fill();
  }
  const envTex=new THREE.CanvasTexture(ec);
  envTex.mapping=THREE.EquirectangularReflectionMapping;
  scene.environment=envTex;

  /* ---- canvas 贴图工具 ---- */
  function cnv(w,h,draw){const c=document.createElement('canvas');c.width=w;c.height=h;
    draw(c.getContext('2d'),w,h);return new THREE.CanvasTexture(c)}

  /* ---- 舞台组：宽屏靠右，窄屏居中 ---- */
  const stage=new THREE.Group();scene.add(stage);

  /* ---- 官方双拱门轮廓 -> 挤出 3D（倒角高光）---- */
  const shape=new THREE.Shape();
  M_POLY.forEach((p,i)=>i===0?shape.moveTo(p[0],p[1]):shape.lineTo(p[0],p[1]));
  shape.closePath();
  const mGeo=new THREE.ExtrudeGeometry(shape,{
    depth:1.15,bevelEnabled:true,bevelThickness:.10,bevelSize:.10,
    bevelSegments:3,curveSegments:1,steps:1});
  mGeo.center();
  const grp=new THREE.Group();
  grp.add(new THREE.Mesh(mGeo,new THREE.MeshStandardMaterial({
    color:0xFFC72C,metalness:.9,roughness:.18,
    emissive:0x3D2400,emissiveIntensity:.38})));
  grp.rotation.y=-.34;
  stage.add(grp);

  /* ---- 三座悬浮小金拱门：环绕主拱门公转 ---- */
  const minis=[];
  [[.16,4.7,.5,1.1,0],[.11,5.8,-.38,2.2,2.1],[.085,3.8,.72,-.6,4.0]].forEach(([sc,r,sp,y,ph],i)=>{
    const m=new THREE.Mesh(mGeo,new THREE.MeshStandardMaterial({
      color:i===1?0xFFE08A:0xFFC72C,metalness:.88,roughness:.22,
      emissive:0x3D2400,emissiveIntensity:.3}));
    m.scale.setScalar(sc);
    m.userData={r,sp,y,ph};
    stage.add(m);minis.push(m);
  });

  /* ---- 反射舞台圆盘（金属吸环境）---- */
  const disc=new THREE.Mesh(new THREE.CircleGeometry(9.2,72),
    new THREE.MeshStandardMaterial({color:0x8E160C,metalness:.95,roughness:.34}));
  disc.rotation.x=-Math.PI/2;disc.position.y=-4.92;stage.add(disc);

  /* ---- 接触阴影（径向渐变贴片，接地用）---- */
  const shTex=cnv(256,256,(g)=>{const rg=g.createRadialGradient(128,128,6,128,128,128);
    rg.addColorStop(0,'rgba(20,0,0,.5)');rg.addColorStop(1,'rgba(20,0,0,0)');
    g.fillStyle=rg;g.fillRect(0,0,256,256)});
  const sh=new THREE.Mesh(new THREE.PlaneGeometry(11,11),
    new THREE.MeshBasicMaterial({map:shTex,transparent:true,depthWrite:false}));
  sh.rotation.x=-Math.PI/2;sh.position.y=-4.88;stage.add(sh);

  /* ---- 刻度环：24 枚金钉 ---- */
  const tickGeo=new THREE.BoxGeometry(.07,.03,.42);
  const tickMat=new THREE.MeshStandardMaterial({color:0xFFD98A,metalness:.8,roughness:.3,
    emissive:0x3D2400,emissiveIntensity:.25});
  const ticks=new THREE.Group();
  for(let i=0;i<24;i++){
    const a=i/24*Math.PI*2;
    const t=new THREE.Mesh(tickGeo,tickMat);
    t.position.set(Math.cos(a)*8.1,0,Math.sin(a)*8.1);
    t.rotation.y=-a;
    ticks.add(t);
  }
  ticks.position.y=-4.86;stage.add(ticks);

  /* ---- 底座三环 ---- */
  const ring=new THREE.Mesh(new THREE.TorusGeometry(3.6,.05,10,72),
    new THREE.MeshBasicMaterial({color:0xFFD98A,transparent:true,opacity:.45}));
  ring.rotation.x=Math.PI/2;ring.position.y=-4.84;stage.add(ring);
  const ring2=new THREE.Mesh(new THREE.TorusGeometry(4.5,.028,10,72),
    new THREE.MeshBasicMaterial({color:0xFFFFFF,transparent:true,opacity:.2}));
  ring2.rotation.x=Math.PI/2;ring2.position.y=-4.85;stage.add(ring2);
  const ring3=new THREE.Mesh(new THREE.TorusGeometry(6.4,.02,8,96),
    new THREE.MeshBasicMaterial({color:0xFFD98A,transparent:true,opacity:.12}));
  ring3.rotation.x=Math.PI/2;ring3.position.y=-4.85;stage.add(ring3);

  /* ---- 背后辉光 ---- */
  const glowTex=cnv(256,256,(g)=>{const rg=g.createRadialGradient(128,128,8,128,128,128);
    rg.addColorStop(0,'rgba(255,216,112,.60)');rg.addColorStop(.45,'rgba(255,190,70,.20)');
    rg.addColorStop(1,'rgba(255,190,70,0)');g.fillStyle=rg;g.fillRect(0,0,256,256)});
  const glow=new THREE.Mesh(new THREE.PlaneGeometry(20,15),
    new THREE.MeshBasicMaterial({map:glowTex,transparent:true,depthWrite:false}));
  glow.position.set(0,0,-4);stage.add(glow);

  /* ---- 顶部体积光锥（叠加混合）---- */
  const beamTex=cnv(64,256,(g,w,h)=>{const lg=g.createLinearGradient(0,0,0,h);
    lg.addColorStop(0,'rgba(255,240,200,.9)');lg.addColorStop(1,'rgba(255,240,200,0)');
    g.fillStyle=lg;g.fillRect(0,0,w,h)});
  const beams=[];
  for(let i=0;i<2;i++){
    const b=new THREE.Mesh(new THREE.PlaneGeometry(7,16),
      new THREE.MeshBasicMaterial({map:beamTex,transparent:true,opacity:.1,
        blending:THREE.AdditiveBlending,depthWrite:false}));
    b.position.set(i?2.6:-2.6,3.4,-3.2);
    b.rotation.z=i?-.14:.14;
    stage.add(b);beams.push(b);
  }

  /* ---- 金色尘埃粒子（上浮循环）---- */
  const DN=220;
  const dpos=new Float32Array(DN*3), dspd=new Float32Array(DN);
  for(let i=0;i<DN;i++){
    dpos[i*3]=(Math.random()-.5)*30;
    dpos[i*3+1]=-5+Math.random()*12;
    dpos[i*3+2]=-8+Math.random()*10;
    dspd[i]=.12+Math.random()*.5;
  }
  const dgeo=new THREE.BufferGeometry();
  dgeo.setAttribute('position',new THREE.BufferAttribute(dpos,3));
  const dustTex=cnv(64,64,(g)=>{const rg=g.createRadialGradient(32,32,2,32,32,32);
    rg.addColorStop(0,'rgba(255,255,255,1)');rg.addColorStop(.4,'rgba(255,230,160,.6)');
    rg.addColorStop(1,'rgba(255,230,160,0)');g.fillStyle=rg;g.fillRect(0,0,64,64)});
  const dust=new THREE.Points(dgeo,new THREE.PointsMaterial({
    size:.16,map:dustTex,transparent:true,opacity:.85,depthWrite:false,
    blending:THREE.AdditiveBlending,color:0xFFE9B8,sizeAttenuation:true}));
  scene.add(dust);

  /* ---- 漂浮晶体 ---- */
  const floaters=[],pg=new THREE.OctahedronGeometry(.17,0);
  for(let i=0;i<18;i++){
    const m=new THREE.Mesh(pg,new THREE.MeshStandardMaterial({
      color:i%2?0xFFD98A:0xFFFFFF,metalness:.6,roughness:.3,transparent:true,opacity:.85}));
    m.position.set((Math.random()-.5)*24,-4+Math.random()*10,-6+Math.random()*9);
    m.userData={sp:.14+Math.random()*.36,ph:Math.random()*6.28,
      ry:(Math.random()-.5)*.02,rx:(Math.random()-.5)*.014};
    scene.add(m);floaters.push(m);
  }

  /* ---- 响应式布局：宽屏舞台靠右，窄屏居中缩小 ---- */
  let wide=true;
  function layout(){
    const s=size();
    wide=s.W/s.H>3;
    stage.position.x=wide?4.7:0;
    dust.position.x=stage.position.x*.4;
  }
  layout();

  /* ---- 交互：鼠标视差 + 拖拽旋转（带惯性）---- */
  let mx=0,my=0,dragging=false,lastX=0,vel=0,spin=-.34;
  cv.style.touchAction='pan-y';
  cv.addEventListener('pointermove',e=>{
    if(dragging){const dx=e.clientX-lastX;lastX=e.clientX;vel=dx*.008;spin+=vel;return}
    const r=cv.getBoundingClientRect();
    mx=((e.clientX-r.left)/r.width-.5)*2;my=((e.clientY-r.top)/r.height-.5)*2});
  cv.addEventListener('pointerdown',e=>{dragging=true;lastX=e.clientX;vel=0;
    try{cv.setPointerCapture(e.pointerId)}catch(err){}});
  const endDrag=()=>{dragging=false};
  cv.addEventListener('pointerup',endDrag);
  cv.addEventListener('pointercancel',endDrag);
  cv.addEventListener('pointerleave',()=>{dragging=false;mx=my=0});

  /* ---- 入场动画：相机推进 + 拱门回弹缩放 ---- */
  let intro=RM?1:0, t=0;
  const easeOut=k=>1-Math.pow(1-k,3);
  const easeBack=k=>{const c=1.70158;return 1+(c+1)*Math.pow(k-1,3)+c*Math.pow(k-1,2)};

  heroTick=function(){
    t+=.008;
    if(intro<1)intro=Math.min(1,intro+.014);
    const ie=easeOut(intro), ib=easeBack(intro);
    cam.position.z=30-12.5*ie;
    grp.scale.setScalar((wide?1:.8)*(.55+.45*ib));
    grp.position.y=(wide?-.05:.2)+Math.sin(t*.8)*.13;
    if(!dragging){vel*=.94;spin+=vel+(RM?0:.0022)}
    grp.rotation.y=spin+Math.sin(t*.42)*.13+mx*.22;
    grp.rotation.x=Math.sin(t*.6)*.03+my*.05;
    /* 小金拱门公转 */
    minis.forEach(m=>{
      const u=m.userData,a=t*u.sp+u.ph;
      m.position.set(Math.cos(a)*u.r,u.y+Math.sin(t*1.2+u.ph)*.35,Math.sin(a)*u.r);
      m.rotation.y=-a+Math.PI/2;
      m.rotation.z=Math.sin(t+u.ph)*.12;
    });
    /* 舞台氛围 */
    ring.material.opacity=.4+Math.sin(t*1.1)*.13;
    ring2.material.opacity=.16+Math.sin(t*1.1+.9)*.09;
    ring3.material.opacity=.1+Math.sin(t*.7)*.05;
    ticks.rotation.y=t*.05;
    glow.material.opacity=.78+Math.sin(t*.7)*.12;
    beams.forEach((b,i)=>{b.material.opacity=(.09+i*.03)+Math.sin(t*.9+i*2)*.025});
    /* 尘埃上浮循环 */
    for(let i=0;i<DN;i++){
      dpos[i*3+1]+=dspd[i]*.008;
      if(dpos[i*3+1]>7.5){dpos[i*3+1]=-5.5;dpos[i*3]=(Math.random()-.5)*30}
    }
    dgeo.attributes.position.needsUpdate=true;
    dust.rotation.y=t*.012;
    floaters.forEach(m=>{
      m.position.y+=Math.sin(t+m.userData.ph)*m.userData.sp*.012;
      m.rotation.y+=m.userData.ry;m.rotation.x+=m.userData.rx;});
    cam.position.x+=(mx*.9-cam.position.x)*.04;
    cam.position.y+=(-my*.6-cam.position.y)*.04;
    cam.lookAt(stage.position.x*.35,0,0);
    renderer.render(scene,cam);
  };
  let rzT=0;
  addEventListener('resize',()=>{clearTimeout(rzT);rzT=setTimeout(()=>{
    const s=size();if(s.W===W&&s.H===H)return;W=s.W;H=s.H;
    renderer.setSize(W,H,false);cam.aspect=W/H;cam.updateProjectionMatrix();layout()},140)});
  /* 减少动态效果偏好：只渲染一帧静态画面，停止持续动画 */
  if(RM){heroTick();heroTick=null}
})();"""

S("let heroTick=null;", "if(RM){heroTick();heroTick=null}\n})();", NEW_HERO)

# ================= 执行 =================
CHECK_ONLY = "--check" in sys.argv
fails = []
for i, (old, new, cnt) in enumerate(edits):
    actual = s.count(old)
    if actual != cnt:
        fails.append("EDIT %d FAIL: expected %d, got %d | %s" % (i, cnt, actual, old[:80].replace("\n", "\\n")))
for i, (a, b, new) in enumerate(spans):
    ia, ib = s.find(a), s.find(b, s.find(a) + len(a)) if s.find(a) >= 0 else -1
    if ia < 0 or ib < 0:
        fails.append("SPAN %d FAIL: markers not found (start=%d end=%d)" % (i, ia, ib))
if CHECK_ONLY or fails:
    for f in fails:
        print(f)
    if fails:
        sys.exit(1)
    print("CHECK OK: %d edits + %d spans matched" % (len(edits), len(spans)))
    sys.exit(0)
for old, new, cnt in edits:
    s = s.replace(old, new)
for a, b, new in spans:
    ia = s.find(a)
    ib = s.find(b, ia + len(a)) + len(b)
    s = s[:ia] + new + s[ib:]

open(P, "w", encoding="utf-8").write(s)
print("OK: %d edits + %d spans applied" % (len(edits), len(spans)))
