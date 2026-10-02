"""Pixel maps drawn by hand for the board pieces.

Each map stores only the left half of a symmetric sprite; `filas` mirrors it.
Every character is a key of the faction palette in `datos/paletas.json`, and
`.` is transparent.
"""

MAPAS = {
    # Life tokens, 12 x 12
    "llama": [
        "......",
        ".....K",
        "....KR",
        "...KRO",
        "..KROO",
        ".KROOY",
        ".KROYY",
        "KROYYW",
        "KROYWW",
        "KROOYW",
        ".KRROO",
        "..KKKK",
    ],
    "flor": [
        "......",
        "....KK",
        "...KPP",
        ".KKKPP",
        "KPPKPP",
        "KPPPKY",
        ".KPPKY",
        "KPPPPK",
        "KPPKPP",
        ".KK.KP",
        "....Kg",
        "....Kg",
    ],
    "torre": [
        "......",
        ".KK.KK",
        ".KmKKm",
        ".KmmmM",
        "..KmmM",
        "..KmMK",
        "..KmMK",
        "..KmmM",
        "..KmmM",
        ".KmmmM",
        ".KMMMM",
        ".KKKKK",
    ],
    # Attack line icons, 12 x 12
    "espada": [
        ".....K",
        "....Ki",
        "....Ki",
        "....Ki",
        "....Ki",
        "....Ki",
        "....Ki",
        "..KKKY",
        "..KYYY",
        "....KM",
        "....KM",
        ".....K",
    ],
    "arco": [
        ".....K",
        "....Ki",
        "...Kii",
        ".....M",
        "K....M",
        "KM...M",
        ".KM..M",
        "..KMMM",
        "...KKM",
        ".....M",
        "....KY",
        "....Y.",
    ],
    "catapulta": [
        "......",
        "....KK",
        "...KiI",
        "....KK",
        ".....M",
        "....KM",
        "...KMK",
        "..KM.M",
        ".KM..M",
        "KMMMMM",
        "KiK...",
        ".K....",
    ],
    # Faction emblems, 16 x 16
    "volcan": [
        "........",
        "......OY",
        ".....O.Y",
        "......OO",
        ".....KKK",
        ".....KSO",
        "....KSSO",
        "....KSsS",
        "...KSsSS",
        "...KSSsO",
        "..KSsSSO",
        "..KSSsSS",
        ".KSsSSsS",
        ".KSSSSSS",
        "KKKKKKKK",
        "........",
    ],
    "arbol": [
        "........",
        ".....KKK",
        "...KKgGG",
        "..KgGGgG",
        ".KgGPGGg",
        ".KGGGgGG",
        "KgGgGGPG",
        "KGGGGgGG",
        ".KGPGGBG",
        "..KKGKBB",
        "....KKBB",
        "......BB",
        ".....KBB",
        "...KKBbB",
        "..KBbKBB",
        ".KK..KKK",
    ],
    "casco": [
        "........",
        ".....RRR",
        "....RRRR",
        "....KKKK",
        "...KYYYY",
        "..KYmYYY",
        "..KYYYYY",
        "..KYYKKY",
        "..KYYKKY",
        "..KYYYKY",
        "..KYYYKK",
        "...KYYK.",
        "...KYYK.",
        "....KK..",
        "........",
        "........",
    ],
}

# Board pieces: file name -> (map, palette)
PIEZAS = {
    "vida-draconiens": ("llama", "DRACONIENS"),
    "vida-lothrim": ("flor", "LOTHRIM"),
    "vida-hoplitas": ("torre", "HOPLITAS"),
    "linea-cuerpo-a-cuerpo": ("espada", "NEUTRAL"),
    "linea-distancia": ("arco", "NEUTRAL"),
    "linea-asedio": ("catapulta", "NEUTRAL"),
    "emblema-draconiens": ("volcan", "DRACONIENS"),
    "emblema-lothrim": ("arbol", "LOTHRIM"),
    "emblema-hoplitas": ("casco", "HOPLITAS"),
}


def filas(nombre: str) -> list[str]:
    mitad = MAPAS[nombre]
    ancho = max(len(f) for f in mitad)
    completas = []
    for fila in mitad:
        izquierda = fila.ljust(ancho, ".")
        completas.append(izquierda + izquierda[::-1])
    return completas
