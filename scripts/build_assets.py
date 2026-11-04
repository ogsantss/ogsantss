"""Gera os SVGs animados do perfil em assets/."""
import math
import random
import textwrap
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
                    on.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" style="animation-duration:5s;animation-delay:{delay:.2f}s"/>')
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
        f'<text x="48" y="44" font-size="15" class="gold">Gabriel</text>',
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
    for x1, x2, label in ((288, 392, "ADC"), (608, 714, "SQL")):
        cx = (x1 + x2) / 2
        b.append(f'<path class="trace" d="M{x1} 270 H{x2}"/>')
        b.append(f'<path class="pulse" pathLength="600" d="M{x1} 270 H{x2}"/>')
        for dy in (-14, 0, 14):
            b.append(f'<path d="M{cx-34} {270+dy} H{cx+34}" stroke="{GOLD}" stroke-width="3"/>')
        b.append(f'<rect class="chip" x="{cx-28}" y="246" width="56" height="48" rx="3"/>')
        b.append(f'<text x="{cx}" y="276" font-size="17" class="silk" text-anchor="middle">{label}</text>')

    for x, title, sub in ((165, "SINAL", "eletrônica"), (500, "CÓDIGO", "desenvolvimento"), (833, "DECISÃO", "dados e indicadores")):
        b.append(f'<text x="{x}" y="349" font-size="16" class="silk" text-anchor="middle" letter-spacing="2">{title}</text>')
        b.append(f'<text x="{x}" y="370" font-size="14" class="muted" text-anchor="middle">{sub}</text>')
    return svg(w, h, "Gabriel Souza: do sinal ao dado, do dado à decisão", css, "".join(b))


def pinout():
    left = ["Python", "SQL", "MongoDB", "Pandas", "Java", "Power BI", "Excel", "Git / GitHub"]
    right = ["Tratamento de Dados", "Análise Exploratória", "Indicadores", "Modelagem de Dados", "Dashboards", "Automação", "Qualidade de Dados", "LGPD"]
    w, h = 1000, 430
    top, step = 96, 38
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
        b.append(f'<path class="pulse" pathLength="600" d="{rpath}" style="animation-duration:5s;animation-delay:{delay + 1:.2f}s"/>')
        for x, pw in ((chip_x - 16, 16), (chip_x + chip_w, 16)):
            b.append(f'<rect x="{x}" y="{y-5}" width="{pw}" height="10" fill="#c7ccd1"/>')
        b.append(f'<circle cx="248" cy="{y}" r="4.5" fill="{GOLD}"/><circle cx="752" cy="{y}" r="4.5" fill="{GOLD}"/>')
        b.append(f'<text x="232" y="{y+6}" font-size="17" class="silk" text-anchor="end">{left[i]}</text>')
        b.append(f'<text x="768" y="{y+6}" font-size="17" class="silk">{right[i]}</text>')
    cx = chip_x + chip_w / 2
    b.append(f'<rect x="{chip_x}" y="{chip_y}" width="{chip_w}" height="{chip_h}" rx="5" fill="none" stroke="{GOLD}" stroke-width="1.5"/>')
    b.insert(2, f'<rect x="{chip_x}" y="{chip_y}" width="{chip_w}" height="{chip_h}" rx="5" fill="#10171a"/>')
    b.append(f'<path d="M{cx-18} {chip_y} a18 18 0 0 0 36 0" fill="{BOARD}" stroke="{GOLD}" stroke-width="1.5"/>')
    mid = chip_y + chip_h / 2
    b.append(f'<text x="{cx}" y="{mid+11}" font-size="34" class="silk" text-anchor="middle" font-weight="700">Gabriel</text>')
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
        f'<text x="{w/2}" y="46" font-size="15" class="muted" text-anchor="middle">VCC ── do ferro de solda aos dados ── OUT</text>',
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


def multiline(x, y, content, width, size, cls, gap=None, extra=""):
    gap = gap or round(size * 1.35)
    return "".join(
        f'<text x="{x}" y="{y + i * gap}" font-size="{size}" class="{cls}"{extra}>{line}</text>'
        for i, line in enumerate(textwrap.wrap(content, width))
    )


