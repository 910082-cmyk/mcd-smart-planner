#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麦麦智配 · 决策引擎（Skill 脚本）

把「麦麦智配」看板的核心消费决策逻辑封装为可在 WorkBuddy 中调用的命令行工具。
数据默认读取项目内已固化的 seed-data.json（离线演示）；亦可在 WorkBuddy 中
实时调用麦当劳 MCP 刷新数据后重新生成 seed。

子命令：
  kcal    热量配餐：给定目标热量，生成 2–3 品低卡组合
  deal    优惠最大化：给定购物车，计算菜单价 / 促销价 / 麦金卡价 / 积分叠加后的最优实付
  advise  点单建议：结合人数、距离、出行方式与取餐方式，推荐最近门店并给出理由
  points  积分当钱花：展示积分享当前折算价值、距最低兑换档进度与可兑券种
  search  食物查询：按名称检索单品价格 / 热量 / 营养 / 可兑积分券
  cart    购物车结算：件数 / 已省 / 合计
  menu    菜单浏览：按分类 / 关键词 / 排序列出在售餐品

所有命令输出 JSON，便于 WorkBuddy 解析后自然语言转述给用户。
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from itertools import combinations

NOW = datetime.now()

# ----------------------------- 数据加载 -----------------------------

def find_seed():
    d = os.path.dirname(os.path.abspath(__file__))
    while d and d != os.path.dirname(d):
        cand = os.path.join(d, 'data', 'seed-data.json')
        if os.path.exists(cand):
            return cand
        d = os.path.dirname(d)
    return None


def load_seed(path=None):
    p = path or find_seed()
    if not p or not os.path.exists(p):
        raise FileNotFoundError('未找到 seed-data.json，请通过 --seed 指定路径')
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def _not_expired(down_time):
    try:
        return datetime.strptime(down_time.replace(' ', 'T'), '%Y-%m-%dT%H:%M:%S') > NOW
    except Exception:
        return True


def _yuan(selling):
    """从 '6.9元可乐麦炫酷1份' 中提取面值数字，与看板 JS 口径一致。"""
    m = re.search(r'([\d.]+)元', selling or '')
    return float(m.group(1)) if m else 0.0


# ----------------------------- 模块实现 -----------------------------

def plan_kcal(seed, target=800, tol=0.2, sort='per', top=6):
    if not (100 <= target <= 3000):
        target = min(3000, max(100, target))
    pool = [dict(code=c, **seed['menu'][c]) for c in seed['menuGlobalOrder']
            if seed['menu'][c].get('kcal') and seed['menu'][c]['kcal'] > 0
            and '酱' not in seed['menu'][c]['name']]
    res = []
    n = len(pool)
    for r in range(2, 4):  # 2 或 3 品组合
        for combo in combinations(range(n), r):
            items = [pool[i] for i in combo]
            kcal = sum(x['kcal'] for x in items)
            if kcal < target * (1 - tol) or kcal > target * (1 + tol):
                continue
            price = sum(x['currentPrice'] for x in items)
            res.append({
                'set': [{'code': x['code'], 'name': x['name'], 'kcal': x['kcal'],
                         'currentPrice': x['currentPrice'], 'image': x.get('image')} for x in items],
                'kcal': kcal, 'price': round(price, 1), 'per': round(price / kcal, 4),
            })
    if not res:
        return {'target': target, 'tol': tol, 'count': 0,
                'message': '在 ±%d%% 容差内没有找到 2–3 品组合，建议放宽容差或调整目标热量' % round(tol * 100)}
    res.sort(key=(lambda x: x['price']) if sort == 'price' else (lambda x: x['per']))
    # 去重（按 code 组合）
    seen, picks = set(), []
    for r in res:
        key = '|'.join(sorted(x['code'] for x in r['set']))
        if key not in seen:
            seen.add(key)
            picks.append(r)
    picks = picks[:top]
    for i, p in enumerate(picks, 1):
        p['rank'] = i
        p['dayRatio'] = round(p['kcal'] / 2300 * 100)
    return {'target': target, 'tol': tol, 'count': len(res), 'top': picks}


