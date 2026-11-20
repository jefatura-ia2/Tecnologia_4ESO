"""Letrero de aulas TIPO BANDERA - generador paramétrico de STL (mm)  -  v5.
v5: hueco central del carril RECTANGULAR (19 x 18) para ESP32-C3 SuperMini + reductor 12->5 V, ventana USB-C en el extremo.
(v4: revisión tras la 1ª impresión de prueba)
Ejes: Y = a lo largo del carril (perpendicular a la pared), X = ancho, Z = altura.
Carril: extremo cercano a la pared en Y=0 (la espiga sale hacia -Y); base de pared en Y<0.
ORIENTACIÓN DE IMPRESIÓN (sin soportes):  carril -> cara inferior (Z=0) sobre la cama;
base -> cara inferior (Z=-15) sobre la cama (cavidad hacia arriba);  letras -> tumbadas sobre su cara (X=-7,5);  tapas -> planas.
Requiere: pip install trimesh manifold3d shapely mapbox_earcut numpy

CAMBIOS v4 respecto a v3 (según fotos y croquis del 20-11-2026):
 1) Alojamiento LED rehecho con las cotas del croquis: rebaje de la tapa 15 mm de ancho, bolsillo de la placa 10 mm,
    taladros de fijación a 8 mm del borde (2 mm del otro).  Placa WS2812 de 8 LED de 53 x 10 mm (antes 68 x 7: no coincidía).
 2) Tapa de PLA translúcido: 14,7 x 74,7 x 2 mm, esquinas redondeadas, encaja a ras en el rebaje.
 3) Conectores Molex: medidas reales aproximadas (las de v3 eran ~5 mm demasiado grandes -> el conector bailaba).
    Alojamientos con nervios de aplastamiento ("crush ribs") que absorben la tolerancia de la impresora.
    El conector de la base va en una cuna con pestañas a presión y tope trasero con ranura para los cables.
 4) Unión carril-base SIN HOLGURA: los brazos elásticos (que flexaban y dejaban cabecear el carril) y el hueco
    pentagonal vacío se sustituyen por una ESPIGA MACIZA pentagonal de 19 mm que rellena por completo el alojamiento
    de la base (holgura 0,15 mm por cara) y se fija con 2 tornillos M3x16 desde debajo de la base (quedan ocultos).
 5) Galgas de prueba (impresión de 10 min) para comprobar ajustes ANTES de imprimir las piezas grandes.
"""
import numpy as np, trimesh, os
from shapely.geometry import Polygon, LineString, box as sbox
from shapely.ops import unary_union
OUT = os.path.dirname(os.path.abspath(__file__))
TOL = 0.3
RX = trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0])

def B(x0,x1,y0,y1,z0,z1):
    return trimesh.creation.box(extents=[x1-x0,y1-y0,z1-z0],
        transform=trimesh.transformations.translation_matrix([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]))
def U(*m): return trimesh.boolean.union(list(m), engine="manifold")
def D(a,*m): return trimesh.boolean.difference([a,*m], engine="manifold")
def cyl_y(r,y0,y1,x,z,sec=48):
    c=trimesh.creation.cylinder(radius=r,height=y1-y0,sections=sec)
    c.apply_transform(RX); c.apply_translation([x,(y0+y1)/2,z]); return c
def cyl_x(r,x0,x1,y,z):
    c=trimesh.creation.cylinder(radius=r,height=abs(x1-x0),sections=32)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0])); c.apply_translation([(x0+x1)/2,y,z]); return c
def cyl_z(r,z0,z1,x,y,sec=32):
    c=trimesh.creation.cylinder(radius=r,height=z1-z0,sections=sec); c.apply_translation([x,y,(z0+z1)/2]); return c
def cone_z(r0,r1,z0,z1,x,y,sec=32):
    """Tronco de cono vertical (r0 en z0, r1 en z1)."""
    a=np.linspace(0,2*np.pi,sec,endpoint=False)
    v=np.vstack([np.c_[x+r0*np.cos(a),y+r0*np.sin(a),np.full(sec,z0)],np.c_[x+r1*np.cos(a),y+r1*np.sin(a),np.full(sec,z1)]])
    return trimesh.convex.convex_hull(v)
