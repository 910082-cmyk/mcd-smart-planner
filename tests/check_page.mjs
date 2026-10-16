#!/usr/bin/env node
/*
 * 页面结构与数据自检（check_page.mjs）
 * 覆盖：种子数据自洽 / 页面结构 / 无障碍骨架 / 交互节点 / 降级与诚实口径
 * 用法：node tests/check_page.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');

/* ---------- 断言 harness ---------- */
let pass = 0, fail = 0;
const failures = [];
function ok(cond, label, detail) {
  if (cond) { pass++; console.log('  ✓ ' + label); }
  else { fail++; failures.push(label + (detail ? ' —— ' + detail : '')); console.log('  ✗ ' + label + (detail ? ' —— ' + detail : '')); }
}
function section(t) { console.log('\n[' + t + ']'); }

/* ---------- 括号配平抽取 SEED（页面只有一行，正则不可靠） ---------- */
function extractSeed(src) {
  const i = src.indexOf('const SEED = ');
  if (i < 0) return null;
  let j = src.indexOf('{', i), depth = 0, k = j, inStr = false, esc = false;
  for (; k < src.length; k++) {
    const c = src[k];
    if (inStr) {
      if (esc) esc = false;
      else if (c === '\\') esc = true;
      else if (c === '"') inStr = false;
      continue;
    }
    if (c === '"') inStr = true;
    else if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) { k++; break; } }
  }
  return JSON.parse(src.slice(j, k));
}

const D = extractSeed(html);

/* ================= 1. 种子数据自洽 ================= */
section('种子数据自洽（SEED 内联常量）');
ok(D !== null, 'SEED 可解析为合法 JSON');
if (D) {
  const menu = D.menu || {};
  const codes = Object.keys(menu);
  ok(codes.length === 121, '菜单恰为 121 项', '实际 ' + codes.length);
  let fMiss = 0, pMiss = 0, iMiss = 0, cMiss = 0, badPrice = 0, badImg = 0;
  const imgs = new Set();
  for (const k of codes) {
    const it = menu[k];
    if (!it.name) fMiss++;
    if (it.currentPrice == null) pMiss++;
    if (!it.image) iMiss++;
    if (!it.cat) cMiss++;
    if (!(typeof it.currentPrice === 'number' && isFinite(it.currentPrice) && it.currentPrice >= 0)) badPrice++;
    if (!/^https:\/\/menu-img\.mcd\.cn\//.test(it.image || '')) badImg++;
    imgs.add(it.image);
  }
  ok(fMiss === 0 && pMiss === 0 && iMiss === 0 && cMiss === 0,
    '每项餐品字段齐全（name/currentPrice/image/cat）',
    `缺 name ${fMiss} / price ${pMiss} / image ${iMiss} / cat ${cMiss}`);
  ok(badPrice === 0, 'currentPrice 均为非负数值', '异常 ' + badPrice + ' 项');
  ok(badImg === 0, '商品图全部来自官方 CDN（menu-img.mcd.cn）', '异常 ' + badImg + ' 项');
  ok(imgs.size === 121, '121 项商品图 URL 互不重复（与 _meta.imageCount 一致）', '实际 ' + imgs.size);

  const cats = D.menuOrder || [];
  ok(cats.length === 15, '官方分类恰为 15 类', '实际 ' + cats.length);
  let miss = 0, dup = 0;
  const seen = new Set();
  cats.forEach(c => (c.codes || []).forEach(x => {
    if (!menu[x]) miss++;
    if (seen.has(x)) dup++;
    seen.add(x);
  }));
  ok(miss === 0, '分类编码全部存在于菜单', '缺失 ' + miss);
  ok(dup > 0 && dup <= 15, '跨类目重复编码在预期区间（实测 9，同一编码可属多类）', '实测 ' + dup);

  const go = D.menuGlobalOrder || [];
  const goSet = new Set(go);
  const noGo = codes.filter(k => !goSet.has(k)).length;
  const noMenu = go.filter(k => !menu[k]).length;
  ok(go.length === 121 && noGo === 0 && noMenu === 0,
    'menuGlobalOrder 与菜单键集合一一对应', `global ${go.length} / 缺全局序 ${noGo} / 序中无菜品 ${noMenu}`);

  const stores = D.stores || [];
  ok(stores.length === 5, '门店恰为 5 家', '实际 ' + stores.length);
  const sMiss = stores.filter(s => !s.storeCode || !s.storeName || !s.address || s.distance == null || typeof s.businessStatus !== 'boolean').length;
  ok(sMiss === 0, '门店字段齐全（code/name/address/distance/businessStatus）', '缺字段 ' + sMiss + ' 家');

  const nut = D.nutrition || {};
  const nutKeys = Object.keys(nut);
  ok(nutKeys.length === 61, '全国营养库恰为 61 项', '实际 ' + nutKeys.length);
  ok(nutKeys.every(k => k && k.length > 0) && new Set(nutKeys).size === nutKeys.length,
    '营养库键全部为非空且互不重复');
  const nutFieldMiss = nutKeys.filter(k => {
    const n = nut[k];
    return n == null || [n.kcal, n.protein, n.fat, n.carb, n.sodium, n.calcium].some(v => typeof v !== 'number');
  }).length;
  ok(nutFieldMiss === 0, '营养库每项含 kcal/蛋白/脂肪/碳水/钠/钙 六个数值字段', '缺字段 ' + nutFieldMiss + ' 项');
  const nameHit = nutKeys.filter(k => Object.values(menu).some(m => m.name === k)).length;
  ok(nameHit >= 10, '营养库与菜单按名称可对应（两套键空间，名称桥接，实测 ' + nameHit + '/61）', '实测 ' + nameHit);
  const withKcal = codes.filter(k => typeof menu[k].kcal === 'number').length;
  ok(withKcal >= 40, '含热量餐品 ≥ 40 项（配餐模块候选池口径，README 记为 41）', '实际 ' + withKcal);

  const cp = D.coupons || {};
  ok(Array.isArray(cp.claimed) && Array.isArray(cp.claimable), '优惠券含 claimed / claimable 两个名单');
  ok(D._meta && D._meta.storeCode === '3390081' && !!D._meta.capturedAt && D._meta.imageCount === 121,
    '_meta 采样口径完整（storeCode 3390081 / capturedAt / imageCount 121）');

  /* 页面 SEED 与 data/seed-data.json 同源 */
  try {
    const raw = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'seed-data.json'), 'utf8'));
    ok(Object.keys(raw.menu).length === 121 && Object.keys(raw.nutrition).length === 61
      && raw.stores.length === 5 && raw.menuOrder.length === 15,
      'data/seed-data.json 与页面 SEED 计数一致');
  } catch (e) {
    ok(false, 'data/seed-data.json 与页面 SEED 计数一致', e.message);
  }
}