def calc_best(seed, cart, account=None):
    items = []
    for code, qty in cart.items():
        m = seed['menu'].get(code)
        if not m:
            continue
        items.append({'code': code, 'name': m['name'], 'qty': qty,
                      'currentPrice': m['currentPrice'], 'originalPrice': m['originalPrice'],
                      'discountType': m.get('discountType')})
    if not items:
        return {'error': '购物车为空或不含有效餐品'}
    list_price = sum(x['currentPrice'] * x['qty'] for x in items)
    orig_price = sum(x['originalPrice'] * x['qty'] for x in items)
    gold = [x for x in items if x['discountType'] == '随单购麦金卡优惠']
    best_gold = min(sum(x['currentPrice'] * x['qty'] for x in gold), list_price) if gold else list_price
    ap = account if account is not None else seed.get('account', {}).get('availablePoint', 0)
    pts = [p for p in seed.get('pointsProducts', [])
           if _not_expired(p['downTime']) and p['point'] <= ap]
    best_pt = max((_yuan(p['selling']) for p in pts), default=0.0)
    best_pt_p = next((p for p in pts if _yuan(p['selling']) == best_pt), None)
    final = min(best_gold, list_price) - best_pt
    stages = [
        {'stage': '菜单原价', 'amount': round(orig_price, 1), 'basis': 'originalPrice 合计'},
        {'stage': '促销优惠后', 'amount': round(list_price, 1),
         'basis': 'currentPrice 合计%s' % ('，含 %d 项促销优惠' % len([x for x in items if x['discountType'] == '促销优惠']) if any(x['discountType'] == '促销优惠' for x in items) else '')},
    ]
    if gold:
        stages.append({'stage': '麦金卡到手价', 'amount': round(best_gold, 1),
                       'basis': '随单购麦金卡优惠%s' % ('，可再省 ¥%.1f' % (list_price - best_gold) if best_gold < list_price else '（无额外优惠）')})
    if best_pt:
        stages.append({'stage': '积分兑换叠加', 'amount': -round(best_pt, 1),
                       'basis': '%s（%d 积分）' % (best_pt_p['spuName'], best_pt_p['point'])})
    stages.append({'stage': '最优实付', 'amount': round(final, 1),
                   'basis': '较原价省 ¥%.1f（%d%%）' % (orig_price - final, round((1 - final / orig_price) * 100)) if orig_price else '—'})
    return {'items': items, 'stages': stages, 'final': round(final, 1),
            'saved': round(list_price - final, 1), 'note': '金额为菜单 currentPrice 推算，未调用 calculate-price 官方回验；叠加积分需经商城独立链路，与门店点餐结算不通。'}


def advise(seed, people=1, maxd=1500, tp='walk', mode=1):
    people = min(10, max(1, int(people)))
    maxd = max(100, int(maxd))
    ss = sorted([s for s in seed['stores'] if s['distance'] <= maxd], key=lambda s: s['distance'])
    if not ss:
        return {'error': '%d 米内无可用门店，请放宽距离限制' % maxd}
    top = ss[0]
    tp_n = {'walk': '步行', 'bike': '骑车', 'metro': '地铁', 'car': '自驾'}.get(tp, '步行')
    w = {'car': 1.6, 'bike': 1.3, 'metro': 1.15}.get(tp, 1.0)
    eta = top['distance'] / 80 * w
    mode_n = {1: '到店自取（beType=1）', 5: '得来速车道取餐（beType=5）', 2: '麦乐送到家（beType=2）'}.get(mode, '到店自取（beType=1）')
    reasons = []
    if tp == 'car' and mode == 5:
        reasons.append('自驾 + 车道取餐，全程不进店，避开堂食排队（推荐组合）')
    elif tp == 'car':
        reasons.append('自驾出行，但当前为堂食场景，需预留停车与进店时间')
    elif tp == 'walk':
        reasons.append('步行 %d 米，按 80 米/分钟估算约 %d 分钟' % (top['distance'], round(eta)))
    elif tp == 'bike':
        reasons.append('骑行 %d 米，约 %d 分钟' % (top['distance'], round(eta)))
    else:
        reasons.append('地铁换乘步行 %d 米，约 %d 分钟' % (top['distance'], round(eta)))
    reasons.append('营业时间 %s–%s，当前%s' % (top['businessStartTime'], top['businessEndTime'], '营业中' if top['businessStatus'] else '休息中'))
    if top['reservation']:
        reasons.append('支持预约下单，可跳过现场点单环节直接取餐')
    if people >= 2:
        combo = '四件套' if people >= 4 else '三件套'
        cnt = sum(1 for m in seed['menu'].values() if combo in m['name'])
        reasons.append('%d 人用餐建议选%s类套餐，当前菜单有 %d 款可选' % (people, combo, cnt))
    if mode == 2:
        reasons.append('麦乐送场景需先经 delivery-query-addresses 确认配送地址，再查可配送门店')
    return {
        'recommend': {'storeName': top['storeName'], 'storeCode': top['storeCode'],
                      'distance': top['distance'], 'etaMin': round(eta), 'mode': mode_n, 'travel': tp_n,
                      'people': people, 'businessStatus': top['businessStatus'], 'reservation': top['reservation']},
        'reasons': reasons,
        'alternatives': [{'storeName': s['storeName'], 'distance': s['distance']} for s in ss[1:4]],
        'boundary': '麦当劳 MCP 不提供门店实时客流/排队/繁忙度数据；推荐仅基于距离、营业状态、预约能力与取餐方式推导，不含实时路况与排队预估。',
        'mustDo': '下单前将最终金额交由 calculate-price 官方回验，并在用户确认后再调用 create-order（会真实下单并产生费用）。',
    }


