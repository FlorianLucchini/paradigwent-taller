"""Review sheet: one row per card with the hand-drawn sprite (if any), the raw
candidates and their pixelated version, side by side."""

from html import escape

from taller.datos import ASSETS, PRUEBAS, cartas

ESTILO = """
body { background: #16120e; color: #ece3d2; font-family: Georgia, serif; padding: 24px; }
h1 { font-weight: 400; } h2 { font-weight: 400; margin: 32px 0 4px; } p { color: #b3a690; margin: 0 0 12px; }
.fila { display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-start; }
figure { margin: 0; display: grid; gap: 4px; font: 12px monospace; color: #b3a690; }
img { width: 160px; height: 160px; background: #2b231b; }
img.pixel { image-rendering: pixelated; }
.grupo { display: grid; gap: 6px; } .grupo > span { font: 12px monospace; color: #c9a24a; }
"""


def figura(src: str, pie: str, pixel: bool) -> str:
    clase = ' class="pixel"' if pixel else ""
    return f'<figure><img{clase} src="{src}" alt="{escape(pie)}"><figcaption>{escape(pie)}</figcaption></figure>'


def escribir(lote: str, ids: list[str], opciones: int) -> None:
    todas = cartas()
    bloques = []
    for carta_id in ids:
        carta = todas[carta_id]
        grupos = []
        if (ASSETS / "ilustraciones" / f"{carta_id}.png").exists():
            grupos.append(("Por código", [figura(f"../../assets/ilustraciones/{carta_id}.png", "código", True)]))
        for carpeta, titulo, pixel in (("crudas", "Stable Diffusion", False), ("pixeladas", "Pixelada", True)):
            figs = [
                figura(f"{carpeta}/{carta_id}-{n}.png", f"opción {n}", pixel)
                for n in range(1, opciones + 1)
                if (PRUEBAS / lote / carpeta / f"{carta_id}-{n}.png").exists()
            ]
            if figs:
                grupos.append((titulo, figs))
        html_grupos = "".join(
            f'<div class="grupo"><span>{t}</span><div class="fila">{"".join(f)}</div></div>' for t, f in grupos
        )
        bloques.append(
            f"<h2>{escape(carta['nombre'])}</h2><p>{escape(carta['descripcion'])}</p>"
            f'<div class="fila">{html_grupos}</div>'
        )

    html = (
        f'<!doctype html><meta charset="utf-8"><title>Revisión {escape(lote)}</title>'
        f"<style>{ESTILO}</style><h1>Revisión: {escape(lote)}</h1>{''.join(bloques)}"
    )
    (PRUEBAS / lote / "index.html").write_text(html, encoding="utf-8")