/* ================= 2. 页面结构 ================= */
section('页面结构');
ok(/<title>[^<]*麦麦智配/.test(html), 'title 含产品名');
ok(/<html lang="zh-CN">/.test(html), 'html lang=zh-CN');
ok(/<meta charset="utf-8"/i.test(html), '声明 utf-8 编码');
ok(/<meta name="viewport" content="width=device-width, initial-scale=1\.0"/.test(html)
  && !/user-scalable\s*=\s*no|maximum-scale\s*=\s*1/.test(html),
  'viewport 不禁用户缩放');
ok((html.match(/<main[\s>]/g) || []).length === 1, '唯一 main 地标');
ok(/<nav role="tablist" aria-label="功能模块切换">/.test(html), 'tablist 带可访问名称');

const tabs = [...html.matchAll(/role="tab" id="tab-([a-z]+)" aria-controls="([a-z]+)"[^>]*data-t="([a-z]+)"/g)];
ok(tabs.length === 7, '共 7 个功能 tab', '实际 ' + tabs.length);
const EXPECT = ['menu', 'search', 'kcal', 'coupon', 'order', 'points', 'mcd'];
ok(tabs.length === 7 && tabs.every((m, idx) => m[1] === EXPECT[idx] && m[2] === EXPECT[idx] && m[3] === EXPECT[idx]),
  'tab 顺序与 aria-controls / data-t 三者一致');
const panels = EXPECT.filter(id => new RegExp(`id="${id}"[\\s>]`).test(html));
ok(panels.length === 7, '7 个面板容器全部存在', '缺 ' + EXPECT.filter(e => !panels.includes(e)).join(','));
ok((html.match(/aria-selected="true"/g) || []).length === 1, '恰好一个 tab 处于选中态');

