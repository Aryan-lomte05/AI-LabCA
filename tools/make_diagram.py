"""Generate the rule-dependency diagram (docs/img/rule_dependency.svg)."""

from pathlib import Path

W, H, BW, BH = 1290, 580, 170, 46
COLX = [20, 230, 440, 650, 860, 1080]
STYLE = {  # fill, stroke
    "in": ("#eceff1", "#607d8b"), "val": ("#fde0dc", "#b7202e"),
    "der": ("#e3f2fd", "#1565c0"), "cls": ("#fff3e0", "#ef6c00"),
    "alert": ("#fce4ec", "#b7202e"), "adv": ("#e8f5e9", "#2e7d32"),
}
N = {  # id: (col, y, title, subtitle, style)
    "region": (0, 30, "region", "plains / coastal / hilly", "in"),
    "tmax": (0, 95, "tmax", "max temperature", "in"),
    "norm": (0, 160, "tmax_normal", "climatological normal", "in"),
    "days": (0, 225, "heat_days", "persistence", "in"),
    "rh": (0, 290, "rh", "relative humidity", "in"),
    "tmin": (0, 355, "tmin, tmin_normal", "night temperature", "in"),
    "sym": (0, 430, "symptoms", "citizen / health", "in"),
    "role": (0, 505, "role, vulnerable, farm", "stakeholder profile", "in"),
    "thr": (1, 30, "threshold_met", "C1-C3", "cls"),
    "dep": (1, 125, "departure", "D1", "der"),
    "hi": (1, 290, "heat_index", "D3 (Rothfusz)", "der"),
    "tdep": (1, 355, "tmin_departure", "D2", "der"),
    "hri": (1, 430, "hri", "T1-T4 triage", "val"),
    "valid": (1, 505, "error -> HALT", "V1-V5, D0: all numeric inputs", "val"),
    "cat": (2, 80, "hw_category", "C4-C8 (IMD)", "cls"),
    "hil": (2, 290, "hi_level", "H1-H4", "cls"),
    "night": (2, 355, "night", "W1-W2 warm night", "cls"),
    "emer": (2, 430, "EMERGENCY / first aid", "T5-T7", "val"),
    "alert": (3, 150, "alert (+status)", "A1-A8 colour code", "alert"),
    "esc": (4, 250, "alert (escalated)", "E1-E3", "alert"),
    "gov": (5, 110, "needs_review", "G1 human-in-loop", "adv"),
    "rec": (5, 190, "recommendation", "K1 summary", "adv"),
    "adv": (5, 300, "stakeholder advice", "P/F/M/X rules + role profile", "adv"),
    "gap": (5, 395, "data-gap notes", "G2-G3: rh / tmin missing", "adv"),
}
E = [("region", "thr"), ("tmax", "thr"), ("tmax", "dep"), ("norm", "dep"), ("tmax", "hi"),
     ("rh", "hi"), ("tmin", "tdep"), ("sym", "hri"), ("thr", "cat"), ("dep", "cat"),
     ("tmax", "cat"), ("hi", "hil"), ("tdep", "night"), ("hri", "emer"), ("cat", "alert"),
     ("days", "alert"), ("alert", "esc"), ("night", "esc"), ("hil", "esc"), ("esc", "gov"),
     ("esc", "rec"), ("esc", "adv")]


def box(k):
    c, y, *_ = N[k]
    return COLX[c], y


out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'viewBox="0 0 {W} {H}" font-family="Carlito, Calibri, Arial, sans-serif">',
       '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
       'markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#78909c"/>'
       '</marker></defs>', f'<rect width="{W}" height="{H}" fill="white"/>']
for s, t in E:
    x1, y1 = box(s)
    x2, y2 = box(t)
    x1, y1, x2, y2 = x1 + BW, y1 + BH / 2, x2, y2 + BH / 2
    mx = (x1 + x2) / 2
    out.append(f'<path d="M{x1},{y1} C{mx},{y1} {mx},{y2} {x2 - 2},{y2}" fill="none" '
               f'stroke="#90a4ae" stroke-width="1.4" marker-end="url(#a)"/>')
for k, (c, y, title, sub, st) in N.items():
    fill, stroke = STYLE[st]
    x = COLX[c]
    out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="8" fill="{fill}" '
               f'stroke="{stroke}" stroke-width="1.6"/>')
    out.append(f'<text x="{x + BW / 2}" y="{y + 19}" text-anchor="middle" font-size="14" '
               f'font-weight="bold" fill="#263238">{title}</text>')
    out.append(f'<text x="{x + BW / 2}" y="{y + 36}" text-anchor="middle" font-size="11.5" '
               f'fill="#455a64">{sub}</text>')
heads = ["User inputs", "Validation / derivation", "Classification", "IMD alert",
         "Escalation", "Conclusions"]
for x, h in zip(COLX, heads):
    out.append(f'<text x="{x + BW / 2}" y="18" text-anchor="middle" font-size="13" '
               f'fill="#b7202e" font-weight="bold">{h}</text>')
out.append("</svg>")
Path(__file__).resolve().parent.parent.joinpath("docs/img/rule_dependency.svg").write_text(
    "\n".join(out), encoding="utf-8")
print("written")