def description():
    w, h = 1000, 380
    text = (
        "O Gabriel é um profissional de dados em início de carreira que transforma dados brutos "
        "em indicadores, análises e processos bem documentados, com atenção "
        "à privacidade."
    )
    lcd = "#a9c94f"
    css = f"""
.cov{{transform:translateX(900px)}}
.c0{{animation:c0 30s steps(70) infinite}}.c1{{animation:c1 30s steps(70) infinite}}.c2{{animation:c2 30s steps(70) infinite}}
@keyframes c0{{0%{{transform:translateX(0)}}4%,100%{{transform:translateX(900px)}}}}
@keyframes c1{{0%,4%{{transform:translateX(0)}}8%,100%{{transform:translateX(900px)}}}}
@keyframes c2{{0%,8%{{transform:translateX(0)}}12%,100%{{transform:translateX(900px)}}}}
.feat{{animation:feat 5s ease-in-out infinite}}
@keyframes feat{{0%,100%{{stroke:{GOLD}}}10%{{stroke:{GREEN}}}25%{{stroke:{GOLD}}}}}
"""
    b = [
        f'<rect x="48" y="44" width="904" height="146" rx="8" fill="#20262b" stroke="#49525a" stroke-width="2"/>',
        f'<rect x="60" y="56" width="880" height="122" rx="4" fill="{lcd}"/>',
        '<clipPath id="lcd"><rect x="60" y="56" width="880" height="122"/></clipPath>',
        '<g clip-path="url(#lcd)">',
    ]
    for i, line in enumerate(textwrap.wrap(text, 72)):
        y = 92 + i * 33
        b.append(f'<text x="76" y="{y}" font-size="20" font-weight="700" fill="#1b2a0c">{line}</text>')
        b.append(f'<rect class="cov c{i}" x="66" y="{y-23}" width="872" height="32" fill="{lcd}"/>')
    b.append("</g>")

    mods = [
        ("DATA", "Tratamento e análise com Python e Pandas"),
        ("SQL", "Consultas e modelagem com SQL e MongoDB"),
        ("BI", "Dashboards e indicadores no Power BI"),
    ]
    cw, gap = 290, 12
    x0 = (w - 3 * cw - 2 * gap) / 2
    for i, (tag, desc) in enumerate(mods):
        x = x0 + i * (cw + gap)
        cx = x + cw / 2
        wire = f"M{cx} 190 V226"
        b.append(f'<path class="trace" d="{wire}"/><path class="pulse" pathLength="600" d="{wire}" style="stroke-dasharray:200 400;animation-delay:{i * .4:.1f}s"/>')
        b.append(f'<rect class="chip feat" x="{x}" y="226" width="{cw}" height="124" rx="6" style="animation-delay:{i:.0f}s"/>')
        b.append(f'<circle class="led" cx="{x+cw-20}" cy="250" r="5.5" style="animation-delay:{i * .3:.1f}s"/>')
        b.append(f'<text x="{x+14}" y="264" font-size="27" font-weight="700" class="silk">{tag}</text>')
        b.append(multiline(x + 14, 300, desc, 28, 15, "muted"))
    return svg(w, h, "Descrição geral e características", css, "".join(b))


