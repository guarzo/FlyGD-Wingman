"""PROTOTYPE — THROWAWAY. Delete once a direction is chosen.

Question it answers: what should the OBS-YouTube-Uploader main window LOOK
like? Not "which defects should we fix" — the whole window reads as an
undesigned utility form, so this explores four structurally different
directions rather than tweaks to one.

Four variants, switchable from the bar at the bottom (click the arrows, or
press Left/Right). Each is a different answer to "what is this window FOR":

  A  Content first    the list is the app; everything else gets out of its way
  B  Master-detail    list left, upload panel right, selection drives the panel
  C  Sectioned        distinct grouped panels, strong hierarchy, generous space
  D  Compact          dense pro-tool; maximum rows visible, minimum chrome

All four use real sv-ttk theming, real DPI scaling, and a realistic number of
realistic recordings, because every layout looks fine with six rows of Lorem.

Run:  python ui_mockup_prototype.py
"""
import datetime
import random
import sys
import tkinter as tk
from tkinter import font as tkfont, ttk

import sv_ttk

# --------------------------------------------------------------------------
# DPI setup — mirrors __main__.main() so the prototype renders the way the
# real app does at the tester's display scaling.
# --------------------------------------------------------------------------


def set_dpi_awareness():
    if sys.platform != "win32":
        return
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass


def system_dpi():
    if sys.platform != "win32":
        return 96
    import ctypes
    try:
        dpi = ctypes.windll.user32.GetDpiForSystem()
    except (AttributeError, OSError):
        return 96
    return dpi if dpi >= 96 else 96


# --------------------------------------------------------------------------
# Fake data — realistic names, sizes and durations, and enough of them that
# density problems actually show up.
# --------------------------------------------------------------------------

def make_recordings(n=40):
    random.seed(7)
    out = []
    t = datetime.datetime(2026, 8, 20, 17, 45)
    for i in range(n):
        t -= datetime.timedelta(minutes=random.randint(18, 200))
        kind = random.choice(["Fight", "Replay", ""])
        stamp = t.strftime("%Y-%m-%d %H-%M-%S")
        name = f"{kind} {stamp}.mkv".strip()
        secs = random.choice([119, 224, 3598, 3599, 3600, 987, 2504, 224])
        mb = round(secs * random.uniform(0.09, 0.13), 1)
        out.append({
            "name": name,
            "when": t,
            "size_mb": mb,
            "secs": secs,
            "link": "https://youtu.be/dQw4w9WgXcQ" if i % 9 == 3 else "",
        })
    return out


def size_str(mb):
    return f"{mb/1024:.1f} GB" if mb >= 1024 else f"{mb:.1f} MB"


def dur_str(s):
    return f"{s//60}:{s%60:02d}"


def when_str(dt, relative=False):
    if not relative:
        return dt.strftime("%Y-%m-%d %H:%M")
    days = (datetime.datetime(2026, 8, 20, 18, 0) - dt).days
    if days == 0:
        return f"Today {dt:%H:%M}"
    if days == 1:
        return f"Yesterday {dt:%H:%M}"
    return dt.strftime("%d %b %H:%M")


RECORDINGS = make_recordings()
SELECTED = {0, 1, 4}


# --------------------------------------------------------------------------
# Typographic scale. The current app uses ONE size and ONE weight everywhere,
# which is most of why it reads as undesigned.
# --------------------------------------------------------------------------

def build_fonts(scale):
    base = "Segoe UI" if sys.platform == "win32" else "DejaVu Sans"
    px = lambda n: -max(9, int(round(n * scale)))
    return {
        "display": tkfont.Font(family=base, size=px(22), weight="bold"),
        "heading": tkfont.Font(family=base, size=px(15), weight="bold"),
        "subhead": tkfont.Font(family=base, size=px(12), weight="bold"),
        "body": tkfont.Font(family=base, size=px(14)),
        "bodysm": tkfont.Font(family=base, size=px(12)),
        "caption": tkfont.Font(family=base, size=px(11)),
        "mono": tkfont.Font(family="Consolas" if sys.platform == "win32" else "DejaVu Sans Mono",
                            size=px(12)),
    }


