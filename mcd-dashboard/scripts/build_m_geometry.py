# -*- coding: utf-8 -*-
"""
麦当劳金色双拱门 M：官方 SVG 路径 -> 挤出 3D 预览图。

关键认知（本次调试的结论）：
  - simple-icons 的麦当劳路径是**单条闭合子路径**，它画的 M 内侧通道在底部是敞开的，
    因此整个图形是单连通区域 —— 没有孔洞，路径本身就是完整边界。
  - 之前走「掩膜 -> 连通标记 -> 边界追踪」是绕远路：阈值化会把抗锯齿边缘变成
    噪声边界，追踪算法在拱顶薄盖处必错。直接用路径多段线即可，且是亚像素精确的。
  - 用「路径回填 vs 原始掩膜」的像素级比对来验证路径正确性（容差 3%）。

输出：
  assets/m-contours.json   轮廓数据（y-up、居中、宽 10 单位，无孔洞）
  assets/m-3d-preview.png  软渲染预览图 1280x520
"""
import re, sys, zlib, struct, math, io, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_svg import parse_path  # 复用已验证的路径解析器（M/L/C/S/Q/T/A/Z -> 多段线）

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(ROOT, 'assets', 'mcd-logo.svg')

# ---------------------------------------------------------------- 位图光栅化（仅用于验证）
def rasterize(subpaths, vb, N=560):
    x0, y0, vw, vh = vb
    es = []
    for sp in subpaths:
        for a, b in zip(sp, sp[1:]):
            if a[1] != b[1]:
                es.append((a[0], a[1], b[0], b[1], 1 if b[1] > a[1] else -1))
    buf = [[0.0] * N for _ in range(N)]
    for row in range(N):
        yv = y0 + (row + 0.5) * vh / N
        xs = []
        for x1, y1, x2, y2, d in es:
            if (y1 <= yv < y2) or (y2 <= yv < y1):
                xs.append((x1 + (yv - y1) / (y2 - y1) * (x2 - x1), d))
        xs.sort()
        w, spans = 0, []
        for i in range(len(xs) - 1):
            w += xs[i][1]
            if w != 0:
                spans.append((xs[i][0], xs[i + 1][0]))
        for a, b in spans:
            fa, fb = (a - x0) / vw * N, (b - x0) / vw * N
            if fb - fa >= 1:
                for c in range(int(math.ceil(fa)), int(math.floor(fb))):
                    buf[row][c] = 255.0
                if int(math.ceil(fa)) - 1 >= 0:
                    buf[row][int(math.ceil(fa)) - 1] = max(buf[row][int(math.ceil(fa)) - 1],
                                                          (math.ceil(fa) - fa) * 255)
                if int(math.floor(fb)) < N:
                    buf[row][int(math.floor(fb))] = max(buf[row][int(math.floor(fb))],
                                                        (fb - math.floor(fb)) * 255)
            else:
                c = int(fa)
                if 0 <= c < N:
                    buf[row][c] = max(buf[row][c], min(255.0, (fb - fa) * 255))
    return buf

def poly_fill(contours, N):
    """nonzero 规则填充闭合多段线，用于回填验证。"""
    m = [[False] * N for _ in range(N)]
    es = []
    for pts in contours:
        for a, b in zip(pts, pts[1:] + pts[:1]):
            if a[1] != b[1]:
                es.append((a[0], a[1], b[0], b[1], 1 if b[1] > a[1] else -1))
    for r in range(N):
        y = r + 0.5
        xs = []
        for x1, y1, x2, y2, d in es:
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append((x1 + (y - y1) / (y2 - y1) * (x2 - x1), d))
        xs.sort()
        w = 0
        for i in range(len(xs) - 1):
            w += xs[i][1]
            if w != 0:
                for c in range(int(math.ceil(xs[i][0])), int(math.floor(xs[i + 1][0]))):
                    if 0 <= c < N:
                        m[r][c] = True
    return m

def shoelace(pts):
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return s / 2

def normalize(outer, target_w=10.0):
    """y 翻转成 y-up，按包围盒中心居中，缩放到目标宽度；保证外轮廓 CCW。"""
    xs = [p[0] for p in outer]; ys = [p[1] for p in outer]
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2
    s = target_w / max(max(xs) - min(xs), max(ys) - min(ys))
    o = [((x - cx) * s, -(y - cy) * s) for x, y in outer]  # y-up
    if shoelace(o) < 0:
        o.reverse()
    return o

# ---------------------------------------------------------------- PNG 输出（全彩）
def write_png(path, W, H, pix):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(pix[y * W * 3:(y + 1) * W * 3])
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + \
               struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 6))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)

# ---------------------------------------------------------------- 软渲染 3D
def rot(p, ay, ax):
    x, y, z = p
    x, z = x * math.cos(ay) + z * math.sin(ay), z * math.cos(ay) - x * math.sin(ay)
    y, z = y * math.cos(ax) - z * math.sin(ax), z * math.cos(ax) + y * math.sin(ax)
    return (x, y, z)

