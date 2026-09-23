#!/usr/bin/env python3
"""Generate docs/diagrams/aloop.svg — "Aladin's Loop (aloop)": the agentic-agile sprint
lifecycle as a 16:9 architecture infographic (light canvas; blue + gold system).

Readable as a real architecture diagram with every genie removed: numbered panels,
labelled arrows (blue = execution, amber dashed = re-plan, teal = state), the sprint
boundary (checkpoint → deterministic context clear → fresh context), and real file /
script names from plugin/.

    python3 docs/diagrams/gen_aloop.py
"""
import math
import os
from xml.sax.saxutils import escape

W, H = 1920, 1080
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

NAVY, NAVY2 = "#13235a", "#1f3a8a"
BLUE, CYAN = "#2f64d6", "#1596c4"
GOLD, GOLD_D, GOLD_L = "#dca127", "#95600f", "#fff3d3"
VIOLET, VIOLET_L = "#6d45c9", "#f1ecfd"
GREEN, GREEN_L = "#138a58", "#e7f7ef"
AMBER = "#cf7a12"
TEAL, TEAL_L = "#0e8a8a", "#e3f6f5"
TXT, MUTED, LINE = "#1b2540", "#5a6683", "#cdd8ee"
SKIN, SKIN_D, TURBAN, VEST = "#5b8ff5", "#3e6ed8", "#22398f", "#1c2f6e"

out = []
add = out.append


def t(x, y, s, size=14, fill=TXT, weight=400, anchor="start", font=SANS, italic=False, ls=None, rot=None):
    add('<text x="%g" y="%g" font-size="%g" fill="%s" font-weight="%d" text-anchor="%s" font-family="%s"%s%s%s>%s</text>'
        % (x, y, size, fill, weight, anchor, font, ' font-style="italic"' if italic else "",
           ' letter-spacing="%g"' % ls if ls else "", ' transform="rotate(%g %g %g)"' % (rot, x, y) if rot else "", escape(s)))


def rect(x, y, w, h, fill="#fff", stroke=LINE, r=12, sw=1.2, extra=""):
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s" stroke="%s" stroke-width="%g" %s/>'
        % (x, y, w, h, r, fill, stroke, sw, extra))


def arrow(d, color, sw=5, dash=None, head=True):
    add('<path d="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round" stroke-linejoin="round"%s%s/>'
        % (d, color, sw, ' stroke-dasharray="%s"' % dash if dash else "",
           ' marker-end="url(#ah-%s)"' % color.strip("#") if head else ""))


def tag(cx, cy, s, color, fill="#ffffff", size=12.5, mono=False):
    w = len(s) * (size * 0.62 if mono else size * 0.66 + 1) + 24
    rect(cx - w / 2, cy - 13, w, 26, fill=fill, stroke=color, r=13, sw=1.5)
    t(cx, cy + 4.5, s, size=size, fill=color, weight=750, anchor="middle", font=MONO if mono else SANS, ls=None if mono else 1)
    return w


ICON = {
    "chat": '<rect x="0" y="1" width="20" height="15" rx="4" fill="none" stroke="{c}" stroke-width="2"/><path d="M5 16 l-2 5 l6 -5" fill="{c}"/><circle cx="6" cy="8.5" r="1.5" fill="{c}"/><circle cx="10" cy="8.5" r="1.5" fill="{c}"/><circle cx="14" cy="8.5" r="1.5" fill="{c}"/>',
    "doc": '<path d="M3 0 h10 l6 6 v14 h-16 z" fill="none" stroke="{c}" stroke-width="2"/><path d="M6 10 h9 M6 14 h9" stroke="{c}" stroke-width="1.6"/>',
    "tree": '<rect x="1" y="1" width="7" height="6" rx="1.5" fill="none" stroke="{c}" stroke-width="1.8"/><rect x="12" y="7" width="7" height="6" rx="1.5" fill="none" stroke="{c}" stroke-width="1.8"/><rect x="12" y="15" width="7" height="5" rx="1.5" fill="none" stroke="{c}" stroke-width="1.8"/><path d="M4.5 7 v10.5 h7.5 M4.5 10 h7.5" fill="none" stroke="{c}" stroke-width="1.6"/>',
    "rules": '<path d="M10 0 l9 4 v6 c0 6 -4 9 -9 11 c-5 -2 -9 -5 -9 -11 v-6 z" fill="none" stroke="{c}" stroke-width="2"/><path d="M6 10 l3 3 l5 -6" fill="none" stroke="{c}" stroke-width="2"/>',
    "check": '<circle cx="10" cy="10" r="10" fill="{c}"/><path d="M5 10.5 l3.5 3.5 l6.5 -7.5" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>',
    "play": '<circle cx="10" cy="10" r="10" fill="{c}"/><path d="M8 5.5 l7 4.5 l-7 4.5 z" fill="#fff"/>',
    "bars": '<rect x="1" y="11" width="4" height="8" rx="1" fill="{c}"/><rect x="8" y="6" width="4" height="13" rx="1" fill="{c}"/><rect x="15" y="1" width="4" height="18" rx="1" fill="{c}"/>',
    "gauge": '<path d="M2 16 a8 8 0 0 1 16 0" fill="none" stroke="{c}" stroke-width="2.4"/><path d="M10 16 l5 -6" stroke="{c}" stroke-width="2.2" stroke-linecap="round"/><circle cx="10" cy="16" r="2" fill="{c}"/>',
    "alert": '<path d="M10 1 l9.5 17 h-19 z" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round"/><path d="M10 7 v5" stroke="{c}" stroke-width="2.2" stroke-linecap="round"/><circle cx="10" cy="15" r="1.3" fill="{c}"/>',
    "cycle": '<path d="M16 6 a7.5 7.5 0 1 0 1.5 6" fill="none" stroke="{c}" stroke-width="2.2"/><path d="M12 5 h5 v-5" fill="none" stroke="{c}" stroke-width="2.2"/>',
    "people": '<circle cx="6" cy="6" r="3.5" fill="{c}"/><circle cx="14" cy="6" r="3.5" fill="{c}"/><path d="M0 18 c0 -6 12 -6 12 0 M8 18 c0 -6 12 -6 12 0" fill="{c}"/>',
    "lock": '<rect x="2" y="8" width="16" height="12" rx="2.5" fill="none" stroke="{c}" stroke-width="2"/><path d="M6 8 v-3 a4 4 0 0 1 8 0 v3" fill="none" stroke="{c}" stroke-width="2"/>',
    "brain": '<path d="M10 2 c-5 0 -8 4 -7 8 c-2 3 0 8 5 8 h4 c5 0 7 -5 5 -8 c1 -4 -2 -8 -7 -8 z" fill="none" stroke="{c}" stroke-width="2"/><path d="M10 3 v15" stroke="{c}" stroke-width="1.5"/>',
    "code": '<path d="M6 4 l-5 6 l5 6 M14 4 l5 6 l-5 6" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round"/>',
    "hook": '<path d="M10 1 v10 a5 5 0 1 1 -8 -4" fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round"/><circle cx="10" cy="2" r="2" fill="{c}"/>',
}


