#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2", "pyyaml"]
# ///
"""Build the Cradio cheatsheet HTMLs from data.yml + templates/."""
from __future__ import annotations
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml

ROOT = Path(__file__).parent
SITE_OUT = Path("/Users/cedar/cedar.ren/pages/cradio_android")

# Colemak-DH key layouts (row, col)
L_LAYOUT = [['Q','W','F','P','B'],['A','R','S','T','G'],['Z','X','C','D','V']]
R_LAYOUT = [['J','L','U','Y',"'"],['M','N','E','I','O'],['K','H',',','.','?']]

# SVG geometry
C, G = 13, 1.5
P = C + G
HW = 5*C + 4*G       # half-width
HH = 3*C + 2*G       # half-height


def _hand(layout, x_off, y_off, hits, with_labels, home_dot_at):
    """Yield SVG fragments for one hand."""
    out = []
    for r in range(3):
        for c in range(5):
            k = layout[r][c]
            on = k in hits
            x = x_off + c*P
            y = y_off + r*P
            cls = 'k on' if on else 'k'
            out.append(f'<rect x="{x:g}" y="{y:g}" width="{C}" height="{C}" rx="1.2" class="{cls}"/>')
            if with_labels == 'all' or (with_labels == 'on' and on):
                lcls = 'lbl on' if on else 'lbl'
                out.append(f'<text x="{x+C/2:g}" y="{y+C/2+0.3:g}" class="{lcls}">{_esc(k)}</text>')
            if home_dot_at and (r, c) == home_dot_at:
                cx, cy = x + C/2, y + C + 1.5
                out.append(f'<polygon points="{cx:g},{cy:g} {cx-1.5:g},{cy+1.8:g} {cx+1.5:g},{cy+1.8:g}" class="home"/>')
    return out


def _esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                  .replace('"', '&quot;'))


def render_diagram(spec=None, *, labels='none', home_dots=False, fluid=False,
                   left=None, right=None, thumbs=None):
    """Render an SVG mini-keyboard diagram.

    spec: dict like {'left': [...], 'right': [...], 'thumbs': [...]}
    Or pass left/right/thumbs as kwargs.
    """
    if spec is None:
        spec = {}
    left = list(spec.get('left', left or []))
    right = list(spec.get('right', right or []))
    thumbs = list(spec.get('thumbs', thumbs or []))
    left_set = set(str(k).upper() if len(str(k))==1 and str(k).isalpha() else str(k) for k in left)
    right_set = set(str(k).upper() if len(str(k))==1 and str(k).isalpha() else str(k) for k in right)
    thumb_set = set(thumbs)
    has_grid = bool(left or right) or 'left' in spec or 'right' in spec
    thumbs_only = bool(thumb_set) and not has_grid

    if thumbs_only:
        return _render_thumbs_only(thumb_set)

    # full grid (always show both hands for context)
    gap = 8
    w = HW + gap + HW
    show_thumbs = bool(thumb_set)
    th_y = HH + 4
    th_r = 4
    h = HH + (th_r*2 + 5 if show_thumbs else 0)

    parts = [f'<svg class="kbmap" viewBox="0 0 {w:g} {h:g}"']
    if fluid:
        parts.append(' style="width:100%;max-width:320px;height:auto"')
    else:
        parts.append(f' width="{w:g}" height="{h:g}"')
    parts.append('>')

    home_l = (1, 3) if home_dots else None  # T position
    home_r = (1, 1) if home_dots else None  # N position
    parts.extend(_hand(L_LAYOUT, 0, 0, left_set, labels, home_l))
    parts.extend(_hand(R_LAYOUT, HW + gap, 0, right_set, labels, home_r))

    cx = HW + gap/2
    parts.append(f'<line x1="{cx:g}" y1="0" x2="{cx:g}" y2="{HH:g}" class="divide"/>')

    if show_thumbs:
        # left thumbs under cols 3,4 (LO at col 3, LI at col 4)
        parts.append(f'<circle cx="{3*P + C/2:g}" cy="{th_y+th_r:g}" r="{th_r}" class="t{" on" if "LO" in thumb_set else ""}"/>')
        parts.append(f'<circle cx="{4*P + C/2:g}" cy="{th_y+th_r:g}" r="{th_r}" class="t{" on" if "LI" in thumb_set else ""}"/>')
        x_off = HW + gap
        parts.append(f'<circle cx="{x_off + 0*P + C/2:g}" cy="{th_y+th_r:g}" r="{th_r}" class="t{" on" if "RI" in thumb_set else ""}"/>')
        parts.append(f'<circle cx="{x_off + 1*P + C/2:g}" cy="{th_y+th_r:g}" r="{th_r}" class="t{" on" if "RO" in thumb_set else ""}"/>')

    parts.append('</svg>')
    return ''.join(parts)