def render_preview(outer, out_path, W=1280, H=460, depth=1.15, ay=-0.30, ax=0.11):
    """把轮廓挤出成带倒角的 3D M，正交投影 + z-buffer 硬深度 + 平面着色。

    不用 painter 排序：M 是凹形（V 缺口 + 双通道），四边形深度序会错，
    产生贯穿画面的条纹。z-buffer 逐像素取最近面，结果与真实光栅化一致。
    """
    # ---- 背景：品牌红（贴近页面实色 #DA291C）+ M 后方金色辉光 + 地面光池 ----
    cxp, cyp = W * 0.66, H * 0.46
    bg = [0.0] * (W * H * 3)
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - cxp) / (W * .80), (y - cyp) / (H * .86))
            t = min(1.0, d) ** 1.3
            r = 0xE4 + (0xC6 - 0xE4) * t
            g = 0x30 + (0x20 - 0x30) * t
            b = 0x22 + (0x17 - 0x22) * t
            # M 后方辉光
            glow = max(0.0, 1.0 - math.hypot((x - cxp) / (W * .24), (y - cyp) / (H * .38)) * 1.10) ** 2.2
            # 地面光池（M 底部宽而柔的暖光）
            pool = max(0.0, 1.0 - math.hypot((x - cxp) / (W * .34), (y - (cyp + H * .27)) / (H * .16)) * 1.05) ** 1.8
            i = (y * W + x) * 3
            bg[i] = min(255, r + glow * 56 + pool * 46)
            bg[i + 1] = min(255, g + glow * 32 + pool * 24)
            bg[i + 2] = min(255, b + glow * 5 + pool * 6)
    # ---- 地面软阴影（先画进背景）----
    SC0 = (H * 0.84) / 8.75
    OX0, OY0 = W * 0.665, H * 0.52
    shx, shy = int(OX0), int(OY0 + 2.62 * SC0)
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - shx) / (3.0 * SC0), (y - shy) / (0.55 * SC0))
            if d < 1.0:
                a = (1.0 - d) ** 2 * 0.34
                i = (y * W + x) * 3
                bg[i] *= (1 - a); bg[i + 1] *= (1 - a); bg[i + 2] *= (1 - a)

    # ---- 三环挤出：front(+d/2, 1.0) / mid(0, .962) / back(-d/2, .925) —— 倒角 ----
    rings = [[(x * sc, y * sc, zi) for x, y in outer] for zi, sc in
             ((depth / 2, 1.0), (0.0, 0.962), (-depth / 2, 0.925))]

    SC = (H * 0.84) / 8.75
    OX, OY = W * 0.665, H * 0.52
    def proj(p):
        x, y, z = rot(p, ay, ax)
        return (OX + x * SC, OY - y * SC, z)

    GOLD = (255, 199, 44)
    def shade(n, base=GOLD, amb=0.42):
        L1 = (-0.52, 0.66, 0.54); L2 = (0.78, 0.18, 0.42)
        nL = math.sqrt(sum(c * c for c in n)) or 1
        n = tuple(c / nL for c in n)
        d1 = max(0.0, sum(n[i] * L1[i] for i in range(3)))
        d2 = max(0.0, sum(n[i] * L2[i] for i in range(3)))
        h = (L1[0], L1[1], L1[2] + 1.0)
        hL = math.sqrt(sum(c * c for c in h)) or 1
        h = tuple(c / hL for c in h)
        s = max(0.0, sum(n[i] * h[i] for i in range(3))) ** 30
        inten = amb + d1 * 0.72 + d2 * 0.22
        return tuple(min(255, base[i] * inten + 255 * s * 0.55) for i in range(3))

    # ---- 组装面片（旋转后的 3D 屏幕坐标：x, y, z=深度，大者近）----
    faces = []
    faces.append(([proj(p) for p in rings[2]], (205, 150, 28)))   # back 暗金
    for band in range(2):
        for i in range(len(outer)):
            j = (i + 1) % len(outer)
            a = rings[band][i]; b = rings[band][j]
            c2 = rings[band + 1][j]; d2 = rings[band + 1][i]
            u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
            v = (c2[0] - a[0], c2[1] - a[1], c2[2] - a[2])
            nrm = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
            faces.append(([proj(a), proj(b), proj(c2), proj(d2)], shade(nrm)))
    # 漂浮粒子（作为面向相机的小菱形面片，参与深度测试）
    import random
    random.seed(7)
    parts = []
    for i in range(16):
        px = -7.5 + random.random() * 15
        py = -2.6 + random.random() * 5.6
        pz = -3.5 + random.random() * 6
        if abs(px) < 2.6 and abs(py) < 2.8:
            continue
        s = 2.5 + random.random() * 6
        a = 0.45 + random.random() * 0.4
        p = proj((px, py, pz))
        parts.append(([(p[0], p[1] - s, p[2]), (p[0] + s, p[1], p[2]),
                        (p[0], p[1] + s, p[2]), (p[0] - s, p[1], p[2])],
                       tuple(int(c * a) for c in (255, 214, 110))))

    # ---- z-buffer 光栅化（2x2 超采样抗锯齿）----
    zbuf = [-1e9] * (W * H)
    acc = [[0.0, 0.0, 0.0, 0.0] for _ in range(W * H)]
    tagbuf = [0] * (W * H)  # 1=正面端盖（用于纵向金属渐变）

    def raster(pts, color, tag=0):
        n = len(pts)
        for i in range(1, n - 1):  # 三角扇形
            tri = (pts[0], pts[i], pts[i + 1])
            (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = tri
            det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
            if abs(det) < 1e-12:
                continue
            minx = int(max(0, math.floor(min(x1, x2, x3))))
            maxx = int(min(W - 1, math.ceil(max(x1, x2, x3))))
            miny = int(max(0, math.floor(min(y1, y2, y3))))
            maxy = int(min(H - 1, math.ceil(max(y1, y2, y3))))
            for py in range(miny, maxy + 1):
                for px in range(minx, maxx + 1):
                    for sy in (0.25, 0.75):
                        for sx in (0.25, 0.75):
                            x, y = px + sx, py + sy
                            w1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
                            w2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
                            w3 = 1 - w1 - w2
                            if w1 < -0.001 or w2 < -0.001 or w3 < -0.001:
                                continue
                            z = w1 * z1 + w2 * z2 + w3 * z3
                            idx = py * W + px
                            if z > zbuf[idx] + 1e-6:
                                zbuf[idx] = z
                                acc[idx][0] = color[0]; acc[idx][1] = color[1]
                                acc[idx][2] = color[2]; acc[idx][3] = 1.0
                                tagbuf[idx] = tag

    for pts, colr in parts + faces:  # 粒子也参与深度，远的被 M 挡住
        raster(pts, colr, 0)
    raster([proj(p) for p in rings[0]], (255, 209, 78), 1)  # 正面端盖最后画并标记

    # ---- 合成（正面端盖叠加纵向金属渐变：上亮下柔）----
    out = bytearray(W * H * 3)
    for i in range(W * H):
        a = acc[i]
        bi = i * 3
        if a[3] > 0:
            r, g, b = a[0], a[1], a[2]
            if tagbuf[i] == 1:
                f = 1.13 - 0.16 * (i // W) / H  # 顶部 +13%，底部 -3%
                r *= f; g *= f; b *= f
            out[bi] = int(min(255, r)); out[bi + 1] = int(min(255, g)); out[bi + 2] = int(min(255, b))
        else:
            out[bi] = int(bg[bi]); out[bi + 1] = int(bg[bi + 1]); out[bi + 2] = int(bg[bi + 2])
    write_png(out_path, W, H, out)

# ---------------------------------------------------------------- 主流程
def main():
    svg = io.open(SVG, encoding='utf-8').read()
    d = re.search(r'd="([^"]+)"', svg).group(1)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).replace(',', ' ').split()]

    sp = parse_path(d)
    print('子路径数: %d（单条闭合轮廓 => 路径即边界，无需提取孔洞）' % len(sp))
    outline = [p for p in sp[0]]
    # 去掉闭合重复点
    if outline[0] == outline[-1]:
        outline = outline[:-1]
    print('轮廓点数: %d（贝塞尔已扁平化）' % len(outline))

    # ---- 验证：路径回填 vs 原始掩膜 ----
    N = 560
    buf = rasterize(sp, vb, N=N)
    orig = [[buf[y][x] >= 110 for x in range(N)] for y in range(N)]
    x0, y0, vw, vh = vb
    s = N / vw
    scaled = [[(x - x0) * s, (y - y0) * s] for x, y in outline]  # viewBox -> 像素坐标
    back = poly_fill([scaled], N)
    diff = sum(1 for y in range(N) for x in range(N) if back[y][x] != orig[y][x])
    area = sum(1 for y in range(N) for x in range(N) if orig[y][x])
    print('回填验证: 差异 %d / %d 像素 (%.2f%%)' % (diff, area, diff / max(area, 1) * 100))
    if diff > area * 0.03:
        print('!! 路径回填与掩膜差异过大，终止')
        sys.exit(1)

    o = normalize(outline, target_w=10.0)
    print('归一化: 宽 10 单位 · %d 点 · 面积 %.2f' % (len(o), abs(shoelace(o))))

    json_path = os.path.join(ROOT, 'assets', 'm-contours.json')
    with io.open(json_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps({'outer': [[round(x, 4), round(y, 4)] for x, y in o],
                            'holes': [], 'unit': 'y-up, centered, width=10'},
                           ensure_ascii=False))
    print('轮廓数据 -> %s' % json_path)

    png = os.path.join(ROOT, 'assets', 'm-3d-preview.png')
    render_preview(o, png)
    print('预览图 -> %s' % png)

if __name__ == '__main__':
    main()