/* 先剥掉内联脚本内容，避免把 document.write 里的字符串误判为 script 标签 */
const htmlNoScript = html.replace(/<script(?![^>]*src)[^>]*>[\s\S]*?<\/script>/g, '');
const srcs = [...htmlNoScript.matchAll(/<script src="([^"]+)"/g)].map(m => m[1]);
ok(srcs.filter(s => s.startsWith('vendor/')).length >= 7 && fs.existsSync(path.join(ROOT, 'vendor', 'three.min.js')),
  'Three.js 及后期处理全部本地化（vendor/）');
const remote = srcs.filter(s => /^https?:/.test(s));
ok(remote.length === 0, '无远程 script 依赖（CDN 仅作 document.write 兜底）', '发现 ' + remote.join(','));

ok(!/javascript:/i.test(html), '无 javascript: URL');
ok(!/TODO|FIXME|lorem|XXX/i.test(html), '无占位文本残留');
ok(/#FFC72C/i.test(html) && /#DA291C/i.test(html), '官方品牌色 #FFC72C / #DA291C 均在使用');
ok(/prefers-reduced-motion/.test(html), '适配 prefers-reduced-motion');
ok(/:focus-visible/.test(html), '键盘焦点态可见（:focus-visible）');
ok(!/\b(alert|confirm|prompt)\s*\(/.test(html), '无 alert/confirm/prompt 打断式弹窗');

/* ================= 3. 交互节点 ================= */
section('交互节点');
const scripts = [...html.matchAll(/<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let syntaxBad = 0;
scripts.forEach((s, i) => {
  try { new Function(s); } catch (e) { syntaxBad++; console.log('    脚本块 #' + i + ' 语法错误: ' + e.message); }
});
ok(scripts.length > 0 && syntaxBad === 0, '全部 ' + scripts.length + ' 个内联脚本语法可解析', '失败 ' + syntaxBad + ' 块');

const declared = new Set();
const jsAll = scripts.join('\n');
for (const m of jsAll.matchAll(/function\s+([A-Za-z_$][\w$]*)\s*\(/g)) declared.add(m[1]);
for (const m of jsAll.matchAll(/(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:function|\()/g)) declared.add(m[1]);
const handlers = [...html.matchAll(/\son(?:click|input|change|submit|keydown|keyup)="([A-Za-z_$][\w$]*)\(/g)].map(m => m[1]);
const undef = [...new Set(handlers)].filter(h => !declared.has(h));
ok(handlers.length > 0 && undef.length === 0,
  '全部 ' + [...new Set(handlers)].length + ' 个内联事件处理器均有函数声明',
  '未声明: ' + undef.join(','));

/* ================= 4. 降级与诚实口径 ================= */
section('降级与诚实口径');
ok((html.match(/onerror=/g) || []).length >= 3, '商品图有 onerror 降级链');
ok((html.match(/catch/g) || []).length >= 5, '3D / 初始化链路有异常兜底');
ok((html.match(/const SEED = /g) || []).length === 1, 'SEED 只定义一次（单一数据源）');
ok(/calculate-price/.test(html) && /未调用/.test(html), '页面明示金额未经 calculate-price 官方回验');
ok(/不提供门店实时客流/.test(html), '页面明示门店推荐的能力边界（无实时客流数据）');
ok(/create-order/.test(html) && /下单前必做/.test(html), '页面引导下单前回验与确认（看板不创建订单）');

/* ================= 5. README 引用完整性 ================= */
section('README 引用完整性');
try {
  const readme = fs.readFileSync(path.join(ROOT, 'README.md'), 'utf8');
  const refs = [...readme.matchAll(/\]\((assets\/[^)]+)\)/g)].map(m => m[1]);
  ok(refs.length >= 2, 'README 至少引用 2 处 assets 资源（主视觉 + 长图）', '实际 ' + refs.length);
  const missingRefs = refs.filter(r => !fs.existsSync(path.join(ROOT, r)));
  ok(missingRefs.length === 0, 'README 引用的 assets 文件全部存在', '缺失: ' + missingRefs.join(','));
  for (const doc of ['CONTEST_DECLARATION.md', 'MCP_INTEGRATION.md', 'workbuddy.md']) {
    ok(readme.includes(doc), 'README 链接受必需文档 ' + doc);
  }
} catch (e) {
  ok(false, 'README 可读取', e.message);
}

/* ---------- 汇总 ---------- */
console.log('\n========================================');
console.log(`通过 ${pass} 项，失败 ${fail} 项`);
if (fail) {
  console.log('失败明细：');
  failures.forEach(f => console.log('  - ' + f));
  process.exit(1);
}
console.log('[OK] 页面结构与数据自检全部通过');
