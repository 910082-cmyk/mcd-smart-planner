# -*- coding: utf-8 -*-
"""
纯 Python 的 SVG path 光栅化器（环境无 PIL / cairosvg / matplotlib）。
用途：把麦当劳 logo 的 path 真的画出来，肉眼确认形状，而不是靠读代码猜。
输出：终端 ASCII 预览 + PNG 文件。
"""
import re, sys, zlib, struct, math, io, os

# ---------- 1. 解析 path ----------
TOKEN = re.compile(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?')

def parse_path(d):
    toks = TOKEN.findall(d)
    i = 0
    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v
    subpaths, cur = [], []
    x = y = 0.0
    sx = sy = 0.0
    cmd = None
    prev_ctrl = None
    while i < len(toks):
        t = toks[i]
        if re.match(r'[A-Za-z]', t):
            cmd = t; i += 1
        if cmd is None:
            break
        rel = cmd.islower()
        c = cmd.upper()
        if c == 'M':
            px, py = (x, y) if rel else (0.0, 0.0)
            x = px + num(); y = py + num()
            if cur: subpaths.append(cur)
            cur = [(x, y)]
            sx, sy = x, y
            cmd = 'l' if rel else 'L'   # 后续成对坐标视为 L
            prev_ctrl = None
        elif c == 'L':
            px, py = (x, y) if rel else (0.0, 0.0)
            x = px + num(); y = py + num()
            cur.append((x, y)); prev_ctrl = None
        elif c == 'H':
            px = x if rel else 0.0
            x = px + num()
            cur.append((x, y)); prev_ctrl = None
        elif c == 'V':
            py = y if rel else 0.0
            y = py + num()
            cur.append((x, y)); prev_ctrl = None
        elif c == 'C':
            px, py = (x, y) if rel else (0.0, 0.0)
            x1 = px + num(); y1 = py + num()
            x2 = px + num(); y2 = py + num()
            x3 = px + num(); y3 = py + num()
            cur.extend(cubic(x, y, x1, y1, x2, y2, x3, y3))
            prev_ctrl = (x2, y2); x, y = x3, y3
        elif c == 'S':
            px, py = (x, y) if rel else (0.0, 0.0)
            x2 = px + num(); y2 = py + num()
            x3 = px + num(); y3 = py + num()
            if prev_ctrl:
                x1, y1 = 2*x - prev_ctrl[0], 2*y - prev_ctrl[1]
            else:
                x1, y1 = x, y
            cur.extend(cubic(x, y, x1, y1, x2, y2, x3, y3))
            prev_ctrl = (x2, y2); x, y = x3, y3
        elif c == 'Q':
            px, py = (x, y) if rel else (0.0, 0.0)
            x1 = px + num(); y1 = py + num()
            x2 = px + num(); y2 = py + num()
            cur.extend(quad(x, y, x1, y1, x2, y2))
            prev_ctrl = (x1, y1); x, y = x2, y2
        elif c == 'T':
            px, py = (x, y) if rel else (0.0, 0.0)
            x2 = px + num(); y2 = py + num()
            if prev_ctrl:
                x1, y1 = 2*x - prev_ctrl[0], 2*y - prev_ctrl[1]
            else:
                x1, y1 = x, y
            cur.extend(quad(x, y, x1, y1, x2, y2))
            prev_ctrl = (x1, y1); x, y = x2, y2
        elif c in ('Z',):
            if cur:
                cur.append((sx, sy))
                subpaths.append(cur); cur = []
            x, y = sx, sy
            prev_ctrl = None
        else:
            raise ValueError('不支持的指令: ' + cmd)
    if cur: subpaths.append(cur)
    return subpaths

def cubic(x0, y0, x1, y1, x2, y2, x3, y3, n=40):
    pts = []
    for k in range(1, n+1):
        t = k / n; u = 1 - t
        px = u*u*u*x0 + 3*u*u*t*x1 + 3*u*t*t*x2 + t*t*t*x3
        py = u*u*u*y0 + 3*u*u*t*y1 + 3*u*t*t*y2 + t*t*t*y3
        pts.append((px, py))
    return pts

def quad(x0, y0, x1, y1, x2, y2, n=24):
    pts = []
    for k in range(1, n+1):
        t = k / n; u = 1 - t
        pts.append((u*u*x0 + 2*u*t*x1 + t*t*x2, u*u*y0 + 2*u*t*y1 + t*t*y2))
    return pts

# ---------- 2. 光栅化 ----------
def edges_of(subpaths):
    es = []
    for sp in subpaths:
        for a, b in zip(sp, sp[1:]):
            if a[1] != b[1]:
                es.append((a[0], a[1], b[0], b[1]))
    return es

def crossings(es, y):
    xs = []
    for x1, y1, x2, y2 in es:
        if (y1 <= y < y2) or (y2 <= y < y1):
            t = (y - y1) / (y2 - y1)
            xs.append((x1 + t*(x2 - x1), 1 if y2 > y1 else -1))
    xs.sort()
    return xs

def fill_rule_winding(xs, rule):
    """返回该扫描线上的填充区间 [(x0,x1), ...]"""
    out = []
    if rule == 'evenodd':
        for i in range(0, len(xs)-1, 2):
            out.append((xs[i][0], xs[i+1][0]))
    else:
        w = 0
        for i in range(len(xs)-1):
            w += xs[i][1]
            if w != 0:
                out.append((xs[i][0], xs[i+1][0]))
    return out

def render(subpaths, W, H, vb, rule='nonzero', supersample=2):
    x0, y0, vw, vh = vb
    es = edges_of(subpaths)
    sx = W / vw; sy = H / vh
    buf = bytearray(W*H)   # 覆盖率 0..255
    ss = supersample
    for row in range(H):
        yv = y0 + (row + 0.5) * vh / H
        xs = crossings(es, yv)
        if not xs:
            continue
        spans = fill_rule_winding(xs, rule)
        for a, b in spans:
            pa = int((a - x0) * sx); pb = int((b - x0) * sx)
            pa = max(0, min(W, pa)); pb = max(0, min(W, pb))
            if pb <= pa:
                # 亚像素：按小数覆盖
                fa = (a - x0) * sx; fb = (b - x0) * sx
                if int(fb) > int(fa):
                    pass
                c = int((fb - fa) * 255)
                if 0 <= int(fa) < W:
                    buf[row*W + int(fa)] = min(255, buf[row*W + int(fa)] + min(255, c))
                continue
            buf[row*W+pa:row*W+pb] = b'\xff' * (pb - pa)
            # 边缘抗锯齿（左右各一像素）
            fa = (a - x0) * sx; fb = (b - x0) * sx
            cl = int((math.ceil(fa) - fa) * 255)
            if 0 <= pa-1 < W and cl: buf[row*W+pa-1] = min(255, buf[row*W+pa-1] + cl)
            cr = int((fb - math.floor(fb)) * 255)
            if 0 <= pb < W and cr: buf[row*W+pb] = min(255, buf[row*W+pb] + cr)
    return buf

# ---------- 3. PNG 编码 ----------
def write_png(path, W, H, buf, fg, bg):
    raw = bytearray()
    fr, fg_, fb = fg
    br, bg_, bb = bg
    for row in range(H):
        raw.append(0)
        for col in range(W):
            a = buf[row*W+col] / 255.0
            raw.append(int(br + (fr-br)*a))
            raw.append(int(bg_ + (fg_-bg_)*a))
            raw.append(int(bb + (fb-bb)*a))
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag+data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)