def analyzer():
    w, h = 1000, 450
    rows = [
        ("Qualidade", "Análise, tratamento e qualidade de dados em processos de governança e privacidade (LGPD)", "10110010"),
        ("Monitoramento", "Dashboards para acompanhar os indicadores da área", "11001100"),
        ("Automação", "Automação de processos e rotinas operacionais", "10101010"),
        ("Financeiro", "Execução e controle de pagamentos via SAP", "11100010"),
        ("Documentação", "Mapeamento de processos com fluxogramas no Figma", "10011101"),
    ]
    css = """
.sq{animation:sq 4s linear infinite}
@keyframes sq{to{transform:translateX(-104px)}}
.cursor{animation:cur 6s ease-in-out infinite alternate}
@keyframes cur{from{transform:translateX(0)}to{transform:translateX(240px)}}
"""
    b = [
        f'<text x="58" y="66" font-size="22" font-weight="700" class="silk">Jovem Aprendiz · Data Governance e Privacidade de Dados</text>',
        f'<circle class="led" cx="65" cy="90" r="6"/>',
        f'<text x="82" y="96" font-size="17" class="gold">QuintoAndar · jan/2026 → atual</text>',
        f'<rect x="210" y="118" width="264" height="{5*58+8}" rx="4" fill="#04100a" stroke="#000" stroke-width="2"/>',
        f'<clipPath id="scr"><rect x="212" y="120" width="260" height="{5*58+4}"/></clipPath>',
    ]
    unit = 13
    for i, (name, desc, bits) in enumerate(rows):
        y = 126 + i * 58
        hi, lo = y + 8, y + 40
        pts = []
        level = None
        for c in range(4):
            for j, bit in enumerate(bits):
                x = c * 8 * unit + j * unit
                ny = hi if bit == "1" else lo
                pts.append(f"{'M' if level is None else 'L'}{x} {ny if level is None else level}")
                if level is not None and level != ny:
                    pts.append(f"L{x} {ny}")
                level = ny
                pts.append(f"L{x + unit} {ny}")
        b.append(
            f'<g clip-path="url(#scr)"><g transform="translate(212 0)"><path class="sq" d="{" ".join(pts)}" fill="none" stroke="{GREEN}" stroke-width="2.2" style="animation-duration:{3 + i * .6:.1f}s"/></g></g>'
        )
        b.append(f'<text x="58" y="{y+20}" font-size="13" class="gold">CH{i}</text>')
        b.append(f'<text x="58" y="{y+40}" font-size="16" class="silk">{name}</text>')
        b.append(multiline(492, y + 19 if len(desc) > 50 else y + 29, desc, 50, 16, "silk", 22))
    b.append(f'<path class="cursor" d="M222 118 V{118+5*58+8}" stroke="{GOLD}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    return svg(w, h, "Condições de operação: experiência no QuintoAndar", css, "".join(b))


def art_radar(cx, cy, r):
    rng = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r*k:.0f}" fill="none" stroke="#1d5238"/>' for k in (.33, .66, 1))
    wedge = f"M0 0 L{r} 0 A{r} {r} 0 0 0 {r*math.cos(math.radians(50)):.1f} {-r*math.sin(math.radians(50)):.1f} Z"
    route = f"M{cx-r*.7:.0f} {cy+r*.45:.0f} L{cx-r*.2:.0f} {cy+r*.3:.0f} L{cx-.1*r:.0f} {cy-r*.2:.0f} L{cx+r*.55:.0f} {cy-r*.45:.0f}"
    blips = "".join(
        f'<circle class="blip" cx="{cx+dx*r:.0f}" cy="{cy+dy*r:.0f}" r="6" fill="#f85149" style="animation-delay:{i*.7:.1f}s"/>'
        for i, (dx, dy) in enumerate(((.5, .35), (-.45, -.4), (.2, .65)))
    )
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#04100a"/>{rng}'
        f'<path d="M{cx-r} {cy} H{cx+r} M{cx} {cy-r} V{cy+r}" stroke="#1d5238"/>'
        f'<path class="route" d="{route}" fill="none" stroke="{GOLD}" stroke-width="3" stroke-linejoin="round"/>{blips}'
        f'<g transform="translate({cx} {cy})"><path class="spin" d="{wedge}" fill="{GREEN}" opacity=".35"/></g>'
    )


def art_train(x, y, w, h):
    base = y + h - 16
    ties = "".join(f'<rect x="{x+i}" y="{base-2}" width="5" height="14" fill="#49525a"/>' for i in range(4, w, 22))
    signal = []
    for i in range(0, w + 1, 6):
        spike = 34 * math.exp(-(((i - w * .72) / 13) ** 2))
        signal.append(f"{'M' if i == 0 else 'L'}{x+i} {y+40-spike-6*math.sin(i/9):.1f}")
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#04100a"/>'
        f'<path d="{" ".join(signal)}" fill="none" stroke="{GREEN}" stroke-width="2.2"/>'
        f'<circle class="blip" cx="{x+w*.72:.0f}" cy="{y+6}" r="7" fill="none" stroke="#f85149" stroke-width="2.5"/>'
        f'<text x="{x+w*.72+14:.0f}" y="{y+18}" font-size="13" fill="#f85149">falha prevista</text>'
        f'{ties}<path d="M{x} {base} H{x+w}" stroke="#c7ccd1" stroke-width="3"/>'
        f'<clipPath id="rail"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
        f'<g clip-path="url(#rail)"><g class="ride"><rect x="{x-110}" y="{base-34}" width="96" height="30" rx="6" fill="{GOLD}"/>'
        f'<rect x="{x-100}" y="{base-28}" width="20" height="11" fill="#04100a"/><rect x="{x-72}" y="{base-28}" width="20" height="11" fill="#04100a"/><rect x="{x-44}" y="{base-28}" width="20" height="11" fill="#04100a"/></g></g>'
    )