def icon(name, x, y, color, s=1.0):
    add('<g transform="translate(%g %g) scale(%g)">%s</g>' % (x, y, s, ICON[name].replace("{c}", color)))


def item(x, y, ic, label, sub=None, color=BLUE, sub_mono=True):
    icon(ic, x, y - 15, color)
    t(x + 30, y, label, size=15, fill=TXT, weight=650)
    if sub:
        t(x + 30, y + 18, sub, size=12.5, fill=MUTED, font=MONO if sub_mono else SANS)


# ── genie (original design) + props ─────────────────────────────────────────
GENIE = (
    '<symbol id="genie" viewBox="0 0 80 104" width="80" height="104">'
    '<path d="M40 62 C16 68 20 90 36 92 C52 94 46 103 30 102 C54 106 62 88 47 82 C37 78 45 68 56 66 Z" fill="%s" opacity=".9"/>' % SKIN_D +
    '<path d="M22 66 C22 48 58 48 58 66 L54 76 C46 80 34 80 26 76 Z" fill="%s"/>' % SKIN +
    '<path d="M27 53 C33 59 47 59 53 53 L51 73 C45 76 35 76 29 73 Z" fill="%s"/>' % VEST +
    '<path d="M31 53 L40 72 L49 53" fill="none" stroke="%s" stroke-width="2.4"/>' % GOLD +
    '<path d="M29 58 C31 62 33 64 35 65 M51 58 C49 62 47 64 45 65" fill="none" stroke="%s" stroke-width="1.4"/>' % GOLD +
    '<ellipse cx="40" cy="34" rx="17" ry="18" fill="%s"/>' % SKIN +
    '<ellipse cx="23" cy="35" rx="3" ry="4.8" fill="%s"/><ellipse cx="57" cy="35" rx="3" ry="4.8" fill="%s"/>' % (SKIN_D, SKIN_D) +
    '<path d="M22 26 C22 5 58 5 58 26 C51 19 29 19 22 26 Z" fill="%s"/>' % TURBAN +
    '<path d="M40 9 C44 1 53 1 51 -5" fill="none" stroke="%s" stroke-width="4.5" stroke-linecap="round"/>' % TURBAN +
    '<circle cx="40" cy="20" r="3.8" fill="%s" stroke="#fff3c4" stroke-width="1.2"/>' % GOLD +
    '<rect x="27.5" y="29" width="11" height="10" rx="4" fill="#eaf2ff" stroke="#14192a" stroke-width="2"/><rect x="41.5" y="29" width="11" height="10" rx="4" fill="#eaf2ff" stroke="#14192a" stroke-width="2"/>'
    '<path d="M38.5 33 h3" stroke="#14192a" stroke-width="2"/><circle cx="33.5" cy="34.5" r="2" fill="#14192a"/><circle cx="47.5" cy="34.5" r="2" fill="#14192a"/>'
    '<path d="M28 26 q5 -3 9 0 M43 26 q5 -3 9 0" fill="none" stroke="#14192a" stroke-width="1.8" stroke-linecap="round"/>'
    '<path d="M33 43.5 q7 -4 14 0 q-7 2 -14 0 z" fill="#14192a"/>'
    '<path d="M35 46.5 C38 49.5 42 49.5 45 46.5" fill="none" stroke="#14192a" stroke-width="1.8" stroke-linecap="round"/>'
    '</symbol>')