# ---------- 4. ASCII 预览 ----------
def ascii_preview(subpaths, vb, cols=104, rows=52, rule='nonzero'):
    x0, y0, vw, vh = vb
    es = edges_of(subpaths)
    lines = []
    for r in range(rows):
        yv = y0 + (r + 0.5) * vh / rows
        xs = crossings(es, yv)
        spans = fill_rule_winding(xs, rule) if xs else []
        line = [' '] * cols
        for a, b in spans:
            ca = int((a - x0) / vw * cols); cb = int((b - x0) / vw * cols)
            for c in range(max(0, ca), min(cols, max(cb, ca+1))):
                line[c] = '#'
        lines.append(''.join(line))
    return '\n'.join(lines)

# ---------- 5. 主流程 ----------
def render_svg_path(d, vb, out_prefix, size=320):
    for rule in ('nonzero', 'evenodd'):
        sp = parse_path(d)
        buf = render(sp, size, size, vb, rule)
        write_png(f'{out_prefix}_{rule}.png', size, size, buf, (255, 199, 44), (255, 255, 255))
    sp = parse_path(d)
    return ascii_preview(sp, vb, rule='nonzero')

if __name__ == '__main__':
    svg = io.open(sys.argv[1], encoding='utf-8').read()
    d = re.search(r'd="([^"]+)"', svg).group(1)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).replace(',', ' ').split()]
    out = sys.argv[2]
    print(render_svg_path(d, vb, out))
    print('\nPNG 已输出: %s_nonzero.png / %s_evenodd.png' % (out, out))