def art_scatter(x, y, w, h):
    rnd = random.Random(7)
    dots = "".join(
        f'<circle cx="{x + w*.36 + rnd.gauss(0, 42):.0f}" cy="{y + h*.55 + rnd.gauss(0, 18):.0f}" r="3.2" fill="{GREEN}" opacity=".8"/>'
        for _ in range(70)
    )
    ax, ay = x + w * .84, y + h * .24
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#04100a"/>{dots}'
        f'<circle cx="{ax:.0f}" cy="{ay:.0f}" r="6" fill="#f85149"/>'
        f'<circle class="blip" cx="{ax:.0f}" cy="{ay:.0f}" r="15" fill="none" stroke="#f85149" stroke-width="2.5"/>'
        f'<text x="{ax-22:.0f}" y="{ay+5:.0f}" font-size="13" fill="#f85149" text-anchor="end">anomalia</text>'
    )


CARD_CSS = f"""
.spin{{animation:spin 4s linear infinite}}
@keyframes spin{{to{{transform:rotate(-360deg)}}}}
.blip{{animation:blink 1.8s ease-in-out infinite}}
.route{{stroke-dasharray:9 7;animation:route 1.5s linear infinite}}
@keyframes route{{to{{stroke-dashoffset:-32}}}}
.ride{{animation:ride 8s linear infinite}}
@keyframes ride{{to{{transform:translateX(580px)}}}}
.tag{{fill:#1a2a22;stroke:#2f5d45}}
"""


def tags_row(x, y, tags):
    out = []
    for tag in tags:
        tw = len(tag) * 9 + 18
        out.append(f'<rect class="tag" x="{x}" y="{y-19}" width="{tw}" height="27" rx="5"/><text x="{x+9}" y="{y}" font-size="15" class="green">{tag}</text>')
        x += tw + 8
    return "".join(out)


def status(x, y, label, active):
    dot = f'<circle class="led" cx="{x}" cy="{y-5}" r="5.5"/>' if active else f'<circle cx="{x}" cy="{y-5}" r="5.5" fill="{GOLD}"/>'
    return dot + f'<text x="{x+14}" y="{y}" font-size="14" class="muted">{label}</text>'


def project_wide():
    w, h = 1000, 330
    b = [
        art_radar(180, 165, 125),
        '<text x="350" y="60" font-size="16" class="gold">A1 · PROJETO PRINCIPAL</text>',
        status(780, 60, "em andamento", True),
        '<text x="350" y="108" font-size="36" font-weight="700" class="silk">Radar Urbano</text>',
        multiline(350, 146, "Sistema web que indica as rotas mais seguras e eficientes da cidade com Machine Learning, mapeia áreas de risco em dashboards de BI e usa um LLM para classificar as ocorrências relatadas pelos usuários.", 58, 18, "silk", 27),
        tags_row(350, 272, ["ML", "LLM", "BI", "Geoespacial"]),
        '<text x="952" y="295" font-size="14" class="green" text-anchor="end">abrir repositório →</text>',
    ]
    return svg(w, h, "Radar Urbano", CARD_CSS, "".join(b))


def project_card(ref, title, label, active, desc, tags, art, link=False):
    w, h = 500, 400
    b = [
        f'<text x="48" y="44" font-size="15" class="gold">{ref}</text>',
        status(310, 44, label, active),
        art(36, 62, 428, 130),
        f'<text x="36" y="232" font-size="22" font-weight="700" class="silk">{title}</text>',
        multiline(36, 262, desc, 47, 16, "silk", 22),
        tags_row(36, 350, tags),
    ]
    if link:
        b.append('<text x="444" y="381" font-size="13" class="green" text-anchor="end">abrir repositório →</text>')
    return svg(w, h, title, CARD_CSS, "".join(b))