def points_info(seed, account=None):
    ap = account if account is not None else seed.get('account', {}).get('availablePoint', 0)
    pp = [p for p in seed.get('pointsProducts', []) if _not_expired(p['downTime'])]
    if not pp:
        return {'availablePoint': ap, 'available': 0, 'message': '当前无可兑换积分券'}
    cheap = min(pp, key=lambda p: p['point'])
    best_v = max(pp, key=lambda p: _yuan(p['selling']))
    best_per = _yuan(best_v['selling']) / best_v['point']
    return {
        'availablePoint': ap, 'availableCount': len(pp),
        'cheapestTier': {'spuName': cheap['spuName'], 'point': cheap['point']},
        'bestValue': {'spuName': best_v['spuName'], 'yuan': _yuan(best_v['selling']), 'point': best_v['point'], 'perPoint': round(best_per, 3)},
        'equivalentYuan': round(ap * best_per, 1),
        'progressToCheapest': round(min(100, ap / cheap['point'] * 100), 1),
        'status': ('已过最低兑换档（%d 积分），当前可兑 %d 张' % (cheap['point'], len([p for p in pp if p['point'] <= ap]))) if ap >= cheap['point']
                  else ('再攒 %d 积分即可兑换「%s」（%d 积分档）' % (cheap['point'] - ap, cheap['spuName'], cheap['point'])),
        'list': [{'spuName': p['spuName'], 'point': p['point'], 'yuan': _yuan(p['selling']),
                  'perPoint': round(_yuan(p['selling']) / p['point'], 3), 'downTime': p['downTime'],
                  'redeemable': p['point'] <= ap} for p in sorted(pp, key=lambda p: p['point'])],
    }


def search(seed, q):
    if not q:
        return {'error': '请提供查询关键词'}
    nut = seed['nutrition'].get(q) or next((seed['nutrition'][k] for k in seed['nutrition'] if q in k), None)
    menu = next((m for m in seed['menu'].values() if m['name'] == q), None) or \
           next((m for m in seed['menu'].values() if q in m['name']), None)
    ap = seed.get('account', {}).get('availablePoint', 0)
    pts = [p for p in seed.get('pointsProducts', []) if _not_expired(p['downTime']) and p['point'] <= ap]
    out = {}
    if menu:
        off = menu['originalPrice'] > menu['currentPrice']
        out['menu'] = {'name': menu['name'], 'currentPrice': menu['currentPrice'],
                       'originalPrice': menu['originalPrice'], 'kcal': menu.get('kcal'),
                       'cat': menu['cat'].replace('\n', ' '),
                       'discount': round((1 - menu['currentPrice'] / menu['originalPrice']) * 100) if off else None,
                       'image': menu.get('image')}
    if nut:
        out['nutrition'] = {'kcal': nut.get('kcal'), 'protein': nut.get('protein'), 'fat': nut.get('fat'),
                           'carb': nut.get('carb'), 'sodium': nut.get('sodium'), 'calcium': nut.get('calcium')}
    out['points'] = [{'spuName': p['spuName'], 'point': p['point'], 'yuan': _yuan(p['selling'])} for p in pts[:5]]
    out['hint'] = '免费领取的优惠券价值通常高于积分兑换，建议先领券再考虑积分。'
    if not menu and not nut:
        out['message'] = '营养库与门店菜单均无「%s」，可尝试更短的关键词' % q
    return out


