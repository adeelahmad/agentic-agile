#!/usr/bin/env python3
# Generates docs/diagrams/architecture.svg — agentic-agile lifecycle (Style 6, Claude Official).
from xml.sax.saxutils import escape

BG="#f8f6f3"; BLUE="#a8c5e6"; TEAL="#9dd4c7"; BEIGE="#f4e4c1"; GRAY="#e8e6e3"
STROKE="#4a4a4a"; TX="#1a1a1a"; TX2="#6a6a6a"; ARR="#5a5a5a"; PURP="#7c3aed"
FONT="-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,sans-serif"
L=[]
def add(s): L.append(s)

add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 860" font-family="%s">' % FONT)
add('  <defs>')
add('    <marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><polygon points="0 0, 8 4, 0 8" fill="%s"/></marker>' % ARR)
add('    <marker id="arrp" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><polygon points="0 0, 8 4, 0 8" fill="%s"/></marker>' % PURP)
add('    <filter id="sh" x="-20%%" y="-20%%" width="140%%" height="140%%"><feDropShadow dx="0" dy="1.5" stdDeviation="1.5" flood-opacity="0.18"/></filter>')
add('  </defs>')
add('  <rect width="1200" height="860" fill="%s"/>' % BG)

# title
add('  <text x="600" y="40" text-anchor="middle" font-size="25" font-weight="700" fill="%s">agentic-agile</text>' % TX)
add('  <text x="600" y="65" text-anchor="middle" font-size="13.5" fill="%s">Hook-enforced agentic TDD for Claude Code — plan the sprint, then write the code behind deterministic gates.</text>' % TX2)

def band(x,y,w,h,label):
    add('  <rect x="%d" y="%d" width="%d" height="%d" rx="14" fill="#ffffff" fill-opacity="0.45" stroke="%s" stroke-width="1.5" stroke-dasharray="7,5"/>' % (x,y,w,h,STROKE))
    add('  <text x="%d" y="%d" font-size="13.5" font-weight="700" fill="%s">%s</text>' % (x+18,y+24,TX,escape(label)))

def node(x,y,w,h,fill,lines,double=False,ts=14):
    if double:
        add('  <rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s" stroke-width="2.5" filter="url(#sh)"/>' % (x,y,w,h,fill,STROKE))
        add('  <rect x="%d" y="%d" width="%d" height="%d" rx="9" fill="none" stroke="%s" stroke-width="1"/>' % (x+4,y+4,w-8,h-8,STROKE))
    else:
        add('  <rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s" stroke-width="2.5" filter="url(#sh)"/>' % (x,y,w,h,fill,STROKE))
    cx=x+w/2; cy=y+h/2; n=len(lines); lh=15
    start=cy-(n-1)*lh/2
    for i,(t,sz,wt) in enumerate(lines):
        by=start+i*lh+sz*0.34
        col=TX if wt=="700" else TX2
        add('  <text x="%.0f" y="%.1f" text-anchor="middle" font-size="%s" font-weight="%s" fill="%s">%s</text>' % (cx,by,sz,wt,col,escape(t)))

def arrow(x1,y1,x2,y2,color=ARR,mk="arr",w=2.0,dash=None):
    d=' stroke-dasharray="%s"'%dash if dash else ''
    add('  <line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="%s"%s marker-end="url(#%s)"/>' % (x1,y1,x2,y2,color,w,d,mk))

def alabel(x,y,t):
    w=len(t)*6.4+8
    add('  <rect x="%.0f" y="%.0f" width="%.0f" height="16" rx="3" fill="%s" opacity="0.95"/>' % (x-w/2,y-12,w,BG))
    add('  <text x="%.0f" y="%.0f" text-anchor="middle" font-size="11" fill="%s">%s</text>' % (x,y,TX2,escape(t)))

# ── BAND 1 : PLANNING ──────────────────────────────────────────────
band(30,82,1140,168,"①  PLANNING  ·  interactive, human-gated")
node(50,150,92,50,BLUE,[("Human",14,"700"),("you",11,"400")])
node(172,140,148,70,TEAL,[("Supervisor",14,"700"),("agentic-agile skill",10.5,"400")],double=True)
node(356,151,96,48,TEAL,[("intake",13,"700")])
node(472,151,112,48,TEAL,[("standards",13,"700")])
node(604,151,96,48,TEAL,[("planner",13,"700")])
node(720,144,162,62,GRAY,[("Stage-2 plans",13,"700"),("stories·tasks·validate·plan",10,"400")])
node(905,144,142,62,BEIGE,[("Human approval",12.5,"700"),("go / no-go",10.5,"400")])
arrow(142,175,170,175)
arrow(320,175,354,175); alabel(337,168,"dispatch")
arrow(452,175,470,175)
arrow(584,175,602,175)
arrow(700,175,718,175)
arrow(882,175,903,175)