def prism_y(pts_xz,y0,y1):
    """Perfil en el plano XZ extruido a lo largo de Y entre y0 e y1."""
    P=pts_xz if isinstance(pts_xz,Polygon) else Polygon(pts_xz)
    m=trimesh.creation.extrude_polygon(P,y1-y0); m.apply_transform(RX); m.apply_translation([0,y1,0]); return m
def prism_x(pts_yz,x0,x1):
    """Perfil en el plano YZ extruido a lo largo de X entre x0 y x1."""
    P=pts_yz if isinstance(pts_yz,Polygon) else Polygon(pts_yz)
    m=trimesh.creation.extrude_polygon(P,x1-x0)
    m.apply_transform(np.array([[0,0,1,x0],[1,0,0,0],[0,1,0,0],[0,0,0,1]],float)); return m
def prism_z(pts_xy,z0,z1):
    m=trimesh.creation.extrude_polygon(Polygon(pts_xy),z1-z0); m.apply_translation([0,0,z0]); return m
def rrect(a0,b0,a1,b1,r):
    """Rectángulo con esquinas redondeadas (shapely)."""
    return sbox(a0+r,b0+r,a1-r,b1-r).buffer(r,quad_segs=8)

# ---- Carril (35 ancho x 30 alto x 200 largo) ----
RW, RH, RL = 35, 30, 200
RAD = 6.0                                    # radio de las 4 esquinas longitudinales del carril (croquis: perfil redondeado)
ROUND_PTS = list(sbox(-RW/2+RAD,RAD,RW/2-RAD,RH-RAD).buffer(RAD,quad_segs=12).exterior.coords)[:-1]
LET_H, LET_T = 120, 15
LET_W = {"E":45,"4":45,"A":60}
# Ranura de letras en T (sin cambios respecto a v3)
NECK, HEAD = 5.0, 7.5
NH, HH = 3.9, 3.8
Z_FLOOR, Z_CEIL = RH-8.0, RH-3.7
SLOT_PTS=[(-(NECK+TOL),RH+1),(NECK+TOL,RH+1),(NECK+TOL,Z_CEIL+1.0),(HEAD+TOL-1.0,Z_CEIL+1.0),(HEAD+TOL,Z_CEIL),
          (HEAD+TOL,Z_FLOOR),(-(HEAD+TOL),Z_FLOOR),(-(HEAD+TOL),Z_CEIL),(-(HEAD+TOL-1.0),Z_CEIL+1.0),(-(NECK+TOL),Z_CEIL+1.0)]
# ---- HUECO CENTRAL RECTANGULAR (v5): aloja la ESP32-C3 SuperMini y el reductor 12->5 V, además del cableado ----
#   Sección útil 19 x 18 mm (z 2..20, encima de la tapa inferior). Paredes: 2,5 mm hasta los bolsillos LED, 2 mm bajo la ranura de letras.
#   El techo es un PUENTE plano de 19 mm (se imprime sin soportes con ventilador al 100 %).
CH_W, CH_Z1 = 19.0, 20.0
ESP_W, ESP_L, ESP_T = 18.0, 22.5, 4.5        # ESP32-C3 SuperMini (PCB 22,5 x 18; alto con USB-C ~4,5)  -> MIDE LA TUYA
BUCK_W, BUCK_L, BUCK_T = 17.0, 22.0, 4.5     # reductor 12->5 V tipo MP1584 / Mini-360 (22 x 17 x 4,5) -> MIDE EL TUYO
ESP_Y1  = RL-2                               # la ESP32 va al final del carril, con el USB-C contra la pared del extremo
BUCK_Y0 = 14.0                               # el reductor va junto a la base (entrada de 12 V por el Molex)
USB_W, USB_H = 12.5, 7.0                     # ventana en el extremo libre para enchufar el cable USB-C (programar sin desmontar)
USB_ZC  = 2.0+1.0+1.6                        # eje del USB-C con la placa apoyada sobre la tapa inferior