def label():
    w, h = 1000, 340
    css = """
.laser{animation:laser 3.5s ease-in-out infinite alternate}
@keyframes laser{from{transform:translateX(0)}to{transform:translateX(286px)}}
.mask{animation:mask 4s steps(1) infinite}
@keyframes mask{0%,100%{fill:#111}50%{fill:#333}}
"""
    paper = "#f4f1e6"
    ink = "#141414"
    x, y, lw, lh = 56, 36, 888, 268
    b = [f'<rect x="{x}" y="{y}" width="{lw}" height="{lh}" rx="8" fill="{paper}"/>']
    b.append(f'<text x="{x+26}" y="{y+40}" font-size="24" font-weight="800" fill="{ink}">Gabriel-SP</text>')
    b.append(f'<path d="M{x+26} {y+54} H{x+540}" stroke="{ink}" stroke-width="2"/>')
    fields = [("LOCAL", "São Paulo, SP"), ("LINKEDIN", "linkedin.com/in/gabrielsouza7"), ("E-MAIL", "contact.gabriels7@gmail.com")]
    for i, (k, v) in enumerate(fields):
        fy = y + 88 + i * 38
        b.append(f'<text x="{x+26}" y="{fy}" font-size="14" fill="#555">{k}</text><text x="{x+122}" y="{fy}" font-size="18" font-weight="700" fill="{ink}">{v}</text>')
    fy = y + 88 + 3 * 38
    b.append(f'<text x="{x+26}" y="{fy}" font-size="14" fill="#555">TELEFONE</text>')
    b.append(f'<rect class="mask" x="{x+122}" y="{fy-17}" width="176" height="23" fill="#111"/>')
    b.append(f'<text x="{x+310}" y="{fy}" font-size="15" fill="{ink}">anonimizado, afinal: LGPD</text>')
    b.append(f'<text x="{x+26}" y="{y+250}" font-size="12" fill="#555">Manusear com cuidado: contém dados tratados conforme a LGPD.</text>')

    # Código de barras decorativo, gerado a partir do código do componente.
    bx, by, bh = x + 575, y + 34, 166
    cursor = bx
    for byte in "Gabriel-SP".encode() * 2:
        for k in range(5):
            bar = 2 + (byte >> k & 1) * 3
            gap = 2 + (byte >> (k + 1) & 1) * 2
            if cursor + bar > bx + 286:
                break
            b.append(f'<rect x="{cursor}" y="{by}" width="{bar}" height="{bh}" fill="{ink}"/>')
            cursor += bar + gap
    b.append(f'<path class="laser" d="M{bx} {by-10} V{by+bh+10}" stroke="#ff2b2b" stroke-width="2.5"/>')
    b.append(f'<text x="{bx+143}" y="{by+bh+32}" font-size="16" fill="{ink}" text-anchor="middle" letter-spacing="3">Gabriel-SP</text>')
    return svg(w, h, "Etiqueta com informações de contato", css, "".join(b))


def button(name, value):
    w, h = 490, 100
    pins = "".join(f'<rect x="{w-52-i*16}" y="{(h-34)/2}" width="10" height="34" rx="1" fill="{GOLD}"/>' for i in range(4))
    b = [
        f'<text x="58" y="44" font-size="15" class="gold">{name}</text>',
        f'<text x="58" y="72" font-size="20" font-weight="700" class="silk">{value}</text>',
        pins,
    ]
    return svg(w, h, name, "", "".join(b))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    assets = {
        "hero": hero(),
        "pinout": pinout(),
        "path": path(),
        "description": description(),
        "analyzer": analyzer(),
        "project-radar": project_wide(),
        "project-motiva": project_card("A2", "Challenge FIAP + Motiva", "em andamento", True, "Prevê falhas em equipamentos que operam nos trilhos de trem de São Paulo, para reduzir paradas não programadas.", ["ML", "Sensores"], art_train),
        "project-leak": project_card("A3", "Vazamento de Dados", "em andamento", True, "Encontra possíveis vazamentos de dados corporativos com detecção de anomalias e auditoria de acessos.", ["Python", "MongoDB", "SQL", "Power BI"], art_scatter),
        "label": label(),
        "btn-linkedin": button("LINKEDIN", "gabrielsouza7"),
        "btn-email": button("E-MAIL", "contact.gabriels7@gmail.com"),
    }
    for name, content in assets.items():
        (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