# ── BAND 2 : EXECUTION ─────────────────────────────────────────────
band(30,275,1140,238,"②  EXECUTION  ·  autonomous, hook-enforced  ·  one worktree-isolated sub-agent per task")
# approval -> execution (vertical gate)
arrow(976,206,976,273,w=2.2); alabel(976,250,"approved → run")
# per-task worktree sub-container
add('  <rect x="50" y="330" width="800" height="158" rx="11" fill="#ffffff" fill-opacity="0.5" stroke="%s" stroke-width="1.3" stroke-dasharray="5,4"/>' % STROKE)
add('  <text x="66" y="350" font-size="11.5" font-weight="700" fill="%s">per task · git worktree  (each step a SubagentStop gate that blocks on fail)</text>' % TX2)
node(70,386,112,62,TEAL,[("RED",14,"700"),("failing tests",10,"400")])
node(214,386,128,62,TEAL,[("SCAFFOLD",13.5,"700"),("panic stubs",10,"400")])
node(374,386,112,62,TEAL,[("GREEN",14,"700"),("minimal impl",10,"400")])
node(518,386,140,62,TEAL,[("STRUCTURAL",13,"700"),("review",10,"400")])
arrow(182,417,212,417); alabel(197,410,"gate")
arrow(342,417,372,417); alabel(357,410,"gate")
arrow(486,417,516,417); alabel(501,410,"gate")
# retry loop (purple, arc over the row)
add('  <path d="M 588,386 C 588,344 150,344 126,384" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arrp)"/>' % PURP)
alabel(357,341,"fail → retry (≤3)")
# final gate + done
node(900,378,132,72,BEIGE,[("FINAL-GATE",13,"700"),("once per sprint",10,"400")])
node(1058,392,92,46,TEAL,[("✓ merged",12.5,"700")])
arrow(658,417,898,414); alabel(778,407,"wave green")
arrow(1032,414,1056,414)

# ── BAND 3 : DETERMINISM ───────────────────────────────────────────
band(30,538,1140,238,"③  DETERMINISM  ·  the enforcement layer (Claude Code hooks + backends — what can't be talked out of)")
defs3=[
 (50,BEIGE,[("PreToolUse",12.5,"700"),("gate-supervisor-scope",9.5,"400"),("no supervisor code",9.5,"400")]),
 (235,BEIGE,[("SubagentStart",12.5,"700"),("gate-tooling",9.5,"400"),("backends on PATH",9.5,"400")]),
 (420,BEIGE,[("WorktreeCreate",12.5,"700"),("/ Remove",9.5,"400"),("git worktree isolation",9.5,"400")]),
 (605,BEIGE,[("SubagentStop gates",11.5,"700"),("red·scaffold·green",9.5,"400"),("structural·final",9.5,"400")]),
 (790,GRAY,[("Comms (story-bound)",10.5,"700"),("init.md ⇄ output.md",9.5,"400"),("append-only",9.5,"400")]),
 (975,GRAY,[("md-db · ctx-symbols",10.5,"700"),("+ transcripts",9.5,"400"),("full capture",9.5,"400")]),
]
for x,fill,lines in defs3:
    node(x,592,175,82,fill,lines)
# tie band 2 to band 3
arrow(976,513,976,536,color=ARR,w=1.6,dash="4,3")
alabel(1060,527,"enforced by ↓")

# legend
ly=800
add('  <text x="50" y="%d" font-size="11.5" font-weight="700" fill="%s">Legend</text>' % (ly,TX2))
def sw(x,fill,t):
    add('  <rect x="%d" y="%d" width="16" height="13" rx="3" fill="%s" stroke="%s" stroke-width="1.2"/>' % (x,ly-11,fill,STROKE))
    add('  <text x="%d" y="%d" font-size="11" fill="%s">%s</text>' % (x+22,ly,TX2,escape(t)))
sw(120,BLUE,"human"); sw(230,TEAL,"agent / step"); sw(380,BEIGE,"gate / hook"); sw(525,GRAY,"artifact / store")
add('  <line x1="690" y1="%d" x2="724" y2="%d" stroke="%s" stroke-width="2" marker-end="url(#arr)"/>' % (ly-4,ly-4,ARR))
add('  <text x="730" y="%d" font-size="11" fill="%s">flow</text>' % (ly,TX2))
add('  <line x1="790" y1="%d" x2="824" y2="%d" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arrp)"/>' % (ly-4,ly-4,PURP))
add('  <text x="830" y="%d" font-size="11" fill="%s">retry loop</text>' % (ly,TX2))
add('  <line x1="930" y1="%d" x2="964" y2="%d" stroke="%s" stroke-width="1.6" stroke-dasharray="4,3" marker-end="url(#arr)"/>' % (ly-4,ly-4,ARR))
add('  <text x="970" y="%d" font-size="11" fill="%s">enforced-by</text>' % (ly,TX2))

add('</svg>')
with open("/Users/adeelahmad/Downloads/agentic-agile/docs/diagrams/architecture.svg","w") as f:
    f.write("\n".join(L))
print("SVG generated, %d lines" % len(L))