# =====================================================================================================================
# CONECTORES MOLEX 4 polos (serie 8981, paso 5,08 mm).   >>> MIDE TUS CONECTORES CON EL CALIBRE Y CAMBIA SOLO ESTO <<<
#   CR = conector que va en el CARRIL (en la foto: el de las 4 bocas con casquillos, cuerpo ~21 mm de ancho)
#   CB = conector que va en la BASE   (el que recibe al anterior dentro de su faldón)
#   W = ancho, H = alto, L = largo de la carcasa (sin cables), CH = chaflanes de polarización (esquinas inferiores)
# =====================================================================================================================
CR_W, CR_H, CR_L, CR_CH = 21.2, 8.6, 20.0, 2.0
CB_W, CB_H, CB_L, CB_CH = 23.4, 9.6, 20.0, 2.0
C_CLR   = 0.20        # holgura por cara del alojamiento (los nervios de aplastamiento cierran el ajuste)
RIB_R   = 0.35        # radio de los nervios de aplastamiento (sobresalen 0,35 -> 0,15 mm de interferencia)
MAT_D   = 8.0         # lo que asoma el conector del carril por la punta de la espiga (entra en el de la base)
FACE_GAP= 0.5         # separación entre la punta de la espiga y la cara del conector de la base
def conn_pts(W,H,zc,c):
    return [(-W/2+c,zc-H/2),(W/2-c,zc-H/2),(W/2,zc-H/2+c),(W/2,zc+H/2),(-W/2,zc+H/2),(-W/2,zc-H/2+c)]

# ---- ESPIGA pentagonal de unión carril -> base (maciza, sin brazos elásticos) ----
PL      = 19.0        # longitud de la espiga = grosor de la pared frontal de la base (engrane largo = no cabecea)
TW      = RW/2        # semiancho de la espiga (35 mm, igual que el carril)
TZ1     = 14.0        # altura de las paredes verticales; el tejado a 45º llega a TZ1+TW = 31,5
TCLR    = 0.15        # holgura por cara espiga/alojamiento (ajuste deslizante justo; ver galga)
TF      = 3.0         # suelo bajo el conector del carril
ZH      = TF+CR_H/2   # eje común de los dos conectores
SCR_X, SCR_Y = 14.3, -PL/2     # 2 tornillos M3x16 verticales (desde debajo de la base) en las paredes de la espiga
def tenon_pts(c=0.0, z0=0.0):
    w=TW+c; return [(-w,z0),(w,z0),(w,TZ1+c),(0,TZ1+c+w),(-w,TZ1+c)]

def tunnel_profile():
    """Hueco del conector del carril: rectángulo con chaflanes + bóveda a 45º encima (imprimible sin soportes)."""
    w=CR_W/2+C_CLR; zt=ZH+CR_H/2+C_CLR
    rect=Polygon(conn_pts(2*w,CR_H+2*C_CLR,ZH,CR_CH))
    roof=Polygon([(-w,zt-0.01),(w,zt-0.01),(0,zt+w)])
    return unary_union([rect,roof])

def tenon():
    y_end = -PL+(CR_L-MAT_D)                                     # fondo del túnel = tope del conector (y = -7)
    t = prism_y(tenon_pts(), -PL, 0.2)
    ribs=[cyl_y(RIB_R,-PL-1,y_end-1,s*(CR_W/2+C_CLR),ZH,16) for s in (-1,1)]
    cut = D(prism_y(tunnel_profile(),-PL-1,y_end), *ribs)
    wire = prism_y([(-6,4),(6,4),(6,9),(0,15),(-6,9)], y_end-0.1, 12)   # paso de los 4 cables hacia el canal central
    pil = [cyl_z(1.25,-1,12,s*SCR_X,SCR_Y) for s in (-1,1)]             # taladros guía Ø2,5 para M3 (rosca en plástico)
    return t, [cut, wire, *pil]

