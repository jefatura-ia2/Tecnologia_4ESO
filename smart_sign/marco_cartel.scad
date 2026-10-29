// =====================================================================
//  Smart Sign IoT · Soporte de pared, tapa y capuchón del cartel
//  TEC_IVJP_lab27 · Tecnología 4º ESO · Misión 4 (Equipo A)
//
//  Modelo PARAMÉTRICO: cambia los valores medidos con el calibre y
//  vuelve a renderizar (F6). Elige la pieza en la variable «pieza» y
//  exporta a STL (Archivo → Exportar → STL).
//
//  Unidades: mm.  Ejes: X = largo, Y = fondo (Y=0 cara frontal), Z = alto.
// =====================================================================

pieza = "conjunto";   // "conjunto" | "soporte" | "tapa" | "capuchon" | "probeta"

// ---------- Metacrilato (mídelo con el calibre en 3 puntos) ----------
ancho_metacrilato   = 160;
alto_metacrilato    = 120;
espesor_metacrilato = 5;
holgura             = 0.2;    // la ranura de la probeta que mejor encaje
prof_ranura         = 10;     // cuánto entra el metacrilato en el soporte

// ---------- Tira LED WS2812 ----------
ancho_tira = 10.5;
alto_tira  = 3;

// ---------- Caja ----------
pared        = 2.4;           // 6 perímetros de 0,4 mm
fondo        = 45;            // cabe la batería 18650 en su portapilas (21 mm) y los módulos
alto_hueco   = 22;            // hueco para la electrónica: el portapilas de la 18650 mide ≈ 21 mm de alto
suelo_canal  = 2.4;           // separación entre el hueco y el canal de la tira
tapa_grosor  = 2;

// ---------- Huecos ----------
usb_ancho = 10;   usb_alto = 4;    // USB-C del TP4056
ojal_d    = 8;    ojal_ranura = 4; ojal_sep = 120;   // dos ojales para tornillos de pared
torreta_d = 7;    rosca_d = 2.6;   paso_d = 3.4;      // tornillos M3
pir_ventana = false;  pir_d = 23;                      // versión 2 (misión 6)

// ---------- Valores calculados (no tocar) ----------
ranura = espesor_metacrilato + holgura;
L      = ancho_metacrilato + 16;                       // 176
z_canal  = alto_hueco + suelo_canal;                   // base del canal de la tira
H      = z_canal + alto_tira + 0.6 + prof_ranura;      // alto total del soporte (≈ 38)
y_c    = fondo / 2;                                     // eje del metacrilato
$fn = 48;

echo(str("Ranura = ", ranura, " mm · Soporte ", L, " × ", fondo, " × ", H, " mm"));

// =====================================================================
module soporte() {
    difference() {
        cube([L, fondo, H]);

        // hueco de la electrónica, abierto por abajo (lo cierra la tapa)
        translate([pared, pared, -1]) cube([L - 2*pared, fondo - 2*pared, alto_hueco + 1]);

        // canal de la tira LED (un poco más largo que el metacrilato)
        translate([(L - ancho_metacrilato - 2)/2, y_c - (ancho_tira + 0.6)/2, z_canal])
            cube([ancho_metacrilato + 2, ancho_tira + 0.6, alto_tira + 0.6 + 0.01]);

        // ranura del metacrilato
        translate([(L - ancho_metacrilato - 0.4)/2, y_c - ranura/2, H - prof_ranura])
            cube([ancho_metacrilato + 0.4, ranura, prof_ranura + 1]);

        // paso de cables de la tira hacia el hueco
        translate([(L - ancho_metacrilato)/2 + 4, y_c, alto_hueco - 1]) cylinder(d = 5, h = suelo_canal + 2);

        // hueco USB-C en el lateral izquierdo (con techo en arco: sin soportes)
        translate([-1, y_c - usb_ancho/2, 3]) usb_hueco();

        // ojales en la cara trasera para colgarlo (cabeza del tornillo Ø8, ranura de 4 mm)
        for (x = [L/2 - ojal_sep/2, L/2 + ojal_sep/2])
            translate([x, fondo + 1, 7]) rotate([90, 0, 0]) ojal();

        // ventana del sensor PIR en el frontal (v2)
        if (pir_ventana)
            translate([L - 25, -1, alto_hueco/2]) rotate([-90, 0, 0]) cylinder(d = pir_d, h = pared + 2);
    }
    // torretas para los tornillos de la tapa
    for (p = torretas())
        translate([p[0], p[1], 0]) difference() {
            cylinder(d = torreta_d, h = alto_hueco);
            translate([0, 0, -1]) cylinder(d = rosca_d, h = 12);
        }
}

