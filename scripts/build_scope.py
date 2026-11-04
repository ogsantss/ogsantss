"""Desenha o osciloscópio do perfil com as contribuições reais dos últimos 12 meses.

Uso: python scripts/build_scope.py <usuario> <arquivo.svg>
"""
import math
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

GREEN = "#39d353"
GOLD = "#d9a441"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"
MONTHS = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]


def fetch_days(user):
    """Lê a página pública do gráfico de contribuições e devolve {data: quantidade}."""
    url = f"https://github.com/users/{user}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (profile-readme)"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

    dates = {}
    for tag in re.findall(r"<td\b[^>]*data-date[^>]*>", html):
        dates[re.search(r'\bid="([^"]+)"', tag)[1]] = re.search(r'data-date="([\d-]+)"', tag)[1]
    days = {}
    for target, text in re.findall(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        if target in dates:
            count = re.match(r"([\d,]+) contribution", text)
            days[dates[target]] = int(count[1].replace(",", "")) if count else 0
    if len(days) < 300:
        raise SystemExit(f"Formato da página mudou: só {len(days)} dias lidos")
    return days


def weekly(days):
    weeks = defaultdict(int)
    first = min(date.fromisoformat(d) for d in days)
    for d, n in days.items():
        weeks[(date.fromisoformat(d) - first).days // 7] += n
    return [weeks[i] for i in range(max(weeks) + 1)], first


def smooth(points):
    """Curva suave passando pelos pontos, como um traço de osciloscópio."""
    d = f"M{points[0][0]:.1f} {points[0][1]:.1f}"
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        mx = (x0 + x1) / 2
        d += f" C{mx:.1f} {y0:.1f} {mx:.1f} {y1:.1f} {x1:.1f} {y1:.1f}"
    return d


def build(days):
    series, first = weekly(days)
    total = sum(days.values())
    peak = max(series)
    last = max((d for d, c in days.items() if c), default=None)
    last = date.fromisoformat(last).strftime("%d/%m") if last else "--"

    w, h = 1000, 420
    sx, sy, sw, sh = 40, 44, 720, 332
    top = math.sqrt(max(peak, 1))
    n = len(series) - 1
    # Escala de raiz quadrada: semanas pequenas continuam visíveis ao lado de um pico.
    points = [(sx + i * sw / n, sy + sh - 18 - math.sqrt(v) / top * (sh - 40)) for i, v in enumerate(series)]
    trace = smooth(points)

    grid = []
    for i in range(1, 12):
        x = sx + i * sw / 12
        grid.append(f'<path d="M{x:.0f} {sy} V{sy+sh}"/>')
    for i in range(1, 8):
        y = sy + i * sh / 8
        grid.append(f'<path d="M{sx} {y:.0f} H{sx+sw}"/>')

    labels = []
    seen = set()
    for i in range(0, len(series), 1):
        m = date.fromordinal(first.toordinal() + i * 7)
        key = (m.year, m.month)
        if key not in seen and m.day <= 7 and m.month % 2 == 1:
            seen.add(key)
            labels.append(f'<text x="{sx + i * sw / n:.0f}" y="{sy+sh-6}" font-size="12" fill="#5f8f73">{MONTHS[m.month-1]}</text>')

    def readout(y, label, value):
        return (
            f'<text x="796" y="{y}" font-size="13" fill="#8fa89b">{label}</text>'
            f'<text x="796" y="{y+32}" font-size="30" font-weight="700" fill="{GREEN}">{value}</text>'
        )

    knobs = "".join(
        f'<circle cx="{x}" cy="358" r="19" fill="#20262b" stroke="#49525a" stroke-width="2"/>'
        f'<path d="M{x} 358 L{x+dx} 345" stroke="{GOLD}" stroke-width="3" stroke-linecap="round"/>'
        for x, dx in ((822, -7), (880, 6), (938, 0))
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">
<title>Osciloscópio: {total} contribuições nos últimos 12 meses</title>
<style>
text{{font-family:{MONO}}}
.sweep{{stroke-dasharray:1000;animation:sweep 7s linear infinite}}
@keyframes sweep{{from{{stroke-dashoffset:1000}}70%,100%{{stroke-dashoffset:0}}}}
.led{{animation:blink 1.4s steps(2) infinite}}
@keyframes blink{{50%{{opacity:.2}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<defs><filter id="glow" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="screen"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="8"/></clipPath></defs>
<rect width="{w}" height="{h}" rx="16" fill="#171b1f"/>
<rect x="8" y="8" width="{w-16}" height="{h-16}" rx="11" fill="none" stroke="#2c3338" stroke-width="2"/>
<text x="{sx}" y="31" font-size="14" fill="#8fa89b">CH1 · CONTRIBUIÇÕES POR SEMANA · 12 MESES · ESCALA √</text>
<circle class="led" cx="{sx+sw-8}" cy="26" r="5" fill="{GREEN}"/>
<text x="{sx+sw-20}" y="31" font-size="14" fill="{GREEN}" text-anchor="end">DADO REAL</text>
<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="8" fill="#04100a" stroke="#000" stroke-width="3"/>
<g clip-path="url(#screen)">
<g stroke="#123524" stroke-width="1">{''.join(grid)}</g>
<path d="M{sx+sw/2} {sy} V{sy+sh}M{sx} {sy+sh/2} H{sx+sw}" stroke="#1d5238" stroke-width="1.2"/>
{''.join(labels)}
<path d="{trace}" fill="none" stroke="{GREEN}" stroke-width="1.5" opacity=".4"/>
<path class="sweep" pathLength="1000" d="{trace}" fill="none" stroke="{GREEN}" stroke-width="2.6" filter="url(#glow)"/>
</g>
{readout(66, "TOTAL / 12 MESES", total)}
{readout(136, "PICO / SEMANA", peak)}
{readout(206, "ÚLTIMA ATIVIDADE", last)}
<g font-size="12" fill="#8fa89b" text-anchor="middle"><text x="822" y="326">POS</text><text x="880" y="326">ESC</text><text x="938" y="326">TRIG</text></g>
{knobs}
<text x="{sx}" y="400" font-size="12" fill="#6d7a72">atualizado em {date.today().strftime('%d/%m/%Y')} a partir do GitHub</text>
</svg>
"""


if __name__ == "__main__":
    user, target = sys.argv[1], Path(sys.argv[2])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build(fetch_days(user)), encoding="utf-8")