# =====================================================================================================================
# MÓDULO LED WS2812 de 8 LED (placa 53 x 10 mm, 2 taladros) - cotas del croquis "Corte del carril":
#   rebaje de la tapa translúcida 15 mm de ancho x 2 mm de prof.;  bolsillo de la placa 10 mm;  taladros a 8 mm del borde
# =====================================================================================================================
LED_L, LED_W, LED_T = 53.0, 10.0, 3.2        # placa (largo, ancho, grueso con LED)  -> MIDE TU PLACA
ZL      = 15.0                               # eje de la tira (centro de la cara lateral plana, z 6..24)
RB_L, RB_W, RB_D, RB_R = 75.0, 15.0, 2.0, 2.0  # rebaje de la tapa: 75 x 15 x 2, esquinas R2
PK_L, PK_W, PK_D = LED_L+0.4, LED_W+0.4, 3.5   # bolsillo de la placa (3,5 > 3,2 -> los LED quedan bajo la tapa)
HOLE_D, HOLE_SP = 1.8, 26.5                  # taladros guía Ø1,8 (tornillo M2 o rosca-chapa 2,2) separados 26,5 (4 LED)
HOLE_Z  = ZL-PK_W/2+0.2+2.0                  # a 2 mm del borde inferior de la placa = 8 mm del borde superior
HOLE_DEPTH = RW/2-RB_D-PK_D-CH_W/2+1.0   # pasante a través de la pared de 2,5 mm (M2 + tuerca por dentro)
LYC     = RL/2                               # alojamiento centrado en el carril
LY0     = LYC-RB_L/2
def led_cuts():
    c=[]
    rec=rrect(LY0,ZL-RB_W/2,LY0+RB_L,ZL+RB_W/2,RB_R)
    for sg in (-1,1):
        xo=sg*RW/2
        def X(a,b): return (min(xo-sg*a,xo-sg*b),max(xo-sg*a,xo-sg*b))
        x0,x1=X(-1,RB_D);              c.append(prism_x(rec,x0,x1))                                             # rebaje tapa
        # bolsillo de la placa: techo achaflanado a 45º detrás del borde superior de la placa (evita 3,5 mm de voladizo);
        # deja 0,8 mm de asiento para el borde superior de la tapa
        xa,xb=RW/2-RB_D-PK_D, RW/2-RB_D+0.01; zb,zt=ZL-PK_W/2, ZL+PK_W/2; zr=ZL+RB_W/2-0.8
        prof=[(sg*xa,zb),(sg*xb,zb),(sg*xb,zr),(sg*(xa+zr-zt),zr),(sg*xa,zt)]
        c.append(prism_y(Polygon(prof).buffer(0),LYC-PK_L/2,LYC+PK_L/2))
        xf=sg*(RW/2-RB_D-PK_D)
        for dy in (-HOLE_SP/2,HOLE_SP/2):
            c.append(cyl_x(HOLE_D/2,xf+sg*0.1,xf-sg*HOLE_DEPTH,LYC+dy,HOLE_Z))
        gap=(RB_L-PK_L)/2                                                                                        # 10,8 mm a cada extremo
        for ya in (LY0+gap/2-2, LY0+RB_L-gap/2-2):                                                               # paso de cables 4x6 al canal
            c.append(B(min(0,sg*(RW/2-RB_D+0.01)),max(0,sg*(RW/2-RB_D+0.01)),ya,ya+4,ZL-5,ZL+1))
    return c

def rail():
    t, tcuts = tenon()
    body=U(prism_y(ROUND_PTS,0,RL), t)
    return D(body,
             prism_y(SLOT_PTS,-1,RL+1),           # ranura de letras
             B(-CH_W/2,CH_W/2,11,RL-2,-1,CH_Z1),   # hueco central rectangular abierto por abajo (ESP32 + reductor + cables)
             B(-USB_W/2,USB_W/2,RL-2.1,RL+1,-1,USB_ZC+USB_H/2),   # ventana USB-C en el extremo libre (abierta por abajo)
             B(-10.5,10.5,11,RL-2,-1,2),          # rebaje de la tapa inferior
             *tcuts, *led_cuts())

def bottom_cover(): return B(-10.2,10.2,12,RL-2.3,0,2)
def led_cover():    # PLA translúcido, imprimir 2 (planas). 0,15 mm de holgura por cara; grosor 1,95 (queda a ras)
    c=0.15; P=rrect(0,0,RB_L-2*c,RB_W-2*c,RB_R-c)
    return trimesh.creation.extrude_polygon(P,RB_D-0.05)

