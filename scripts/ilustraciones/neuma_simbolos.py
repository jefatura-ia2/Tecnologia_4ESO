from lib import *

AIR = C["air"]


def compresor(s, x, y):
    s.circle(x, y, 26, fill="white", stroke=C["ink"], sw=2.5)
    s.path(f"M{x},{y-18} L{x-12},{y+4} L{x+12},{y+4} Z", C["ink"], 1.5, C["ink"])
    s.line(x, y + 26, x, y + 40, C["ink"], 2)
    s.text(x, y + 58, "Compresor", 12, C["ink"], "middle", "bold")
    return (x + 26, y)


def frl(s, x, y):
    """Unidad de acondicionamiento simplificada (filtro + regulador + manómetro)."""
    s.rect(x, y - 30, 120, 60, fill="white", stroke=C["ink"], sw=2, rx=4)
    s.path(f"M{x+30},{y-20} L{x+45},{y} L{x+30},{y+20} L{x+15},{y} Z", C["ink"], 2)      # filtro
    s.line(x + 15, y, x + 45, y, C["ink"], 1.5, "3,3")
    s.rect(x + 58, y - 18, 24, 36, fill="white", stroke=C["ink"], sw=2)                   # regulador
    s.arrow(x + 60, y + 14, x + 80, y - 14, C["ink"], 1.5)
    s.circle(x + 102, y - 2, 11, fill="white", stroke=C["ink"], sw=2)                      # manómetro
    s.arrow(x + 102, y + 2, x + 108, y - 8, C["ink"], 1.2)
    s.text(x + 60, y + 50, "Unidad de", 12, C["ink"], "middle", "bold")
    s.text(x + 60, y + 66, "acondicionamiento", 12, C["ink"], "middle", "bold")
    return (x, y), (x + 120, y)


def valve32(s, x, y, a=56, label="EV1", tag="3/2 NC 12 V"):
    """Electroválvula 3/2 NC, solenoide a la izquierda, muelle a la derecha.
    El cuadro derecho (reposo) es el conectado a las vías. Devuelve vías {2, 1, 3}."""
    L, R = x, x + a
    s.rect(L, y, a, a, fill="white", stroke=C["ink"], sw=2)
    s.rect(R, y, a, a, fill="white", stroke=C["ink"], sw=2)
    # cuadro izquierdo (activada): 1 → 2, 3 bloqueada
    s.arrow(L + a * 0.25, y + a, L + a * 0.5, y + 4, C["ink"], 1.8)
    s.line(L + a * 0.75, y + a, L + a * 0.75, y + a - 12, C["ink"], 2)
    s.line(L + a * 0.75 - 7, y + a - 12, L + a * 0.75 + 7, y + a - 12, C["ink"], 2)
    # cuadro derecho (reposo): 2 → 3 escape, 1 bloqueada
    s.arrow(R + a * 0.5, y + 4, R + a * 0.75, y + a, C["ink"], 1.8)
    s.line(R + a * 0.25, y + a, R + a * 0.25, y + a - 12, C["ink"], 2)
    s.line(R + a * 0.25 - 7, y + a - 12, R + a * 0.25 + 7, y + a - 12, C["ink"], 2)
    # solenoide
    s.rect(L - 22, y + a * 0.25, 22, a * 0.5, fill="white", stroke=C["ink"], sw=2)
    s.line(L - 22, y + a * 0.75, L, y + a * 0.25, C["ink"], 1.5)
    # muelle
    zz = [(R + a, y + a / 2)]
    for i in range(7):
        zz.append((R + a + 4 + i * 4, y + a / 2 + (-9 if i % 2 == 0 else 9)))
    zz.append((R + a + 32, y + a / 2))
    s.poly(zz, C["ink"], 1.8)
    # vías (en el cuadro de reposo)
    p2, p1, p3 = (R + a * 0.5, y), (R + a * 0.25, y + a), (R + a * 0.75, y + a)
    s.line(p2[0], p2[1], p2[0], p2[1] - 14, C["ink"], 2)
    s.line(p1[0], p1[1], p1[0], p1[1] + 14, C["ink"], 2)
    s.line(p3[0], p3[1], p3[0], p3[1] + 10, C["ink"], 2)
    s.path(f"M{p3[0]-8},{p3[1]+10} L{p3[0]+8},{p3[1]+10} L{p3[0]},{p3[1]+22} Z", C["ink"], 1.5, "white")  # escape
    s.text(p2[0] + 6, p2[1] - 4, "2", 11, C["muted"])
    s.text(p1[0] - 12, p1[1] + 14, "1", 11, C["muted"])
    s.text(p3[0] + 10, p3[1] + 14, "3", 11, C["muted"])
    s.text(L - 26, y + a / 2 + 4, label, 13, C["orange"], "end", "bold")
    s.text(L - 26, y + a / 2 + 22, tag, 11, C["muted"], "end")
    return {"2": (p2[0], p2[1] - 14), "1": (p1[0], p1[1] + 14), "3": p3}


def cylinder(s, x, y, w=220, h=60, piston=0.35, single=False, rod_ext=90):
    """Cilindro horizontal: tapa trasera a la izquierda. Devuelve tomas y extremo del vástago."""
    s.rect(x, y, w, h, fill="white", stroke=C["ink"], sw=2.5)
    px = x + w * piston
    s.rect(px - 5, y + 2, 10, h - 4, fill=C["ink"], stroke=C["ink"], sw=1)
    s.rect(px + 5, y + h / 2 - 6, w - (px - x) + rod_ext - 5, 12, fill="#e5e7eb", stroke=C["ink"], sw=2)
    if single:
        zz = [(px + 6, y + h / 2)]
        n = 9
        span = x + w - px - 10
        for i in range(n):
            zz.append((px + 10 + i * span / n, y + (8 if i % 2 == 0 else h - 8)))
        zz.append((x + w - 2, y + h / 2))
        s.poly(zz, C["ink"], 1.5)
    rear = (x + 14, y + h)
    front = (x + w - 14, y + h)
    s.line(rear[0], rear[1], rear[0], rear[1] + 14, C["ink"], 2)
    if not single:
        s.line(front[0], front[1], front[0], front[1] + 14, C["ink"], 2)
    tip = (px + 5 + w - (px - x) + rod_ext - 5, y + h / 2)
    return {"rear": (rear[0], rear[1] + 14), "front": (front[0], front[1] + 14), "tip": tip}


def air(s, pts):
    s.poly(pts, AIR, 3.5)