def _render_thumbs_only(thumb_set):
    r = 5.5
    gap = 5
    div_w = 14
    order = ['LO','LI','RI','RO']
    total_w = 4*(2*r) + 2*gap + div_w + 4
    h = 2*r + 14
    parts = [f'<svg class="kbmap" width="{total_w:g}" height="{h:g}" viewBox="0 0 {total_w:g} {h:g}">']
    x = r + 2
    pos = []
    for i, k in enumerate(order):
        pos.append((k, x))
        cls = 't on' if k in thumb_set else 't'
        parts.append(f'<circle cx="{x:g}" cy="{r+2:g}" r="{r}" class="{cls}"/>')
        if i == 1:
            x += 2*r + div_w
        elif i < 3:
            x += 2*r + gap
    div_x = total_w / 2
    parts.append(f'<line x1="{div_x:g}" y1="0" x2="{div_x:g}" y2="{2*r+4:g}" class="divide"/>')
    l_lbl = (pos[0][1] + pos[1][1]) / 2
    r_lbl = (pos[2][1] + pos[3][1]) / 2
    parts.append(f'<text x="{l_lbl:g}" y="{2*r+11:g}" class="handlbl">L</text>')
    parts.append(f'<text x="{r_lbl:g}" y="{2*r+11:g}" class="handlbl">R</text>')
    parts.append('</svg>')
    return ''.join(parts)


def render_inline_diagram(spec):
    """Inline mid-sentence diagram — same as render_diagram but with vertical-align style."""
    svg = render_diagram(spec)
    return svg.replace('<svg class="kbmap"', '<svg class="kbmap inline"', 1)


def render_keys(items):
    """Render the `keys:` array — list of {kbd|tag|plus|sep|diagram|inline_diagram} dicts."""
    out = []
    for it in items or []:
        if 'kbd' in it:
            out.append(f'<kbd>{_esc(it["kbd"])}</kbd>')
        elif 'tag' in it:
            out.append(f'<kbd class="tag">{_esc(it["tag"])}</kbd>')
        elif 'plus' in it:
            out.append('<span class="plus">+</span>')
        elif 'sep' in it:
            out.append(f'<span class="sep">{_esc(it["sep"])}</span>')
        elif 'inline_diagram' in it:
            out.append(render_inline_diagram(it['inline_diagram']))
        elif 'diagram' in it:
            out.append(render_diagram(it['diagram']))
    return ' '.join(out)


def render_intro_diagram():
    return render_diagram({'left': [], 'right': []}, labels='all', home_dots=True, fluid=True)


def main():
    data = yaml.safe_load((ROOT / 'data.yml').read_text())

    env = Environment(
        loader=FileSystemLoader(ROOT / 'templates'),
        autoescape=select_autoescape(['html']),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals.update(
        render_keys=render_keys,
        render_diagram=render_diagram,
        render_intro_diagram=render_intro_diagram,
    )

    SITE_OUT.mkdir(parents=True, exist_ok=True)
    targets = [
        ('v1.html.j2', 'v1-current.html'),
        ('v2.html.j2', 'v2-technical-manual.html'),
        ('v3.html.j2', 'v3-tech-manual-dark.html'),
    ]
    for tpl_name, out_name in targets:
        tpl_path = ROOT / 'templates' / tpl_name
        if not tpl_path.exists():
            print(f"skip: {tpl_name} (no template)")
            continue
        tpl = env.get_template(tpl_name)
        html = tpl.render(**data)
        (SITE_OUT / out_name).write_text(html)
        print(f"wrote {SITE_OUT / out_name}")


if __name__ == '__main__':
    main()