# ---- Base de pared (80 de ancho), imprimir sobre la cara inferior ----
BX, BY, BZ0, BZ1, FW = 80, 56, -15, 45, PL     # BY 48 -> 56: más sitio para doblar los cables tras el conector
def base():
    b=B(-BX/2,BX/2,-BY,0,BZ0,BZ1)
    cav=B(-BX/2+3,BX/2-3,-BY+3,-FW,BZ0+3,BZ1+1)
    pocket=prism_y(tenon_pts(TCLR,-TCLR),-FW-0.1,0.1)                    # alojamiento = espiga + 0,15 (tejado 45º)
    scr=[]
    for s in (-1,1):                                                      # M3 desde abajo: avellanado Ø6,5 + cono 45º + Ø3,4
        x=s*SCR_X
        scr += [cyl_z(3.25,BZ0-1,-6,x,SCR_Y), cone_z(3.25,1.7,-6.01,-4.45,x,SCR_Y), cyl_z(1.7,-4.5,1,x,SCR_Y)]
    b=D(b,cav,pocket,*scr)
    # cuna del conector de la base: suelo + 2 postes con pestaña a presión + tope trasero con ranura para cables
    y0=-FW-FACE_GAP; y1=y0-CB_L; zb=ZH-CB_H/2; zt=ZH+CB_H/2
    w=CB_W/2+C_CLR; pw=2.4
    floor=B(-w-pw,w+pw,y1-2.5,-FW-0.1,BZ0+2.9,zb)
    posts=[]
    for s in (-1,1):
        xi,xo=s*w,s*(w+pw)
        posts.append(B(min(xi,xo),max(xi,xo),y1,y0,zb-0.01,zt+1.4))
        # pestaña: sobresale 0,6 hacia dentro sobre el conector; cara superior a 45º para que entre a presión
        posts.append(prism_y(Polygon([(xi,zt+0.15),(xi-s*0.6,zt+0.15),(xi-s*0.6,zt+0.55),(xi,zt+1.15)]).buffer(0), y1+3, y0-3))
    stop=D(B(-w-pw,w+pw,y1-2.5,y1,zb-0.01,zt+1.4), B(-CB_W/2+3,CB_W/2-3,y1-3,y1+0.1,zb+1.5,zt+2))
    ribs=[cyl_z(RIB_R,zb,zt,s*w,yy,16) for s in (-1,1) for yy in (y0-5,y1+5)]
    cradle=U(floor,*posts,stop)
    b=U(b,cradle,*ribs)
    holes=[cyl_y(2.1,-BY-1,-BY+3.1,sx,zz) for sx in (-30,30) for zz in (BZ0+8,BZ1-8)]
    holes.append(cyl_y(5,-BY-1,-BY+3.1,0,15))
    holes+=[cyl_y(4.25,-FW-0.1,0.1,sx,zz) for sx in (-30,30) for zz in (BZ0+8,BZ1-8)]
    return D(b,*holes)

def lid():
    return U(B(-BX/2,BX/2,-BY,0,BZ1,BZ1+2), B(-BX/2+3.3,BX/2-3.3,-BY+3.3,-FW-0.3,BZ1-4,BZ1+0.01))

# ---- Galgas de ajuste (imprimir PRIMERO, 10-15 min) ----
def gauges():
    """Galgas (se imprimen planas, ya en su orientación):
       A) placa de 8 mm con los huecos de los 2 conectores (con nervios de aplastamiento)
       B) bloque con el rebaje de la tapa (75x15x2) y el bolsillo de la placa LED (53,4x10,4x3,5) a tamaño real
       C) rebanada de 8 mm de la espiga + rebanada del alojamiento de la base -> comprueba la holgura carril-base"""
    def pz(P,z0,z1,dx=0,dy=0):
        m=trimesh.creation.extrude_polygon(P if isinstance(P,Polygon) else Polygon(P),z1-z0); m.apply_translation([dx,dy,z0]); return m
    # A
    w=CB_W/2+C_CLR; zt=ZH+CB_H/2+C_CLR
    pb=unary_union([Polygon(conn_pts(2*w,CB_H+2*C_CLR,ZH,CB_CH)),Polygon([(-w,zt-0.01),(w,zt-0.01),(0,zt+w)])])
    A=D(B(-32,32,-2,24,0,8),
        D(pz(tunnel_profile(),-1,9,-15,0),*[cyl_z(RIB_R,-2,10,-15+s*(CR_W/2+C_CLR),ZH) for s in (-1,1)]),
        D(pz(pb,-1,9,15,0),*[cyl_z(RIB_R,-2,10,15+s*w,ZH) for s in (-1,1)]))
    # B
    yb=40
    Bk=D(B(-42,42,yb-11,yb+11,0,6.5),
         pz(rrect(-RB_L/2,yb-RB_W/2,RB_L/2,yb+RB_W/2,RB_R),6.5-RB_D,7),
         B(-PK_L/2,PK_L/2,yb-PK_W/2,yb+PK_W/2,6.5-RB_D-PK_D,7),
         *[cyl_z(HOLE_D/2,0.5,7,dx,yb-PK_W/2+0.2+2.0) for dx in (-HOLE_SP/2,HOLE_SP/2)])
    # C
    yc=60
    sp=pz(tenon_pts(),0,8,-25,yc)
    ring=D(pz(tenon_pts(TCLR+4,-TCLR-4),0,8,25,yc),pz(tenon_pts(TCLR,-TCLR),-1,9,25,yc))
    return U(A,Bk), U(sp,ring)