def genie(x, y, s=1.0, prop=None):
    add('<use href="#genie" transform="translate(%g %g) scale(%g)"/>' % (x, y, s))
    g = lambda body: add('<g transform="translate(%g %g) scale(%g)">%s</g>' % (x, y, s, body))
    if prop == "intent":
        g('<g transform="translate(54 40) rotate(-10)"><rect width="48" height="58" rx="4" fill="#f6e2ab" stroke="%s" stroke-width="2"/>'
          '<rect x="-4" y="-4" width="56" height="66" rx="7" fill="none" stroke="%s" stroke-opacity=".45" stroke-width="3"/>'
          '<text x="24" y="16" font-size="10" font-weight="700" fill="#6b4312" text-anchor="middle" font-family="%s">INTENT</text>'
          '<path d="M8 27 h32 M8 35 h32 M8 43 h22" stroke="#b07a2a" stroke-width="2"/></g>' % (GOLD_D, GOLD, SERIF))
    elif prop == "plan":
        g('<g transform="translate(54 38) rotate(6)"><rect width="54" height="60" rx="4" fill="#eef4ff" stroke="%s" stroke-width="2"/>'
          '<text x="27" y="14" font-size="9" font-weight="700" fill="%s" text-anchor="middle" font-family="%s">plan.md</text>'
          '<rect x="20" y="20" width="14" height="8" rx="2" fill="%s"/><rect x="5" y="38" width="14" height="8" rx="2" fill="%s"/>'
          '<rect x="35" y="38" width="14" height="8" rx="2" fill="%s"/><path d="M27 28 v5 M12 38 v-5 h30 v5" fill="none" stroke="%s" stroke-width="1.6"/></g>'
          % (BLUE, BLUE, MONO, BLUE, CYAN, CYAN, BLUE))
    elif prop == "wand":
        g('<path d="M56 60 L86 22" stroke="%s" stroke-width="3.6" stroke-linecap="round"/><circle cx="87" cy="20" r="5.5" fill="#fff4b8"/>'
          '<circle cx="87" cy="20" r="12" fill="#ffe27a" opacity=".4"/><path d="M87 5 v6 M87 29 v6 M72 20 h6 M96 20 h6" stroke="%s" stroke-width="2" stroke-linecap="round"/>' % (GOLD_D, GOLD))
    elif prop == "laptop":
        g('<g transform="translate(56 56)"><rect width="36" height="24" rx="3" fill="#1e2842" stroke="#7f9cd9" stroke-width="1.5"/>'
          '<path d="M5 7 h12 M9 12 h18 M9 17 h10" stroke="#8fd3a8" stroke-width="1.8"/><rect x="-4" y="24" width="44" height="4" rx="2" fill="#7f9cd9"/></g>')
    elif prop == "terminal":
        g('<g transform="translate(56 52)"><rect width="38" height="28" rx="3" fill="#10182c" stroke="#7f9cd9" stroke-width="1.5"/>'
          '<path d="M5 8 l5 4 l-5 4" fill="none" stroke="#7df0c0" stroke-width="2"/><path d="M13 17 h10" stroke="#7df0c0" stroke-width="2"/>'
          '<text x="30" y="23" font-size="7" fill="#ff8a7a" font-family="%s">✗</text></g>' % SANS)
    elif prop == "magnifier":
        g('<g transform="translate(58 44)"><circle cx="13" cy="13" r="11" fill="#dff1ff" fill-opacity=".75" stroke="%s" stroke-width="3"/>'
          '<path d="M8 11 l-3 3 l3 3 M18 11 l3 3 l-3 3" fill="none" stroke="%s" stroke-width="1.6"/>'
          '<path d="M21 21 l12 12" stroke="%s" stroke-width="5" stroke-linecap="round"/></g>' % (GOLD_D, BLUE, GOLD_D))
    elif prop == "checklist":
        g('<g transform="translate(56 44)"><rect width="36" height="46" rx="3" fill="#fff" stroke="#8a97b4" stroke-width="1.6"/>'
          '<rect x="4" y="7" width="15" height="9" rx="2" fill="%s"/><text x="11.5" y="14" font-size="6.5" font-weight="700" fill="#fff" text-anchor="middle" font-family="%s">PASS</text>'
          '<rect x="4" y="21" width="15" height="9" rx="2" fill="%s"/><text x="11.5" y="28" font-size="6.5" font-weight="700" fill="#fff" text-anchor="middle" font-family="%s">PASS</text>'
          '<rect x="4" y="35" width="15" height="9" rx="2" fill="#d9534f"/><text x="11.5" y="42" font-size="6.5" font-weight="700" fill="#fff" text-anchor="middle" font-family="%s">FAIL</text>'
          '<path d="M23 11 h9 M23 25 h9 M23 39 h9" stroke="#8a97b4" stroke-width="1.8"/></g>' % (GREEN, SANS, GREEN, SANS, SANS))
    elif prop == "thumbs":
        g('<g transform="translate(58 42)"><path d="M4 22 h8 v16 h-8 z" fill="%s"/><path d="M12 22 l6 -12 c2 -4 7 -2 6 2 l-2 8 h9 c3 0 4 3 3 5 l-3 12 c-1 2 -2 3 -4 3 h-15 z" fill="%s"/></g>' % (SKIN_D, SKIN))
    elif prop == "toolbox":
        g('<g transform="translate(50 70)"><rect x="0" y="8" width="54" height="28" rx="4" fill="#9a5b22" stroke="#6b3c12" stroke-width="2"/>'
          '<path d="M17 8 v-6 h20 v6" fill="none" stroke="#6b3c12" stroke-width="3"/><rect x="0" y="16" width="54" height="4" fill="#6b3c12"/>'
          '<path d="M42 8 l10 -18" stroke="#9aa6bf" stroke-width="4" stroke-linecap="round"/><circle cx="53" cy="-12" r="4" fill="none" stroke="#9aa6bf" stroke-width="2.5"/></g>')