module usb_hueco() {
    // rectángulo con techo en punta a 45°: imprimible sin soportes
    rotate([90, 0, 90]) linear_extrude(pared + 2)
        polygon([[0, 0], [usb_ancho, 0], [usb_ancho, usb_alto], [usb_ancho/2, usb_alto + usb_ancho/2], [0, usb_alto]]);
}

module ojal() {
    cylinder(d = ojal_d, h = pared + 2);
    translate([-ojal_ranura/2, 0, 0]) cube([ojal_ranura, 6, pared + 2]);
    translate([0, 6, 0]) cylinder(d = ojal_ranura, h = pared + 2);
}

function torretas() = [
    [pared + torreta_d/2, pared + torreta_d/2],
    [L - pared - torreta_d/2, pared + torreta_d/2],
    [pared + torreta_d/2, fondo - pared - torreta_d/2],
    [L - pared - torreta_d/2, fondo - pared - torreta_d/2]
];

// =====================================================================
module tapa() {
    difference() {
        cube([L, fondo, tapa_grosor]);
        for (p = torretas()) translate([p[0], p[1], -1]) {
            cylinder(d = paso_d, h = tapa_grosor + 2);
            translate([0, 0, tapa_grosor - 0.6]) cylinder(d1 = paso_d, d2 = 6.4, h = 1.61);   // avellanado
        }
        // rejilla de ventilación para el TP4056 (se calienta al cargar)
        for (i = [0:5]) translate([20 + i*6, fondo/2 - 8, -1]) cube([2.5, 16, tapa_grosor + 2]);
    }
}

// =====================================================================
module capuchon() {
    pc = 2;                        // pared del capuchón
    prof = 7;                      // cuánto abraza el canto superior
    Lc = ancho_metacrilato + 0.4 + 2*pc;
    Wc = ranura + 2*pc;
    difference() {
        cube([Lc, Wc, prof + pc]);
        translate([pc, pc, -1]) cube([ancho_metacrilato + 0.4, ranura, prof + 1]);
    }
}

// =====================================================================
module probeta() {
    holguras = [0, 0.1, 0.2, 0.3, 0.4];
    difference() {
        cube([len(holguras) * 14 + 4, 20, 12]);
        for (i = [0 : len(holguras) - 1])
            translate([4 + i*14, -1, 4]) cube([espesor_metacrilato + holguras[i], 22, 9]);
    }
    for (i = [0 : len(holguras) - 1])
        translate([4 + i*14, 2, 12]) linear_extrude(0.6) text(str(i), size = 5);
}

// =====================================================================
if (pieza == "soporte")  soporte();
if (pieza == "tapa")     tapa();
if (pieza == "capuchon") capuchon();
if (pieza == "probeta")  probeta();
if (pieza == "conjunto") {
    color("WhiteSmoke") soporte();
    color("DimGray") translate([0, 0, -tapa_grosor - 6]) tapa();             // tapa separada (vista explosionada)
    color("LightCyan", 0.45)
        translate([(L - ancho_metacrilato)/2, y_c - espesor_metacrilato/2, H - prof_ranura + 6])
            cube([ancho_metacrilato, espesor_metacrilato, alto_metacrilato]);
    color("WhiteSmoke")
        translate([(L - ancho_metacrilato - 0.4)/2 - 2, y_c - ranura/2 - 2, H - prof_ranura + 6 + alto_metacrilato + 8])
            capuchon();    // la abertura mira hacia abajo y abraza el canto superior
}