def muted(mode):
    return "#9198a1" if mode == "dark" else "#6c6c6c"


def surface(mode):
    return "#252526" if mode == "dark" else "#f3f3f3"


def hairline(mode):
    return "#3a3a3c" if mode == "dark" else "#dcdcdc"


# --------------------------------------------------------------------------
# Variant A — CONTENT FIRST
# The list is the app. One toolbar, one selection summary, nothing else
# competing. Title/Description move behind the upload action entirely.
# --------------------------------------------------------------------------

def variant_a(parent, F, mode, S):
    pad = S["pad"]
    root = ttk.Frame(parent, padding=(pad * 2, pad * 2, pad * 2, pad))
    root.pack(fill="both", expand=True)

    bar = ttk.Frame(root)
    bar.pack(fill="x", pady=(0, pad * 2))
    ttk.Button(bar, text="Upload Selected", style="Accent.TButton").pack(side="left")
    ttk.Button(bar, text="Upload combat logs").pack(side="left", padx=pad)
    ttk.Button(bar, text="Stitch").pack(side="left")
    ttk.Button(bar, text="Delete").pack(side="left", padx=pad)
    ttk.Button(bar, text="Settings").pack(side="right")

    sel = ttk.Frame(root)
    sel.pack(fill="x", pady=(0, pad))
    tk.Label(sel, text=f"{len(SELECTED)} of {len(RECORDINGS)} selected",
             font=F["subhead"], bg=surface(mode) if False else None,
             fg=None).pack(side="left")
    tk.Label(sel, text="·  2.4 GB  ·  1h 42m", font=F["bodysm"],
             fg=muted(mode)).pack(side="left", padx=(pad, 0))
    ttk.Button(sel, text="Select all").pack(side="right")
    ttk.Button(sel, text="Clear").pack(side="right", padx=pad)

    cols = ("name", "when", "size", "dur", "link")
    tv = ttk.Treeview(root, columns=cols, show="headings", selectmode="extended")
    for key, text, w, anchor in (
        ("name", "Recording", int(360 * S["scale"]), "w"),
        ("when", "When", int(150 * S["scale"]), "w"),
        ("size", "Size", int(90 * S["scale"]), "e"),
        ("dur", "Length", int(80 * S["scale"]), "e"),
        ("link", "", int(90 * S["scale"]), "w"),
    ):
        tv.heading(key, text=text)
        tv.column(key, width=w, anchor=anchor, stretch=(key == "name"))
    for i, r in enumerate(RECORDINGS):
        tv.insert("", "end", values=(
            ("● " if i in SELECTED else "   ") + r["name"],
            when_str(r["when"], relative=True),
            size_str(r["size_mb"]),
            dur_str(r["secs"]),
            "uploaded" if r["link"] else "",
        ), tags=("sel" if i in SELECTED else "odd" if i % 2 else "even",))
    tv.tag_configure("even", background=surface(mode))
    tv.tag_configure("sel", background="#2d4f67" if mode == "dark" else "#dbeafe")
    tv.pack(fill="both", expand=True)

    st = ttk.Frame(root, padding=(0, pad, 0, 0))
    st.pack(fill="x")
    tk.Label(st, text="Watching D:\\Videos", font=F["caption"],
             fg=muted(mode)).pack(side="left")


# --------------------------------------------------------------------------
# Variant B — MASTER / DETAIL
# The list answers "what have I got"; the right panel answers "what am I
# about to publish". Two-line rows kill the metadata columns entirely.
# --------------------------------------------------------------------------