# ---- Letras (sin cambios) ----
FOOT_PTS=[(-NECK,0.01),(NECK,0.01),(NECK,-NH),(HEAD,-NH),(HEAD,-NH-HH),(-HEAD,-NH-HH),(-HEAD,-NH),(-NECK,-NH)]
FOOT_Y={"E":(2,43),"4":(26,46),"A":(2,58)}
def poly(ch):
    if ch=="E": return unary_union([sbox(0,0,14,120),sbox(0,106,45,120),sbox(0,53,36,67),sbox(0,0,45,14)])
    if ch=="4": return [sbox(29,0,43,120), sbox(0,28,45,42), Polygon([(0,42),(14,42),(29.5,82),(29.5,120)])]
    if ch=="A": return unary_union([Polygon([(0,0),(14,0),(38,120),(22,120)]),
                    Polygon([(46,0),(60,0),(38,120),(22,120)]),sbox(11,26,49,40)])
def letter(ch,y0):
    P=poly(ch); P=P if isinstance(P,list) else [P]
    body=U(*[trimesh.creation.extrude_polygon(q,LET_T) for q in P])
    M=np.array([[0,0,1,-LET_T/2],[1,0,0,0],[0,1,0,0],[0,0,0,1]],float); body.apply_transform(M)
    m=U(body,prism_y(FOOT_PTS,*FOOT_Y[ch])); m.apply_translation([0,y0,RH]); return m

def overhang(m,axis,floor,thr=0.72):
    n=m.face_normals; c=m.triangles_center; a=m.area_faces
    bad=(n[:,axis]<-thr)&(c[:,axis]>floor+0.05)
    return round(float(a[bad].sum()),1), np.round(np.unique(np.round(c[bad][:,axis],1))[:8],1).tolist()

def save(m,n):
    m.export(os.path.join(OUT,n)); print(n,m.is_watertight,np.round(m.extents,1))

if __name__=="__main__":
    r,bs,l,d,lc=rail(),base(),lid(),bottom_cover(),led_cover()
    L=[letter("E",18),letter("4",71),letter("A",124)]
    g1,g2=gauges()
    save(r,"01_carril_con_espiga_PLA_negro.stl"); save(bs,"02_base_pared_PLA_negro.stl")
    lp=l.copy(); lp.apply_transform(trimesh.transformations.rotation_matrix(np.pi,[1,0,0])); lp.apply_translation([0,0,-lp.bounds[0][2]])
    save(lp,"03_tapa_base_PLA_negro.stl"); save(d,"04_tapa_inferior_canal_PLA_negro.stl"); save(lc,"04b_tapa_led_PLA_translucido_x2.stl")
    for c,m in zip("E4A",L): save(m,f"05_letra_{c}_PLA_amarillo.stl")
    save(g1,"00a_galga_conectores_y_led.stl"); save(g2,"00b_galga_espiga_y_alojamiento.stl")
    save(trimesh.util.concatenate([r,bs,l,d,*L]),"00_conjunto_montado.stl")
    # --- comprobaciones ---
    I=lambda a,b: round(trimesh.boolean.intersection([a,b],engine='manifold').volume,3)
    print("interf carril-base:",I(r,bs))
    for c,m in zip("E4A",L): print("interf letra",c,"-carril:",I(r,m))
    cr=prism_y(conn_pts(CR_W,CR_H,ZH,CR_CH),-PL-MAT_D,-PL-MAT_D+CR_L)
    cb=prism_y(conn_pts(CB_W,CB_H,ZH,CB_CH),-FW-FACE_GAP-CB_L,-FW-FACE_GAP)
    print("conector carril vs carril (solo nervios, ~0,15 mm):",I(cr,r))
    print("conector base vs base (solo nervios):",I(cb,bs))
    print("conector base vs carril:",I(cb,r))
    print("voladizos carril (mm2):",overhang(r,2,0))
    print("voladizos base (mm2):",overhang(bs,2,BZ0))
    for c,m in zip("E4A",L): print("voladizos letra",c,":",overhang(m,0,-7.5))