def card(x, y, w, h, n, title, accent=NAVY):
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="18" fill="url(#glass)" stroke="%s" stroke-width="1.8" filter="url(#shadow)"/>'
        % (x, y, w, h, accent))
    add('<path d="M%g %g h%g a18 18 0 0 1 18 18 v34 h-%g v-34 a18 18 0 0 1 18 -18 z" fill="url(#head)"/>' % (x + 18, y, w - 36, w))
    t(x + 18, y + 35, "%d." % n, size=22, fill=GOLD, weight=700, font=SERIF)
    t(x + 44, y + 35, title, size=21, fill="#ffffff", weight=700, font=SERIF)


# ── document ────────────────────────────────────────────────────────────────
add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-labelledby="t d">' % (W, H, W, H))
add("<title id=\"t\">Aladin's Loop (aloop) — Deterministic Autonomous Sprint Lifecycle</title>")
add("<desc id=\"d\">Intent in; Opus planner writes a deterministic, self-contained sprint plan; the Sonnet orchestrator "
    "(Aladin) dispatches worker genies that build, test, review and verify in parallel, time-boxed by hooks; tools run "
    "outside model control; everything is recorded (stats.md, NEXT.md, execution.log); the runtime clears context and "
    "the fresh session resumes from NEXT.md; budget overruns loop back to the planner; repeat until the project is "
    "complete. Runs on Claude Code, Codex and OpenCode.</desc>")
