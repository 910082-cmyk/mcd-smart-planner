#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管道测试：build_menu_order.py 对当前 seed-data.json 必须幂等。

做法：把 seed-data.json 复制到临时文件，将模块的 BASE 指向副本后真实执行
main()（不碰仓库里的原文件），再断言：
  1. OFFICIAL 官方分类恰为 15 类，名称与顺序符合麦当劳官方菜单；
  2. 重建产物中每个分类的编码全部存在于 menu（无缺失 code）；
  3. menuGlobalOrder 去重后全覆盖 121 项餐品；
  4. 重建产物与仓库中的 seed-data.json 完全一致（幂等）——
     防止「脚本改了、数据没重建」导致的页面与管道漂移。

用法：python tests/test_data_pipeline.py
"""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
SEED = os.path.join(ROOT, 'data', 'seed-data.json')
SCRIPT = os.path.join(ROOT, 'scripts', 'build_menu_order.py')

OFFICIAL_NAMES = [
    '人气热卖', '精选单人餐', '鸡肉汉堡/卷', '小食拼盘/多人餐', '蘸酱炸鸡',
    '随心配 1+1', '大堡口福 单人餐', '巨无霸 牛鱼肉堡', '安格斯MAX 厚牛堡',
    '炸鸡', '小食甜品/其他', '开心乐园', '麦咖啡', '500 大卡套餐', '饮品',
]

passed, failed = 0, 0


def ok(cond, label, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print('  ✓ ' + label)
    else:
        failed += 1
        print('  ✗ ' + label + ((' —— ' + detail) if detail else ''))


def load_module(path):
    spec = importlib.util.spec_from_file_location('build_menu_order', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    with io.open(SEED, encoding='utf-8') as f:
        committed = json.load(f)

    print('[官方分类定义]')
    mod = load_module(SCRIPT)
    ok(len(mod.OFFICIAL) == 15, 'OFFICIAL 恰为 15 个官方分类', '实际 %d' % len(mod.OFFICIAL))
    names = [n for n, _ in mod.OFFICIAL]
    ok(names == OFFICIAL_NAMES, '分类名称与顺序符合官方菜单',
       '不一致: %s' % [n for n in names if n not in OFFICIAL_NAMES])

    print('[管道执行（临时副本，不碰原文件）]')
    tmpdir = tempfile.mkdtemp(prefix='mcd-pipeline-')
    try:
        tmp_seed = os.path.join(tmpdir, 'seed-data.json')
        shutil.copy2(SEED, tmp_seed)
        mod.BASE = tmp_seed  # 重定向输出到副本
        mod.main()

        with io.open(tmp_seed, encoding='utf-8') as f:
            rebuilt = json.load(f)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    menu = rebuilt['menu']
    order = rebuilt['menuOrder']
    ok(len(order) == 15, '重建产物含 15 个分类', '实际 %d' % len(order))
    missing = [(c['name'], code) for c in order for code in c['codes'] if code not in menu]
    ok(not missing, '分类编码全部存在于菜单（无缺失 code）', '缺失 %d 个: %s' % (len(missing), missing[:5]))
    empty = [c['name'] for c in order if not c['codes']]
    ok(not empty, '每个分类都非空', '空分类: %s' % empty)

    gl = rebuilt['menuGlobalOrder']
    ok(len(gl) == len(set(gl)), 'menuGlobalOrder 无重复编码')
    ok(set(gl) == set(menu.keys()), 'menuGlobalOrder 全覆盖菜单（%d 项）' % len(menu),
       '差集 %d' % len(set(menu.keys()) - set(gl)))

    print('[幂等性（防脚本与数据漂移）]')
    same_order = committed.get('menuOrder') == rebuilt.get('menuOrder')
    same_global = committed.get('menuGlobalOrder') == rebuilt.get('menuGlobalOrder')
    ok(same_order and same_global,
       '重建产物与仓库 seed-data.json 的 menuOrder / menuGlobalOrder 完全一致',
       'menuOrder %s / menuGlobalOrder %s' % ('一致' if same_order else '不一致',
                                             '一致' if same_global else '不一致'))

    print('\n========================================')
    print('通过 %d 项，失败 %d 项' % (passed, failed))
    if failed:
        sys.exit(1)
    print('[OK] 数据管道测试全部通过')


if __name__ == '__main__':
    main()