def cart_summary(seed, cart):
    ks = list(cart.keys())
    if not ks:
        return {'count': 0, 'total': 0.0, 'saved': 0.0}
    total = sum(seed['menu'][k]['currentPrice'] * q for k, q in cart.items() if k in seed['menu'])
    saved = sum((seed['menu'][k]['originalPrice'] - seed['menu'][k]['currentPrice']) * q
                for k, q in cart.items() if k in seed['menu'] and seed['menu'][k]['originalPrice'] > seed['menu'][k]['currentPrice'])
    n = sum(cart.values())
    return {'count': n, 'total': round(total, 1), 'saved': round(saved, 1)}


def menu_list(seed, cat='全部', q='', sort=None):
    base = seed['menuGlobalOrder'] if cat == '全部' else next((c['codes'] for c in seed['menuOrder'] if c['name'] == cat), [])
    items = [dict(code=c, **seed['menu'][c]) for c in base if c in seed['menu']]
    if q:
        q = q.lower()
        items = [m for m in items if q in m['name'].lower() or any(q in t.lower() for t in m.get('tags', []))]
    if sort == 'price':
        items.sort(key=lambda m: m['currentPrice'])
    elif sort == 'priceDesc':
        items.sort(key=lambda m: -m['currentPrice'])
    elif sort == 'save':
        items.sort(key=lambda m: -(m['originalPrice'] - m['currentPrice']) / m['originalPrice'] if m['originalPrice'] else 0)
    return {'cat': cat, 'count': len(items), 'items': [
        {'code': m['code'], 'name': m['name'], 'currentPrice': m['currentPrice'], 'originalPrice': m['originalPrice'],
         'kcal': m.get('kcal'), 'tags': m.get('tags', [])} for m in items]}


# ----------------------------- CLI -----------------------------

def _parse_cart(s):
    cart = {}
    for part in (s or '').split(','):
        part = part.strip()
        if not part:
            continue
        code, _, q = part.partition(':')
        cart[code.strip()] = int(q) if q else 1
    return cart


def main():
    ap = argparse.ArgumentParser(description='麦麦智配决策引擎')
    ap.add_argument('--seed', help='seed-data.json 路径（默认自动探测）')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('kcal', help='热量配餐')
    p.add_argument('--target', type=int, default=800)
    p.add_argument('--tol', type=float, default=0.2)
    p.add_argument('--sort', choices=['per', 'price'], default='per')
    p.add_argument('--top', type=int, default=6)

    p = sub.add_parser('deal', help='优惠最大化')
    p.add_argument('--cart', required=True, help='code:qty,code:qty')
    p.add_argument('--account', type=float, default=None)

    p = sub.add_parser('advise', help='点单建议')
    p.add_argument('--people', type=int, default=1)
    p.add_argument('--maxd', type=int, default=1500)
    p.add_argument('--tp', choices=['walk', 'bike', 'metro', 'car'], default='walk')
    p.add_argument('--mode', type=int, default=1, choices=[1, 2, 5])

    p = sub.add_parser('points', help='积分当钱花')
    p.add_argument('--account', type=float, default=None)

    p = sub.add_parser('search', help='食物查询')
    p.add_argument('--q', required=True)

    p = sub.add_parser('cart', help='购物车结算')
    p.add_argument('--cart', required=True, help='code:qty,code:qty')

    p = sub.add_parser('menu', help='菜单浏览')
    p.add_argument('--cat', default='全部')
    p.add_argument('--q', default='')
    p.add_argument('--sort', choices=['price', 'priceDesc', 'save'], default=None)

    args = ap.parse_args()
    seed = load_seed(args.seed)
    if args.cmd == 'kcal':
        out = plan_kcal(seed, args.target, args.tol, args.sort, args.top)
    elif args.cmd == 'deal':
        out = calc_best(seed, _parse_cart(args.cart), args.account)
    elif args.cmd == 'advise':
        out = advise(seed, args.people, args.maxd, args.tp, args.mode)
    elif args.cmd == 'points':
        out = points_info(seed, args.account)
    elif args.cmd == 'search':
        out = search(seed, args.q)
    elif args.cmd == 'cart':
        out = cart_summary(seed, _parse_cart(args.cart))
    elif args.cmd == 'menu':
        out = menu_list(seed, args.cat, args.q, args.sort)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