add("<defs>")
add('<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbf3df"/><stop offset=".4" stop-color="#f8f7f2"/><stop offset="1" stop-color="#eef1f7"/></linearGradient>')
add('<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0 H0 V32" fill="none" stroke="#2f64d6" stroke-opacity=".06" stroke-width="1"/></pattern>')
add('<linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".97"/><stop offset="1" stop-color="#f6f9ff" stop-opacity=".94"/></linearGradient>')
add('<linearGradient id="head" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (NAVY, NAVY2))
add('<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe9ad"/><stop offset=".5" stop-color="%s"/><stop offset="1" stop-color="#9b6514"/></linearGradient>' % GOLD)
add('<radialGradient id="aura"><stop offset="0" stop-color="#fff1b0" stop-opacity=".95"/><stop offset=".5" stop-color="#bcd0ff" stop-opacity=".4"/><stop offset="1" stop-color="#bcd0ff" stop-opacity="0"/></radialGradient>')
add('<linearGradient id="carpet" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a45a8"/><stop offset="1" stop-color="#172673"/></linearGradient>')
add('<linearGradient id="clear" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (NAVY, "#2c4fb5"))
add('<filter id="shadow" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#23305a" flood-opacity=".14"/></filter>')
add('<filter id="bloom" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
for col in (BLUE, CYAN, AMBER, TEAL, GREEN, VIOLET):
    add('<marker id="ah-%s" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>' % (col.strip("#"), col))
add(GENIE)
add("</defs>")
add('<rect width="%d" height="%d" fill="url(#bg)"/><rect width="%d" height="%d" fill="url(#grid)"/>' % (W, H, W, H))


# subtle skyline (secondary, behind everything)
def dome(cx, base, r, h, fill):
    add('<path d="M%g %g v-%g q0 -%g %g -%g q%g 0 %g %g v%g z" fill="%s"/>' % (cx - r, base, h, r * 1.3, r, r * 1.3, r, r, r * 1.3, h, fill))
    add('<path d="M%g %g v-14" stroke="%s" stroke-width="2.5"/>' % (cx, base - h - r * 1.3, fill))


for cx, r, h in ((40, 30, 60), (120, 20, 40), (1780, 26, 50), (1870, 34, 64)):
    dome(cx, 150, r, h, "#efe4cc")
add('<path d="M1700 150 v-48 a14 14 0 0 1 28 0 v48 z M1745 150 v-70 h12 v70 z" fill="#f1e7d2"/>')

# ── header ──────────────────────────────────────────────────────────────────
t(48, 56, "You state the intent.", size=23, fill=NAVY2, italic=True, font=SERIF, rot=-4)
t(66, 88, "Aladin handles the rest.", size=23, fill=NAVY2, italic=True, font=SERIF, rot=-4)
add('<path d="M60 102 C140 112 230 104 300 90" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % GOLD)
add('<text x="%g" y="62" font-size="58" fill="%s" font-weight="700" text-anchor="middle" font-family="%s">Aladin’s Loop '
    '<tspan fill="%s" font-size="42">(aloop)</tspan></text>' % (W / 2, NAVY, SERIF, BLUE))
t(W / 2, 98, "Deterministic Autonomous Sprint Lifecycle", size=25, fill=TXT, anchor="middle", font=SERIF)
flow = ["INTENT", "PLAN", "ORCHESTRATE", "EXECUTE", "VERIFY", "RECORD", "CLEAR", "RESUME"]
fcol = [GOLD_D, BLUE, GOLD_D, VIOLET, GREEN, TEAL, NAVY2, BLUE]
widths = [len(s) * 10.6 for s in flow]
total = sum(widths) + 36 * (len(flow) - 1)
fx = W / 2 - total / 2
for i, s in enumerate(flow):
    t(fx, 132, s, size=14, fill=fcol[i], weight=800, ls=2)
    fx += widths[i]
    if i < len(flow) - 1:
        t(fx + 12, 132, "→", size=15, fill=MUTED)
        fx += 36
# principles banner (architecture metadata)
rect(1560, 18, 300, 50, fill="#ffffff", stroke=LINE, r=16, sw=1.2)
t(1710, 38, "OPEN SOURCE · MODEL AGNOSTIC", size=11, fill=NAVY2, weight=700, anchor="middle", ls=0.8)
t(1710, 56, "DETERMINISTIC · BUILT FOR DEVELOPERS", size=11, fill=NAVY2, weight=700, anchor="middle", ls=0.8)
t(1710, 94, "Small sprints. Big progress.", size=19, fill=GOLD_D, italic=True, anchor="middle", font=SERIF)
t(1710, 120, "runs on Claude Code · Codex · OpenCode", size=12.5, fill=MUTED, italic=True, anchor="middle")

# ── row A: 1 · 2 · 3 · 4 · 7 ────────────────────────────────────────────────
AY, AH = 150, 410
C1, C2, C3, C4, C7 = (18, 280), (318, 290), (628, 540), (1188, 410), (1618, 284)

# 1 — Inputs / Setup
x, w = C1
card(x, AY, w, AH, 1, "Inputs / Setup")
t(x + w / 2, AY + 76, "You give the intent. A Genie captures it.", size=13.5, fill=MUTED, anchor="middle")
add('<path d="M%g %g C%g %g %g %g %g %g" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="3 5" opacity=".8"/>'
    % (x + 20, AY + 138, x + 40, AY + 120, x + 60, AY + 128, x + 74, AY + 140, GOLD))
t(x + 14, AY + 132, "you", size=12, fill=GOLD_D, weight=700)
genie(x + 70, AY + 96, 1.22, "intent")
item(x + 16, AY + 264, "chat", "User goal / intent", "feature · bug · change")
item(x + 16, AY + 314, "doc", "defaults.md", "config · constraints (init)")
item(x + 16, AY + 364, "tree", "NEXT.md carry-over", "backlog · out-of-scope")

# 2 — Planning Layer
x, w = C2
card(x, AY, w, AH, 2, "Planning Layer")
t(x + w / 2, AY + 76, "Planner Genie (Opus 5.5)", size=15.5, fill=BLUE, weight=750, anchor="middle")
t(x + w / 2, AY + 96, "Decomposes intent into an executable,", size=12.8, fill=MUTED, anchor="middle")
t(x + w / 2, AY + 113, "deterministic, self-contained plan.", size=12.8, fill=MUTED, anchor="middle")
genie(x + 58, AY + 122, 1.08, "plan")
for i, (ic, lab, sub) in enumerate([("tree", "Break down tasks", "stories → tasks"), ("rules", "Apply rules & constraints", "standards.md"),
                                    ("lock", "Create deterministic plan", "tests-only · waves"), ("doc", "Output sprint plan", "sprintN/plan.md")]):
    item(x + 16, AY + 262 + i * 38, ic, lab, sub)

# 3 — Orchestration Core (hero)
x, w = C3
card(x, AY, w, AH, 3, "Orchestration Core")
t(x + w / 2, AY + 80, "Aladin Orchestrator (Sonnet)", size=21, fill=GOLD_D, weight=700, anchor="middle", font=SERIF)
t(x + w / 2, AY + 102, "Monitors, coordinates, tracks, and adapts.", size=14, fill=MUTED, anchor="middle")
nodes_l = [("bars", "Track Progress", "execution.log"), ("gauge", "Manage Token Budget", None), ("alert", "Detect Issues", "gate verdicts")]
nodes_r = [("cycle", "Mid-sprint Re-planning", "split, don’t retry"), ("people", "Coordinate Subagents", "waves · worktrees"),
           ("lock", "Ensure Determinism", "hooks, not goodwill")]
NW, NH = 176, 62
for side, nodes in ((0, nodes_l), (1, nodes_r)):
    for i, (ic, lab, sub) in enumerate(nodes):
        nx = x + 16 if side == 0 else x + w - 16 - NW
        ny = AY + 122 + i * (NH + 12)
        rect(nx, ny, NW, NH, fill=GOLD_L, stroke="#e8c874", r=12, sw=1.4, extra='filter="url(#bloom)"')
        icon(ic, nx + 10, ny + 12, GOLD_D, 0.95)
        t(nx + 36, ny + 25, lab, size=12.2, fill=TXT, weight=750)
        if sub:
            t(nx + 36, ny + 45, sub, size=11, fill=MUTED, font=MONO)
        else:   # budget gauges: tokens + time
            for k, (lbl, frac, lim) in enumerate((("tok", 0.62, "150k/250k"), ("time", 0.45, "20/30m"))):
                gy = ny + 38 + k * 12
                t(nx + 38, gy + 4, lbl, size=9.5, fill=MUTED, weight=700)
                rect(nx + 62, gy - 3, 48, 7, fill="#fff", stroke="#e0c27a", r=3.5, sw=1)
                rect(nx + 62, gy - 3, 48 * frac, 7, fill=GOLD, stroke="none", r=3.5, sw=0)
                add('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#b33" stroke-width="1.5"/>' % (nx + 62 + 48 * .6, gy - 5, nx + 62 + 48 * .6, gy + 6))
                t(nx + 114, gy + 4, lim, size=9, fill=MUTED, font=MONO)
# lamp, infinity smoke, genie
lx, ly = x + w / 2, AY + AH - 50
add('<circle cx="%g" cy="%g" r="120" fill="url(#aura)"/>' % (lx, ly - 110))
inf = "M%g %g C%g %g %g %g %g %g C%g %g %g %g %g %g C%g %g %g %g %g %g C%g %g %g %g %g %g Z" % (
    lx, ly - 120, lx + 28, ly - 170, lx + 66, ly - 150, lx + 66, ly - 120, lx + 66, ly - 90, lx + 28, ly - 70, lx, ly - 120,
    lx - 28, ly - 170, lx - 66, ly - 150, lx - 66, ly - 120, lx - 66, ly - 90, lx - 28, ly - 70, lx, ly - 120)
add('<path id="inf" d="%s" fill="none" stroke="#8fb2ff" stroke-width="10" stroke-opacity=".35" stroke-linecap="round"/>' % inf)
add('<path d="%s" fill="none" stroke="#6f97f5" stroke-width="2.4" stroke-opacity=".85"/>' % inf)
t(lx, AY + AH - 12, "PLAN → EXECUTE → VERIFY → LEARN → REPEAT", size=11.5, fill=NAVY2, weight=800, anchor="middle", ls=2)
add('<path d="M%g %g C%g %g %g %g %g %g" fill="none" stroke="#8fb2ff" stroke-width="5" stroke-linecap="round" opacity=".7"/>'
    % (lx + 52, ly - 16, lx + 70, ly - 40, lx + 20, ly - 56, lx + 10, ly - 76))
genie(lx - 54, ly - 212, 1.3, "wand")
add('<g transform="translate(%g %g)">' % (lx - 80, ly - 36) +
    '<path d="M22 32 C22 12 114 12 114 32 C114 44 98 50 68 50 C36 50 22 44 22 32 Z" fill="url(#gold)" stroke="#86560f" stroke-width="1.6"/>'
    '<path d="M114 28 C130 26 146 14 154 2 C150 20 138 34 116 40" fill="url(#gold)" stroke="#86560f" stroke-width="1.6"/>'
    '<path d="M22 30 C4 26 2 44 18 44" fill="none" stroke="%s" stroke-width="5.5" stroke-linecap="round"/>' % GOLD_D +
    '<ellipse cx="68" cy="15" rx="26" ry="7" fill="url(#gold)" stroke="#86560f" stroke-width="1.3"/><circle cx="68" cy="6" r="4.5" fill="%s"/>' % GOLD +
    '<path d="M40 24 h56" stroke="#fff3c4" stroke-width="1.2" opacity=".8"/>'
    '<rect x="44" y="50" width="48" height="9" rx="3" fill="url(#gold)" stroke="#86560f" stroke-width="1.3"/>'
    '<text x="68" y="39" font-size="8.6" font-weight="800" fill="#4a2f0a" text-anchor="middle" font-family="%s" letter-spacing=".4">ALADIN’S LOOP</text></g>' % SERIF)

# 4 — Execution Layer
x, w = C4
card(x, AY, w, AH, 4, "Execution Layer", accent=VIOLET)
t(x + w / 2, AY + 76, "Specialized worker Genies (Sonnet) execute", size=13.5, fill=MUTED, anchor="middle")
t(x + w / 2, AY + 94, "tasks in parallel — one isolated worktree each.", size=13.5, fill=MUTED, anchor="middle")
crew = [("Subagent A — Build", "SCAFFOLD → GREEN", "laptop"), ("Subagent B — Test", "RED: failing tests first", "terminal"),
        ("Reviewer — Quality", "structure · duplicates", "magnifier"), ("Verifier — Checks", "gates · PASS / FAIL", "checklist")]
cw, chh = (w - 38) / 2, 126
for i, (name, what, prop) in enumerate(crew):
    cx = x + 13 + (i % 2) * (cw + 12)
    cy = AY + 110 + (i // 2) * (chh + 10)
    rect(cx, cy, cw, chh, fill=VIOLET_L, stroke="#cdbdf3", r=12, sw=1.2)
    genie(cx + 18, cy + 2, 0.86, prop)
    t(cx + cw / 2, cy + 100, name, size=13.5, fill=VIOLET, weight=750, anchor="middle")
    t(cx + cw / 2, cy + 117, what, size=11.8, fill=MUTED, anchor="middle")
t(x + w / 2, AY + AH - 14, "every stop is gated by a hook · a block keeps the worker working (≤3)", size=11.8, fill=VIOLET, weight=650, anchor="middle")

# 7 — Outcomes
x, w = C7
card(x, AY, w, AH, 7, "Outcomes", accent=GREEN)
t(x + w / 2, AY + 76, "Sprint complete. Context cleared.", size=13.5, fill=MUTED, anchor="middle")
t(x + w / 2, AY + 94, "Ready for next.", size=13.5, fill=MUTED, anchor="middle")
genie(x + 28, AY + 104, 1.02, "thumbs")
add('<circle cx="%g" cy="%g" r="34" fill="%s" filter="url(#bloom)"/><path d="M%g %g l10 10 l20 -22" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round"/>'
    % (x + 206, AY + 158, GREEN, x + 191, AY + 158))
steps = [("check", "Completed Sprint", "final gate green", GREEN), ("check", "Artifacts Recorded", "stats.md · NEXT.md", GREEN),
         ("check", "Context Clear", "runtime /clear", GREEN), ("play", "Next Sprint Resume", "reads NEXT.md", BLUE)]
for i, (ic, lab, sub, col) in enumerate(steps):
    sy = AY + 248 + i * 42
    item(x + 18, sy, ic, lab, sub, color=col)
    if i < 3:
        arrow("M%g %g L%g %g" % (x + 28, sy + 7, x + 28, sy + 22), GREEN, sw=2)

# execution arrows between row-A cards + edge labels
for (a, b, lab, col) in ((C1, C2, "INTENT IN", GOLD_D), (C2, C3, "PLAN", BLUE), (C3, C4, "EXECUTE", VIOLET), (C4, C7, "VERIFY", GREEN)):
    x1, x2 = a[0] + a[1] + 3, b[0] - 5
    arrow("M%g %g L%g %g" % (x1, AY + 186, x2, AY + 186), CYAN, sw=6)
    t((x1 + x2) / 2 + 4, AY + 206, lab, size=10.5, fill=col, weight=800, anchor="end", ls=1, rot=-90)

# ── band: RE-PLAN loop (amber) ──────────────────────────────────────────────
RY = AY + AH + 30
arrow("M%g %g V%g H%g V%g" % (C4[0] + 60, AY + AH + 2, RY, C2[0] + 200, AY + AH + 6), AMBER, sw=3, dash="10 7")
wl = tag(C3[0] + 60, RY, "RE-PLAN", AMBER, fill="#fff8ec", size=13)
chain = "worker stopped at hard budget / fails  →  evidence kept, partial work NOT merged  →  planner splits the task  →  resume from accepted state"
rect(C3[0] + 60 + wl / 2 + 8, RY - 12, len(chain) * 6.55 + 20, 24, fill="#fff8ec", stroke="#f0cf98", r=12, sw=1)
t(C3[0] + 60 + wl / 2 + 18, RY + 4.5, chain, size=12, fill="#8a520c", weight=600)

# ── band: SPRINT BOUNDARY (right → left), the repeat loop ───────────────────
BY = RY + 62
# Outcomes → boundary
arrow("M%g %g V%g" % (C7[0] + C7[1] / 2 + 60, AY + AH + 2, BY - 30), TEAL, sw=4)
bx = [(1470, 440, TEAL_L, TEAL, "SPRINT N · CHECKPOINT", "execute → verify → stats.md + NEXT.md → checkpoint"),
      (930, 470, None, None, "DETERMINISTIC CONTEXT CLEAR", "runtime, not the genie: Stop hook → /clear → SessionStart"),
      (420, 440, "#eaf1ff", BLUE, "FRESH CONTEXT", "read NEXT.md → determine next sprint → resume")]
for i, (bx0, bw, fill, col, head, body) in enumerate(bx):
    if fill is None:
        rect(bx0, BY - 30, bw, 60, fill="url(#clear)", stroke=NAVY, r=14, sw=1.5, extra='filter="url(#shadow)"')
        t(bx0 + bw / 2, BY - 6, head, size=14.5, fill="#ffffff", weight=800, anchor="middle", ls=2)
        t(bx0 + bw / 2, BY + 16, body, size=12.2, fill="#cfdcff", anchor="middle")
    else:
        rect(bx0, BY - 30, bw, 60, fill=fill, stroke=col, r=14, sw=1.5)
        t(bx0 + bw / 2, BY - 6, head, size=14, fill=col, weight=800, anchor="middle", ls=1.5)
        t(bx0 + bw / 2, BY + 16, body, size=12.2, fill=TXT, anchor="middle", font=MONO)
arrow("M%g %g L%g %g" % (1470 - 4, BY, 930 + 470 + 8, BY), TEAL, sw=4)
arrow("M%g %g L%g %g" % (930 - 4, BY, 420 + 440 + 8, BY), BLUE, sw=4)
# fresh context → planning (repeat)
arrow("M%g %g H%g V%g" % (420 - 4, BY, C2[0] + 60, AY + AH + 6), BLUE, sw=4)
tag(C1[0] + 172, BY - 22, "REPEAT UNTIL PROJECT COMPLETE", BLUE, fill="#eef4ff", size=12)
t(C1[0] + 172, BY + 10, "the repo carries the memory forward", size=12, fill=TEAL, italic=True, anchor="middle")

# ── row B: 5 Tooling ribbon · 6 State / Artifacts ───────────────────────────
TY, TH = BY + 62, 292
T5, T6 = (18, 1250), (1288, 614)

# 5 — Tooling / Runtime
x, w = T5
card(x, TY, w, TH, 5, "Tooling / Runtime Layer", accent=CYAN)
t(x + 360, TY + 34, "Deterministic tools. Outside model control.", size=14, fill="#cfe0ff", italic=True)
t(x + w - 20, TY + 34, "Automate the grind. Keep the thinking.", size=14, fill="#f3d99a", italic=True, anchor="end", font=SERIF)
genie(x + 24, TY + 92, 1.12, "toolbox")
tools = [("selfcheck", "lint · test · validate"), ("md-db", "schema-check docs"), ("ctx-symbols", "code context"),
         ("gate-tooling", "policies · enforcement"), ("budget", "time box · hard stop"), ("stats", "token ledger · stats")]
for i, (nm, sub) in enumerate(tools):
    tx, ty = x + 150 + i * 180, TY + 74
    rect(tx, ty, 168, 62, fill="#eef6ff", stroke="#b8d3f2", r=12, sw=1.3)
    icon("code", tx + 10, ty + 11, CYAN, 0.8)
    t(tx + 34, ty + 26, nm, size=14, fill=NAVY2, weight=750, font=MONO)
    t(tx + 12, ty + 48, sub, size=12, fill=MUTED)
t(x + 150, TY + 164, "HOOK LAYER — fires on every event, on every host (hooks.json · OpenCode plugin)", size=11.5, fill=MUTED, weight=700, ls=1)
hooks = [("SessionStart", "build tools · load NEXT.md"), ("PreToolUse", "scope · commit author · isolation"),
         ("PostToolUse", "budget warn / stop · record"), ("SubagentStop", "role gate · keep working"), ("Stop", "ledger · sprint totals")]
for i, (ev, what) in enumerate(hooks):
    hx, hy = x + 150 + i * 216, TY + 178
    rect(hx, hy, 204, 60, fill="#ffffff", stroke="#c7d6ef", r=10, sw=1.2)
    icon("hook", hx + 10, hy + 10, NAVY2, 0.8)
    t(hx + 30, hy + 25, ev, size=13.5, fill=NAVY2, weight=750, font=MONO)
    t(hx + 12, hy + 47, what, size=11.8, fill=MUTED)
t(x + 150, TY + TH - 22, "all callable as `agentic <tool>` · md-db + ctx-symbols auto-built · no model reasoning inside",
  size=12, fill=MUTED)
# TOOLS arrows down from orchestration + execution
for sx in (C3[0] + 140, C4[0] + 200):
    arrow("M%g %g V%g" % (sx, BY + 32, TY - 6), CYAN, sw=3.2)
tag(C3[0] + 140, BY + 46, "TOOLS", CYAN, size=11)
tag(C4[0] + 200, BY + 46, "TOOLS", CYAN, size=11)

# 6 — Deterministic State / Artifacts
x, w = T6
card(x, TY, w, TH, 6, "Deterministic State / Artifacts", accent=TEAL)
t(x + 18, TY + 76, "Everything is recorded. The repo is the source of truth.", size=14.5, fill=TEAL, weight=700)
t(x + 18, TY + 96, "Artifacts are the memory. Everything else is ephemeral.", size=13, fill=MUTED, italic=True, font=SERIF)
tree = ["docs/agents/", "├── defaults.md", "├── NEXT.md  ← read on resume", "├── memory.md",
        "└── sprintN/", "    ├── stories.md · plan.md", "    ├── sNN-*/output.md", "    ├── execution.log", "    └── stats.md"]
for i, s in enumerate(tree):
    t(x + 22, TY + 124 + i * 19, s.replace(" ", "\u00a0"), size=12.8, fill=NAVY2 if i == 0 else TXT, weight=700 if i == 0 else 400, font=MONO)
side = [("stats.md", "tokens · time · status · tasks"), ("output.md", "results · worker reports"),
        ("execution.log", "decisions · lineage"), (".agentic/", "run data · always git-ignored")]
for i, (nm, sub) in enumerate(side):
    sx, sy = x + 350, TY + 108 + i * 46
    rect(sx, sy, 246, 42, fill=TEAL_L, stroke="#a9dcd8", r=10, sw=1.2)
    t(sx + 12, sy + 18, nm, size=13, fill=TEAL, weight=750, font=MONO)
    t(sx + 12, sy + 34, sub, size=11.3, fill=MUTED)
# state arrow: checkpoint writes into artifacts
arrow("M%g %g V%g" % (1690, BY + 32, TY - 6), TEAL, sw=3.2)
tag(1690, BY + 46, "WRITE CHECKPOINT", TEAL, size=11)

# ── footer ──────────────────────────────────────────────────────────────────
fy = H - 16
fx = 24
for ic, s in (("cycle", "Open Source"), ("people", "Model Agnostic — Claude Code · Codex · OpenCode"),
              ("lock", "Deterministic by Design"), ("code", "Built for Developers")):
    icon(ic, fx, fy - 15, NAVY2, 0.85)
    t(fx + 24, fy, s, size=14, fill=TXT, weight=600)
    fx += len(s) * 7.7 + 50
    if s != "Built for Developers":
        t(fx - 26, fy, "|", size=14, fill=LINE)
add('<g transform="translate(%g %g) scale(.32)"><path d="M22 32 C22 12 114 12 114 32 C114 44 98 50 68 50 C36 50 22 44 22 32 Z" fill="url(#gold)"/>'
    '<path d="M114 28 C130 26 146 14 154 2 C150 20 138 34 116 40" fill="url(#gold)"/><ellipse cx="68" cy="15" rx="26" ry="7" fill="url(#gold)"/></g>' % (W - 405, fy - 18))
t(W - 22, fy, "Restore Time. Build What Matters.", size=20, fill=NAVY, anchor="end", font=SERIF, italic=True)
add("</svg>")

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aloop.svg")
with open(path, "w") as f:
    f.write("\n".join(out) + "\n")
print("wrote", path)
