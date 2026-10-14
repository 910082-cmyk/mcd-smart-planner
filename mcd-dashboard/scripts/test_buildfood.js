/* 单元测试：验证 buildFood 对所有 121 项餐品都能成功构建 3D 模型，不抛异常 */
const fs = require('fs');
const path = require('path');

// ---- mock THREE：只记录调用，不真正渲染 ----
let geoCount = 0, meshCount = 0;
function Geo(){ geoCount++; return { dispose(){} }; }
function Mat(){ return { opacity:1, transparent:false }; }
const THREE = {
  Group: class { constructor(){ this.children=[]; this.position={set(){},x:0,y:0,z:0,lerp(){}}; this.rotation={x:0,y:0,z:0}; this.scale={setScalar(){},x:1,y:1,z:1}; this.userData={}; } add(o){ if(o) this.children.push(o); return this; } traverse(f){ f(this); this.children.forEach(c=>c.traverse&&c.traverse(f)); } },
  Mesh: class { constructor(g,m){ meshCount++; this.geometry=g; this.material=m; this.position={set(x,y,z){this.x=x;this.y=y;this.z=z},lerp(){}}; this.rotation={x:0,y:0,z:0}; this.scale={setScalar(v){this.s=v},x:1,y:1,z:1}; } },
  Vector3: class { constructor(x,y,z){this.x=x;this.y=y;this.z=z} },
  CylinderGeometry: function(){ return new Geo(); },
  BoxGeometry: function(){ return new Geo(); },
  SphereGeometry: function(){ return new Geo(); },
  TorusGeometry: function(){ return new Geo(); },
  CircleGeometry: function(){ return new Geo(); },
  TubeGeometry: function(){ return new Geo(); },
  CatmullRomCurve3: class { constructor(){} },
  MeshStandardMaterial: function(){ return Mat(); },
  MeshBasicMaterial: function(){ return Mat(); },
  AmbientLight: class {}, DirectionalLight: class {}, PointLight: class {},
  Fog: class {}, Color: class {}, PerspectiveCamera: class {}, Scene: class {},
  WebGLRenderer: class { constructor(){ throw new Error('沙箱禁渲染'); } },
};

// ---- 从 index.html 抽出 buildFood 及其依赖 ----
const html = fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const m = html.match(/function buildFood\(it\)\{[\s\S]*?\n  \}\n\n/);
const helpers = html.match(/function addBurger[\s\S]*?(?=\n\n  \/\/ ---- 舞台管理)/);
if(!m || !helpers){ console.error('抽取失败'); process.exit(1); }

// 构造可执行上下文
const M = {};
['bun','bunT','patty','chicken','cheese','lettuce','tomato','fish','fry','box','boxY','cup','coffee','soda','ice','cone','pie','steel','toy','apple','corn']
  .forEach(k=>M[k]={});
const mk = (g,mat,x=0,y=0,z=0)=>({geometry:g,material:mat,position:{x,y,z,set(a,b,c){this.x=a;this.y=b;this.z=c},lerp(){}},rotation:{x:0,y:0,z:0},scale:{x:1,y:1,z:1,s:1,setScalar(v){this.s=v;this.x=this.y=this.z=v},set(a,b,c){this.x=a;this.y=b;this.z=c}}});

const src = m[0].replace(/function\s+buildFood\s*\(\s*it\s*\)\s*\{/,'var buildFood = function(it){') + '\n' + helpers[0]
  .replace(/function\s+(add\w+)\s*\(([^)]*)\)\s*\{/g,'var $1 = function($2){');

const fn = new Function('THREE','M','mk','cache', src + '; return {buildFood, addBurger, addFries, addDrink, addCoffee, addDrumstick, addHashBrown, addCorn, addApple, addSnackBox, addPie, addIceCream, addHappyBox};');
const api = fn(THREE, M, mk, {});

// ---- 跑全部餐品 ----
const D = JSON.parse(fs.readFileSync(path.join(__dirname,'..','data','seed-data.json'),'utf8'));
const order = [];
D.menuOrder.forEach(c=>c.codes.forEach(x=>order.push({code:x, cat:c.name})));
D.menuGlobalOrder.forEach(x=>{ if(!order.find(o=>o.code===x)) order.push({code:x,cat:'?'}); });

let ok=0, fail=[];
const buckets={};
order.forEach(({code,cat})=>{
  const it = Object.assign({}, D.menu[code]);
  it.cat = (it.cat||cat).replace(/\\n/g,' ');
  try{
    const g = api.buildFood(it);
    if(!g || !g.children || g.children.length===0) throw new Error('空模型');
    ok++;
    const k = cat; buckets[k]=(buckets[k]||0)+1;
  }catch(e){ fail.push({code, name:it.name, cat, err:e.message}); }
});

console.log('总餐品：%d   建模成功：%d   失败：%d', order.length, ok, fail.length);
console.log('几何体总数：%d', geoCount);
console.log('\n各分类建模情况：');
D.menuOrder.forEach(c=>console.log('  ' + String(c.name).padEnd(18) + ' ' + (buckets[c.name]||0) + ' 项'));
if(fail.length){
  console.log('\n失败明细：');
  fail.slice(0,10).forEach(f=>console.log('  x', f.name, '['+f.cat+']', f.err));
  process.exit(1);
}else{
  console.log('\n[OK] 全部餐品建模通过，无异常');
}
