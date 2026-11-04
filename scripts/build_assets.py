"""Gera os SVGs animados do perfil em assets/ (hero, pinagem e trajetória)."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

BOARD = "#07130e"
BOARD_LINE = "#143126"
GREEN = "#39d353"
GOLD = "#d9a441"
SILK = "#e6edf3"
MUTED = "#8fa89b"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"

BASE_CSS = f"""
text{{font-family:{MONO}}}
.silk{{fill:{SILK}}}.muted{{fill:{MUTED}}}.gold{{fill:{GOLD}}}.green{{fill:{GREEN}}}
.trace{{fill:none;stroke:{GOLD};stroke-width:2;opacity:.45}}
.pulse{{fill:none;stroke:{GREEN};stroke-width:3;stroke-linecap:round;
  stroke-dasharray:70 530;animation:flow 3s linear infinite}}
.chip{{fill:#10171a;stroke:{GOLD};stroke-width:1.5}}
.led{{fill:{GREEN};animation:blink 1.6s ease-in-out infinite}}
@keyframes flow{{from{{stroke-dashoffset:600}}to{{stroke-dashoffset:0}}}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""

# Fonte de matriz de pontos 5x7, só com as letras do nome.
FONT = {
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    " ": ["00000"] * 7,
}


def board(w, h):
    """Placa de circuito: fundo, furos de fixação e borda em serigrafia."""
    parts = [
        f'<rect width="{w}" height="{h}" rx="16" fill="{BOARD}"/>',
        f'<rect x="8" y="8" width="{w-16}" height="{h-16}" rx="11" fill="none" stroke="{BOARD_LINE}" stroke-width="2"/>',
    ]
    for x, y in ((24, 24), (w - 24, 24), (24, h - 24), (w - 24, h - 24)):
        parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#000" stroke="{GOLD}" stroke-width="2.5"/>')
    return "".join(parts)


def svg(w, h, title, css, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
        f"<title>{title}</title><style>{BASE_CSS}{css}</style>{board(w, h)}{body}</svg>\n"
    )


def dot_matrix(text, x0, y0, pitch, radius):
    """Letreiro de LEDs. A luz varre as colunas da esquerda para a direita."""
    off, on = [], []
    col = 0
    for ch in text:
        glyph = FONT[ch]
        for c in range(5):
            cx = x0 + (col + c) * pitch
            delay = (col + c) * 0.035
            for r in range(7):
                cy = y0 + r * pitch
                if glyph[r][c] == "1":
                    on.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" style="animation-delay:{delay:.2f}s"/>')
                else:
                    off.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}"/>')
        col += 6
    return (
        f'<g fill="#12281e">{"".join(off)}</g>'
        f'<g class="lit" fill="{GREEN}">{"".join(on)}</g>'
    )


def hero():
    w, h = 1000, 400
    css = """
.lit circle{animation:lit 5s ease-in-out infinite}
@keyframes lit{0%,100%{opacity:1}8%{opacity:.35;fill:#d9a441}16%{opacity:1}}
.wave{animation:slide 2s linear infinite}
@keyframes slide{to{transform:translateX(-80px)}}
.bits{animation:bits 7s linear infinite}
@keyframes bits{to{transform:translateX(-168px)}}
.bar{transform-box:fill-box;transform-origin:bottom;animation:grow 4s ease-in-out infinite}
@keyframes grow{0%{transform:scaleY(.1)}35%,100%{transform:scaleY(1)}}
.fc{stroke-dasharray:6 6;animation:fc 1.2s linear infinite}
@keyframes fc{to{stroke-dashoffset:-12}}
"""
    name_w = (13 * 6 - 1 - 1) * 11
    x0 = (w - name_w) / 2
    b = [
        f'<text x="48" y="44" font-size="15" class="gold">GS-2026</text>',
        f'<text x="{w/2}" y="44" font-size="15" class="muted" text-anchor="middle">DATASHEET · REV 3.0</text>',
        f'<text x="{w-48}" y="44" font-size="15" class="muted" text-anchor="end">SÃO PAULO · SP</text>',
        dot_matrix("GABRIEL SOUZA", x0, 74, 11, 4.3),
        f'<text x="{w/2}" y="182" font-size="18" class="silk" text-anchor="middle" letter-spacing="1">Análise de Dados · Ciência de Dados · Governança e Privacidade</text>',
    ]

    # Estágio 1: sinal analógico.
    wave = "M-80 0" + "".join(
        f" L{x} {-24 * math.sin(2 * math.pi * x / 80):.1f}" for x in range(-76, 360, 4)
    )
    b.append(
        '<clipPath id="c1"><rect x="50" y="222" width="230" height="96"/></clipPath>'
        f'<g clip-path="url(#c1)"><g transform="translate(50 270)"><path class="wave" d="{wave}" fill="none" stroke="{GREEN}" stroke-width="2.5"/></g></g>'
    )

    # Estágio 2: bits.
    pattern = "1011 0010 1110 0101 "
    b.append(
        '<clipPath id="c2"><rect x="400" y="222" width="200" height="96"/></clipPath>'
        f'<g clip-path="url(#c2)" font-size="21" class="green">'
        f'<text class="bits" x="400" y="262" xml:space="preserve">{pattern * 4}</text>'
        f'<text class="bits" x="316" y="294" xml:space="preserve" style="animation-duration:5s" opacity=".55">{pattern * 4}</text>'
        "</g>"
    )

    # Estágio 3: dados reais viram previsão.
    heights = [24, 38, 31, 52, 46, 66]
    for i, bh in enumerate(heights):
        b.append(f'<rect class="bar" x="{722 + i * 27}" y="{318 - bh}" width="19" height="{bh}" rx="2" fill="{GREEN}" style="animation-delay:{i * .12:.2f}s"/>')
    b.append(f'<path class="fc" d="M866 252 L900 238 L944 224" fill="none" stroke="{GOLD}" stroke-width="2.5"/>')

    # Trilhas e chips conversores entre os estágios.
    for x1, x2, label in ((288, 392, "ADC"), (608, 714, "ML")):
        cx = (x1 + x2) / 2
        b.append(f'<path class="trace" d="M{x1} 270 H{x2}"/>')
        b.append(f'<path class="pulse" pathLength="600" d="M{x1} 270 H{x2}"/>')
        for dy in (-14, 0, 14):
            b.append(f'<path d="M{cx-34} {270+dy} H{cx+34}" stroke="{GOLD}" stroke-width="3"/>')
        b.append(f'<rect class="chip" x="{cx-28}" y="246" width="56" height="48" rx="3"/>')
        b.append(f'<text x="{cx}" y="276" font-size="17" class="silk" text-anchor="middle">{label}</text>')

    for x, title, sub in ((165, "SINAL", "eletrônica"), (500, "CÓDIGO", "desenvolvimento"), (833, "DECISÃO", "dados e previsão")):
        b.append(f'<text x="{x}" y="349" font-size="16" class="silk" text-anchor="middle" letter-spacing="2">{title}</text>')
        b.append(f'<text x="{x}" y="370" font-size="14" class="muted" text-anchor="middle">{sub}</text>')
    return svg(w, h, "Gabriel Souza: do sinal ao dado, do dado à decisão", css, "".join(b))


def pinout():
    left = ["Python", "SQL", "MongoDB", "Pandas", "Java", "HTML / CSS", "Power BI", "Excel", "n8n", "SAP", "Figma", "Git / GitHub"]
    right = ["Machine Learning", "Modelagem Preditiva", "Detecção de Anomalias", "Análise Exploratória", "LLM", "Big Data", "Modelagem de Dados", "Dashboards", "Automação", "Qualidade de Dados", "Governança de Dados", "LGPD"]
    w, h = 1000, 560
    top, step = 96, 34
    n = len(left)
    chip_x, chip_w = 360, 280
    chip_y, chip_h = 72, step * n + 14
    b = [
        '<text x="48" y="50" font-size="15" class="gold">IN · FERRAMENTAS</text>',
        f'<text x="{w-48}" y="50" font-size="15" class="gold" text-anchor="end">OUT · ENTREGAS</text>',
    ]
    for i in range(n):
        y = top + i * step
        lpath = f"M248 {y} H{chip_x}"
        rpath = f"M{chip_x+chip_w} {y} H752"
        delay = i * 0.25
        b.append(f'<path class="trace" d="{lpath}"/><path class="trace" d="{rpath}"/>')
        b.append(f'<path class="pulse" pathLength="600" d="{lpath}" style="animation-delay:{delay:.2f}s"/>')
        b.append(f'<path class="pulse" pathLength="600" d="{rpath}" style="animation-delay:{delay + 1:.2f}s"/>')
        for x, pw in ((chip_x - 16, 16), (chip_x + chip_w, 16)):
            b.append(f'<rect x="{x}" y="{y-5}" width="{pw}" height="10" fill="#c7ccd1"/>')
        b.append(f'<circle cx="248" cy="{y}" r="4.5" fill="{GOLD}"/><circle cx="752" cy="{y}" r="4.5" fill="{GOLD}"/>')
        b.append(f'<text x="232" y="{y+6}" font-size="17" class="silk" text-anchor="end">{left[i]}</text>')
        b.append(f'<text x="768" y="{y+6}" font-size="17" class="silk">{right[i]}</text>')
        b.append(f'<text x="{chip_x+10}" y="{y+5}" font-size="13" class="muted">{i+1}</text>')
        b.append(f'<text x="{chip_x+chip_w-10}" y="{y+5}" font-size="13" class="muted" text-anchor="end">{2*n-i}</text>')
    cx = chip_x + chip_w / 2
    b.append(f'<rect x="{chip_x}" y="{chip_y}" width="{chip_w}" height="{chip_h}" rx="5" fill="none" stroke="{GOLD}" stroke-width="1.5"/>')
    b.insert(2, f'<rect x="{chip_x}" y="{chip_y}" width="{chip_w}" height="{chip_h}" rx="5" fill="#10171a"/>')
    b.append(f'<path d="M{cx-18} {chip_y} a18 18 0 0 0 36 0" fill="{BOARD}" stroke="{GOLD}" stroke-width="1.5"/>')
    mid = chip_y + chip_h / 2
    b.append(f'<text x="{cx}" y="{mid-22}" font-size="28" class="silk" text-anchor="middle" font-weight="700">GS-2026</text>')
    b.append(f'<text x="{cx}" y="{mid+6}" font-size="14" class="muted" text-anchor="middle">processador de dados</text>')
    b.append(f'<text x="{cx}" y="{mid+28}" font-size="14" class="muted" text-anchor="middle">encapsulamento: humano</text>')
    b.append(f'<circle class="led" cx="{cx}" cy="{mid+56}" r="6"/>')
    b.append(f'<text x="{cx}" y="{mid+84}" font-size="13" class="green" text-anchor="middle">ATIVO</text>')
    return svg(w, h, "Pinagem: ferramentas de entrada e entregas de saída", "", "".join(b))


def path():
    stages = [
        ("U1", "2022–2024", "Técnico em", "Eletrônica", "Etec Carolina", "Carinhato Sampaio", False),
        ("U2", "2025–2027", "Análise e Desenv.", "de Sistemas", "Centro Univ.", "Senac Santo Amaro", True),
        ("U3", "jan/2026 → hoje", "Data Governance", "e Privacidade", "Jovem Aprendiz", "QuintoAndar", True),
        ("U4", "2026–2028", "Tecnólogo em", "Data Science", "FIAP", "Machine Learning", True),
    ]
    w, h = 1000, 300
    card_w, gap, y = 210, 26, 74
    x0 = (w - 4 * card_w - 3 * gap) / 2
    bus_y = y + 172
    b = [
        f'<text x="{w/2}" y="46" font-size="15" class="muted" text-anchor="middle">VCC ── do ferro de solda ao modelo preditivo ── OUT</text>',
        f'<path class="trace" d="M40 {bus_y} H{w-40}"/>',
        f'<path class="pulse" pathLength="600" d="M40 {bus_y} H{w-40}" style="animation-duration:4s"/>',
    ]
    for i, (ref, when, t1, t2, s1, s2, active) in enumerate(stages):
        x = x0 + i * (card_w + gap)
        cx = x + card_w / 2
        b.append(f'<path class="trace" d="M{cx} {y+152} V{bus_y}"/><circle cx="{cx}" cy="{bus_y}" r="5" fill="{GOLD}"/>')
        b.append(f'<rect class="chip" x="{x}" y="{y}" width="{card_w}" height="152" rx="6"/>')
        b.append(f'<text x="{x+14}" y="{y+26}" font-size="14" class="gold">{ref}</text>')
        if active:
            b.append(f'<circle class="led" cx="{x+card_w-18}" cy="{y+21}" r="5.5" style="animation-delay:{i * .3:.1f}s"/>')
        else:
            b.append(f'<text x="{x+card_w-14}" y="{y+26}" font-size="16" class="green" text-anchor="end">✓</text>')
        b.append(f'<text x="{x+14}" y="{y+60}" font-size="16" class="silk" font-weight="700">{t1}</text>')
        b.append(f'<text x="{x+14}" y="{y+81}" font-size="16" class="silk" font-weight="700">{t2}</text>')
        b.append(f'<text x="{x+14}" y="{y+106}" font-size="14" class="muted">{s1}</text>')
        b.append(f'<text x="{x+14}" y="{y+124}" font-size="14" class="muted">{s2}</text>')
        b.append(f'<text x="{cx}" y="{bus_y+30}" font-size="14" class="silk" text-anchor="middle">{when}</text>')
    return svg(w, h, "Trajetória: Etec, Senac, QuintoAndar e FIAP", "", "".join(b))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "hero.svg").write_text(hero(), encoding="utf-8")
    (OUT / "pinout.svg").write_text(pinout(), encoding="utf-8")
    (OUT / "path.svg").write_text(path(), encoding="utf-8")