def variant_b(parent, F, mode, S):
    pad = S["pad"]
    root = ttk.Frame(parent, padding=pad * 2)
    root.pack(fill="both", expand=True)

    body = ttk.Frame(root)
    body.pack(fill="both", expand=True)

    left = ttk.Frame(body)
    left.pack(side="left", fill="both", expand=True)

    head = ttk.Frame(left)
    head.pack(fill="x", pady=(0, pad))
    tk.Label(head, text="Recordings", font=F["heading"]).pack(side="left")
    tk.Label(head, text=f"{len(RECORDINGS)} in D:\\Videos", font=F["caption"],
             fg=muted(mode)).pack(side="left", padx=(pad, 0))

    canvas = tk.Canvas(left, highlightthickness=0, bd=0,
                       bg=surface(mode) if mode == "dark" else "#ffffff")
    rows = ttk.Frame(canvas)
    sb = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    rows.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=rows, anchor="nw", width=int(520 * S["scale"]))
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    for i, r in enumerate(RECORDINGS[:24]):
        row = tk.Frame(rows, bg=("#2d4f67" if i in SELECTED else
                                 (surface(mode) if mode == "dark" else "#ffffff")))
        row.pack(fill="x", pady=1, padx=1)
        inner = tk.Frame(row, bg=row["bg"])
        inner.pack(fill="x", padx=pad, pady=int(6 * S["scale"]))
        tk.Label(inner, text=r["name"], font=F["body"], bg=row["bg"],
                 anchor="w").pack(fill="x")
        meta = f"{when_str(r['when'], True)}   ·   {size_str(r['size_mb'])}   ·   {dur_str(r['secs'])}"
        tk.Label(inner, text=meta, font=F["caption"], fg=muted(mode),
                 bg=row["bg"], anchor="w").pack(fill="x")

    right = ttk.Frame(body, padding=(pad * 2, 0, 0, 0))
    right.pack(side="right", fill="y")
    card = ttk.LabelFrame(right, text="  Upload  ", padding=pad * 2)
    card.pack(fill="both", expand=True)
    tk.Label(card, text=f"{len(SELECTED)} recordings selected",
             font=F["subhead"]).pack(anchor="w")
    tk.Label(card, text="2.4 GB  ·  1h 42m  ·  earliest first", font=F["caption"],
             fg=muted(mode)).pack(anchor="w", pady=(2, pad * 2))
    tk.Label(card, text="TITLE", font=F["caption"], fg=muted(mode)).pack(anchor="w")
    ttk.Entry(card, width=32).pack(fill="x", pady=(2, pad))
    tk.Label(card, text="DESCRIPTION", font=F["caption"], fg=muted(mode)).pack(anchor="w")
    tk.Text(card, height=5, width=32, font=F["bodysm"]).pack(fill="x", pady=(2, pad))
    tk.Label(card, text="PRIVACY", font=F["caption"], fg=muted(mode)).pack(anchor="w")
    ttk.Combobox(card, values=["private", "unlisted", "public"],
                 state="readonly", width=14).pack(anchor="w", pady=(2, pad * 2))
    ttk.Checkbutton(card, text="Stitch into one video").pack(anchor="w", pady=(0, pad))
    ttk.Button(card, text="Upload to YouTube", style="Accent.TButton").pack(fill="x")
    ttk.Button(card, text="Upload combat logs").pack(fill="x", pady=(pad, 0))


# --------------------------------------------------------------------------
# Variant C — SECTIONED PANELS
# Same information as today, but grouped into panels with real headings,
# real containment and real whitespace. The most conservative rearrangement:
# nothing moves house, everything gets a room.
# --------------------------------------------------------------------------

def variant_c(parent, F, mode, S):
    pad = S["pad"]
    outer = tk.Frame(parent, bg=("#1b1b1c" if mode == "dark" else "#eaeaea"))
    outer.pack(fill="both", expand=True)
    root = ttk.Frame(outer, padding=pad * 3)
    root.pack(fill="both", expand=True)

    hero = ttk.Frame(root)
    hero.pack(fill="x", pady=(0, pad * 2))
    tk.Label(hero, text="Recordings", font=F["display"]).pack(anchor="w")
    tk.Label(hero, text=f"{len(RECORDINGS)} clips in D:\\Videos  ·  watching for new ones",
             font=F["bodysm"], fg=muted(mode)).pack(anchor="w", pady=(2, 0))

    panel = tk.Frame(root, bg=surface(mode), highlightthickness=1,
                     highlightbackground=hairline(mode))
    panel.pack(fill="both", expand=True)
    ph = tk.Frame(panel, bg=surface(mode))
    ph.pack(fill="x", padx=pad * 2, pady=(pad * 2, pad))
    tk.Label(ph, text="Select what to upload", font=F["subhead"],
             bg=surface(mode)).pack(side="left")
    tk.Label(ph, text=f"{len(SELECTED)} selected · 2.4 GB", font=F["caption"],
             fg=muted(mode), bg=surface(mode)).pack(side="right")

    holder = tk.Frame(panel, bg=surface(mode))
    holder.pack(fill="both", expand=True, padx=pad * 2, pady=(0, pad * 2))
    cols = ("name", "when", "size", "dur")
    tv = ttk.Treeview(holder, columns=cols, show="headings")
    for key, text, w, anchor in (("name", "Recording", int(380 * S["scale"]), "w"),
                                 ("when", "When", int(160 * S["scale"]), "w"),
                                 ("size", "Size", int(100 * S["scale"]), "e"),
                                 ("dur", "Length", int(90 * S["scale"]), "e")):
        tv.heading(key, text=text)
        tv.column(key, width=w, anchor=anchor, stretch=(key == "name"))
    for i, r in enumerate(RECORDINGS):
        tv.insert("", "end", values=(r["name"], when_str(r["when"], True),
                                     size_str(r["size_mb"]), dur_str(r["secs"])),
                  tags=("sel" if i in SELECTED else "",))
    tv.tag_configure("sel", background="#2d4f67" if mode == "dark" else "#dbeafe")
    tv.pack(fill="both", expand=True)

    det = tk.Frame(root, bg=surface(mode), highlightthickness=1,
                   highlightbackground=hairline(mode))
    det.pack(fill="x", pady=(pad * 2, 0))
    dh = tk.Frame(det, bg=surface(mode))
    dh.pack(fill="x", padx=pad * 2, pady=pad)
    tk.Label(dh, text="Upload details", font=F["subhead"], bg=surface(mode)).pack(side="left")
    tk.Label(dh, text="optional — leave blank to use the filename",
             font=F["caption"], fg=muted(mode), bg=surface(mode)).pack(side="left", padx=(pad, 0))
    ttk.Button(dh, text="Show").pack(side="right")

    foot = ttk.Frame(root, padding=(0, pad * 2, 0, 0))
    foot.pack(fill="x")
    ttk.Button(foot, text="Settings").pack(side="left")
    ttk.Button(foot, text="Delete Selected").pack(side="left", padx=pad)
    ttk.Button(foot, text="Upload Selected", style="Accent.TButton").pack(side="right")
    ttk.Button(foot, text="Upload combat logs").pack(side="right", padx=pad)


# --------------------------------------------------------------------------
# Variant D — COMPACT
# For someone with 132 recordings who wants to see as many as possible.
# Tight rows, aligned monospaced numerics, minimal chrome, keyboard-first.
# --------------------------------------------------------------------------

def variant_d(parent, F, mode, S):
    pad = max(2, S["pad"] // 2)
    root = ttk.Frame(parent, padding=(pad * 2, pad, pad * 2, pad))
    root.pack(fill="both", expand=True)

    bar = ttk.Frame(root)
    bar.pack(fill="x", pady=(0, pad))
    tk.Label(bar, text="D:\\Videos", font=F["subhead"]).pack(side="left")
    tk.Label(bar, text=f"{len(RECORDINGS)} clips · {len(SELECTED)} selected · 2.4 GB",
             font=F["caption"], fg=muted(mode)).pack(side="left", padx=(pad * 2, 0))
    for label in ("Settings", "Delete", "Stitch", "Combat logs"):
        ttk.Button(bar, text=label).pack(side="right", padx=(pad, 0))
    ttk.Button(bar, text="Upload", style="Accent.TButton").pack(side="right", padx=(pad, 0))

    style = ttk.Style()
    style.configure("Compact.Treeview", rowheight=int(20 * S["scale"]))
    cols = ("name", "when", "size", "dur", "link")
    tv = ttk.Treeview(root, columns=cols, show="headings", style="Compact.Treeview")
    for key, text, w, anchor in (("name", "recording", int(400 * S["scale"]), "w"),
                                 ("when", "when", int(130 * S["scale"]), "w"),
                                 ("size", "size", int(80 * S["scale"]), "e"),
                                 ("dur", "len", int(60 * S["scale"]), "e"),
                                 ("link", "yt", int(50 * S["scale"]), "center")):
        tv.heading(key, text=text)
        tv.column(key, width=w, anchor=anchor, stretch=(key == "name"))
    for i, r in enumerate(RECORDINGS):
        tv.insert("", "end", values=(r["name"], when_str(r["when"], True),
                                     size_str(r["size_mb"]), dur_str(r["secs"]),
                                     "✓" if r["link"] else ""),
                  tags=("sel" if i in SELECTED else "",))
    tv.tag_configure("sel", background="#2d4f67" if mode == "dark" else "#dbeafe")
    tv.pack(fill="both", expand=True)

    tk.Label(root, text="space select · a all · u upload · d delete · / filter",
             font=F["caption"], fg=muted(mode)).pack(anchor="w", pady=(pad, 0))


VARIANTS = [
    ("A", "Content first", variant_a),
    ("B", "Master–detail", variant_b),
    ("C", "Sectioned panels", variant_c),
    ("D", "Compact", variant_d),
]


class Mockup:
    def __init__(self, root):
        self.root = root
        self.index = 0
        self.mode = "dark"
        root.title("PROTOTYPE — main window directions")

        scaling = float(root.tk.call("tk", "scaling"))
        self.scale = round(scaling / (96 / 72), 2)
        self.S = {"scale": self.scale, "pad": max(4, int(round(8 * self.scale)))}

        sv_ttk.set_theme(self.mode)
        self.F = build_fonts(self.scale)

        self.host = ttk.Frame(root)
        self.host.pack(fill="both", expand=True)

        self.switch = ttk.Frame(root, padding=self.S["pad"])
        self.switch.pack(fill="x", side="bottom")
        ttk.Separator(root, orient="horizontal").pack(fill="x", side="bottom")
        ttk.Button(self.switch, text="←", width=3, command=self.prev).pack(side="left")
        self.label = ttk.Label(self.switch, text="")
        self.label.pack(side="left", padx=self.S["pad"])
        ttk.Button(self.switch, text="→", width=3, command=self.next).pack(side="left")
        ttk.Button(self.switch, text="Toggle light/dark",
                   command=self.toggle_mode).pack(side="right")
        ttk.Label(self.switch, text="←/→ to switch  ·  this bar is not part of the design",
                  foreground=muted(self.mode)).pack(side="right", padx=self.S["pad"])

        root.bind("<Left>", lambda e: self.prev())
        root.bind("<Right>", lambda e: self.next())
        self.render()

    def render(self):
        for c in self.host.winfo_children():
            c.destroy()
        key, name, fn = VARIANTS[self.index]
        self.label.config(text=f"{key} — {name}    ({self.index+1}/{len(VARIANTS)})")
        fn(self.host, self.F, self.mode, self.S)

    def next(self):
        self.index = (self.index + 1) % len(VARIANTS)
        self.render()

    def prev(self):
        self.index = (self.index - 1) % len(VARIANTS)
        self.render()

    def toggle_mode(self):
        self.mode = "light" if self.mode == "dark" else "dark"
        sv_ttk.set_theme(self.mode)
        self.render()


def main():
    set_dpi_awareness()
    root = tk.Tk()
    root.tk.call("tk", "scaling", system_dpi() / 72.0)
    scale = round(float(root.tk.call("tk", "scaling")) / (96 / 72), 2)
    root.geometry(f"{int(1180*scale)}x{int(760*scale)}")
    root.minsize(int(900 * scale), int(600 * scale))
    Mockup(root)
    root.mainloop()


if __name__ == "__main__":
    main()
