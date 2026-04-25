import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading

sys.path.insert(0, os.path.dirname(__file__))                        

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from ga import run_ga
from csp import get_violations
from utils import format_schedule_text, get_subject_summary, priority_label
BG      = "#0F0F1A"
PANEL   = "#161628"
CARD    = "#1E1E38"
ACCENT  = "#6C63FF"
ACCENT2 = "#FF6B6B"
GREEN   = "#43D9AD"
YELLOW  = "#FFD166"
TEXT    = "#E8E8F0"
SUBTEXT = "#888899"
BORDER  = "#2A2A45"

SUBJECT_COLORS = [
    "#6C63FF","#FF6B6B","#43D9AD","#FFD166",
    "#F78C6C","#C792EA","#89DDFF","#FF5370"
]
FONT_NAME = "Arial"
class StudyPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Smart Study Planner  |  GA + CSP")
        self.root.configure(bg=BG)
        self.root.geometry("1300x860")
        self.root.minsize(1000, 680)

        self.subjects_data   = []
        self.best_schedule   = None
        self.fitness_history = []

        self._build_header()
        self._build_body()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=PANEL, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="  AI Smart Study Planner",
                 font=(FONT_NAME, 20, "bold"), bg=PANEL, fg=ACCENT
                 ).pack(side="left", padx=18)
        tk.Label(hdr, text="Genetic Algorithm  x  Constraint Satisfaction",
                 font=(FONT_NAME, 10), bg=PANEL, fg=SUBTEXT
                 ).pack(side="left")
        self.status_var = tk.StringVar(value="Ready — add subjects then click Generate")
        tk.Label(hdr, textvariable=self.status_var,
                 font=(FONT_NAME, 10, "bold"), bg=PANEL, fg=GREEN
                 ).pack(side="right", padx=20)

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg=PANEL, width=340)
        sidebar.pack(side="left", fill="y", padx=(8, 6), pady=8)
        sidebar.pack_propagate(False)

        scroll_canvas = tk.Canvas(sidebar, bg=PANEL, bd=0,
                                  highlightthickness=0, width=320)
        vsb = tk.Scrollbar(sidebar, orient="vertical",
                            command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        scroll_canvas.pack(side="top", fill="both", expand=True)

        inner = tk.Frame(scroll_canvas, bg=PANEL)
        win_id = scroll_canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(e):
            scroll_canvas.itemconfig(win_id, width=e.width)
        scroll_canvas.bind("<Configure>", _resize)

        def _scroll_update(e):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        inner.bind("<Configure>", _scroll_update)

        def _mousewheel(e):
            scroll_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        scroll_canvas.bind_all("<MouseWheel>", _mousewheel)

        self._build_input_section(inner)

        pin = tk.Frame(sidebar, bg="#0D0D1A", pady=10)
        pin.pack(side="bottom", fill="x")

        tk.Frame(pin, bg=ACCENT, height=2).pack(fill="x", pady=(0, 8))

        self.progress_var = tk.DoubleVar()
        pb_style = ttk.Style()
        pb_style.theme_use("default")
        pb_style.configure("GA.Horizontal.TProgressbar",
                           troughcolor=CARD, background=GREEN,
                           thickness=8, borderwidth=0)
        ttk.Progressbar(pin, variable=self.progress_var, maximum=100,
                        style="GA.Horizontal.TProgressbar"
                        ).pack(fill="x", padx=12, pady=(0, 8))

        self.run_btn = tk.Button(
            pin,
            text="  GENERATE SCHEDULE  ",
            command=self._run_ga,
            bg=GREEN, fg="#0A0A0A",
            activebackground="#2fbf8a", activeforeground="#0A0A0A",
            font=(FONT_NAME, 13, "bold"),
            relief="flat", cursor="hand2",
            pady=14, bd=0
        )
        self.run_btn.pack(fill="x", padx=12, pady=(0, 4))

        self.gen_status = tk.Label(pin, text="Add 2+ subjects to begin",
                                   bg="#0D0D1A", fg=SUBTEXT,
                                   font=(FONT_NAME, 9))
        self.gen_status.pack()

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True,
                    padx=(0, 8), pady=8)
        self._build_output_tabs(right)

    def _build_input_section(self, parent):
        P = {"bg": PANEL}
        section_title(parent, "ADD SUBJECT")

        form = tk.Frame(parent, **P)
        form.pack(fill="x", padx=14, pady=(4, 2))

        rows = [
            ("Subject Name",    "entry",   None),
            ("Study Hours",     "spin",    (1, 8)),
            ("Difficulty 1-5",  "spin",    (1, 5)),
            ("Preferred Time",  "combo",   ["Morning", "Evening"]),
        ]
        self.name_var     = tk.StringVar()
        self.hours_var    = tk.IntVar(value=2)
        self.diff_var     = tk.IntVar(value=3)
        self.pref_var     = tk.StringVar(value="Morning")

        vars_map = [self.name_var, self.hours_var, self.diff_var, self.pref_var]

        for i, (label, kind, opts) in enumerate(rows):
            tk.Label(form, text=label, bg=PANEL, fg=SUBTEXT,
                     font=(FONT_NAME, 10)).grid(row=i, column=0, sticky="w", pady=4)
            var = vars_map[i]
            if kind == "entry":
                w = mk_entry(form, var)
            elif kind == "spin":
                w = mk_spin(form, var, opts[0], opts[1])
            elif kind == "combo":
                w = ttk.Combobox(form, textvariable=var, values=opts,
                                 width=13, state="readonly",
                                 font=(FONT_NAME, 10))
            w.grid(row=i, column=1, sticky="ew", padx=(8, 0), pady=4)
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Priority", bg=PANEL, fg=SUBTEXT,
                 font=(FONT_NAME, 10)).grid(row=4, column=0, sticky="w", pady=4)
        self.priority_var = tk.IntVar(value=2)
        pf = tk.Frame(form, **P)
        pf.grid(row=4, column=1, sticky="w", padx=(8, 0))
        for val, lbl, col in [(1,"Low",SUBTEXT),(2,"Med",YELLOW),(3,"High",ACCENT2)]:
            tk.Radiobutton(pf, text=lbl, variable=self.priority_var, value=val,
                           bg=PANEL, fg=col, selectcolor=CARD,
                           activebackground=PANEL, font=(FONT_NAME, 10)
                           ).pack(side="left", padx=2)

        btn_row = tk.Frame(parent, **P)
        btn_row.pack(fill="x", padx=14, pady=(6, 2))
        mk_btn(btn_row, "+ Add Subject", self._add_subject, ACCENT
               ).pack(side="left", fill="x", expand=True)
        mk_btn(btn_row, "Clear All", self._clear_subjects, "#3A3A55"
               ).pack(side="left", fill="x", expand=True, padx=(6, 0))

        divider(parent)
        section_title(parent, "SUBJECTS ADDED")

        self.subject_listbox = tk.Listbox(
            parent, bg=CARD, fg=TEXT, font=(FONT_NAME, 10),
            selectbackground=ACCENT, height=6,
            bd=0, highlightthickness=1, highlightcolor=BORDER,
            activestyle="none"
        )
        self.subject_listbox.pack(fill="x", padx=14)

        self.count_label = tk.Label(parent, text="0 subjects added",
                                    bg=PANEL, fg=ACCENT2,
                                    font=(FONT_NAME, 9))
        self.count_label.pack(anchor="w", padx=14, pady=(2, 0))

        mk_btn(parent, "Remove Selected", self._remove_subject, "#3A3A55"
               ).pack(fill="x", padx=14, pady=(4, 2))

        divider(parent)
        section_title(parent, "GA SETTINGS")

        ga = tk.Frame(parent, bg=PANEL)
        ga.pack(fill="x", padx=14, pady=(4, 2))

        self.pop_var   = tk.IntVar(value=30)
        self.gen_var   = tk.IntVar(value=50)
        self.break_var = tk.IntVar(value=2)
        self.mut_var   = tk.DoubleVar(value=0.1)

        settings = [
            ("Population", self.pop_var, 10, 100),
            ("Generations", self.gen_var, 10, 200),
            ("Break After (hrs)", self.break_var, 1, 5),
        ]
        for i, (lbl, var, lo, hi) in enumerate(settings):
            tk.Label(ga, text=lbl, bg=PANEL, fg=SUBTEXT,
                     font=(FONT_NAME, 10)).grid(row=i, column=0, sticky="w", pady=3)
            mk_spin(ga, var, lo, hi).grid(row=i, column=1, sticky="ew",
                                           padx=(8, 0), pady=3)

        tk.Label(ga, text="Mutation Rate", bg=PANEL, fg=SUBTEXT,
                 font=(FONT_NAME, 10)).grid(row=3, column=0, sticky="w", pady=3)
        tk.Scale(ga, variable=self.mut_var, from_=0.01, to=0.5,
                 orient="horizontal", resolution=0.01,
                 bg=PANEL, fg=TEXT, troughcolor=CARD,
                 highlightthickness=0, font=(FONT_NAME, 9)
                 ).grid(row=3, column=1, sticky="ew", padx=(8, 0))
        ga.columnconfigure(1, weight=1)

        tk.Frame(parent, bg=PANEL, height=30).pack()

    def _build_output_tabs(self, parent):
        nb_style = ttk.Style()
        nb_style.theme_use("default")
        nb_style.configure("TNotebook", background=BG, borderwidth=0)
        nb_style.configure("TNotebook.Tab", background=CARD, foreground=SUBTEXT,
                           padding=[16, 7], font=(FONT_NAME, 11))
        nb_style.map("TNotebook.Tab",
                     background=[("selected", PANEL)],
                     foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True)

        self.tab_sched = tk.Frame(nb, bg=PANEL)
        nb.add(self.tab_sched, text="  Schedule  ")
        self._build_schedule_tab(self.tab_sched)

        self.tab_graph = tk.Frame(nb, bg=PANEL)
        nb.add(self.tab_graph, text="  Fitness Graph  ")
        self._build_graph_tab(self.tab_graph)

        self.tab_csp = tk.Frame(nb, bg=PANEL)
        nb.add(self.tab_csp, text="  CSP Visualizer  ")
        self._build_csp_tab(self.tab_csp)

        self.tab_sum = tk.Frame(nb, bg=PANEL)
        nb.add(self.tab_sum, text="  Summary  ")
        self._build_summary_tab(self.tab_sum)

    def _build_schedule_tab(self, parent):
        top = tk.Frame(parent, bg=PANEL)
        top.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(top, text="Optimized Schedule", bg=PANEL, fg=TEXT,
                 font=(FONT_NAME, 14, "bold")).pack(side="left")
        self.fitness_label = tk.Label(top, text="Fitness: —",
                                      bg=PANEL, fg=GREEN,
                                      font=(FONT_NAME, 12, "bold"))
        self.fitness_label.pack(side="right")

        self.fig_s, self.ax_s = plt.subplots(figsize=(9, 5))
        self.fig_s.patch.set_facecolor(PANEL)
        self.canvas_s = FigureCanvasTkAgg(self.fig_s, master=parent)
        self.canvas_s.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=6)
        self._placeholder(self.ax_s, self.canvas_s,
                          "Run GA to see your optimized schedule here")

    def _draw_schedule(self, schedule):
        ax = self.ax_s; ax.clear()
        ax.set_facecolor(BG); self.fig_s.patch.set_facecolor(PANEL)
        unique = [s for s in dict.fromkeys(e[1] for e in schedule) if s != "Break"]
        cmap = {"Break": "#2A2A45"}
        for i, s in enumerate(unique):
            cmap[s] = SUBJECT_COLORS[i % len(SUBJECT_COLORS)]
        n = len(schedule)
        for i, (slot, sub) in enumerate(schedule):
            y = n - i - 1
            ax.barh(y, 1, height=0.72, color=cmap[sub], alpha=0.92,
                    edgecolor=PANEL, linewidth=1.5)
            label = f"  Break" if sub == "Break" else f"  {sub}"
            ax.text(0.025, y, f"{slot}{label}", va="center", color="white",
                    fontsize=10, fontfamily=FONT_NAME, fontweight="bold")
        ax.set_xlim(0, 1.02); ax.set_ylim(-0.6, n - 0.3)
        ax.axis("off")
        ax.set_title("Optimized Study Timetable", color=TEXT,
                     fontfamily=FONT_NAME, fontsize=14, pad=10)
        patches = [mpatches.Patch(color=c, label=s) for s, c in cmap.items()]
        ax.legend(handles=patches, fontsize=9, loc="lower right",
                  facecolor=CARD, edgecolor=BORDER, labelcolor=TEXT)
        self.canvas_s.draw()

    def _build_graph_tab(self, parent):
        self.fig_g, self.ax_g = plt.subplots(figsize=(9, 5))
        self.fig_g.patch.set_facecolor(PANEL)
        self.canvas_g = FigureCanvasTkAgg(self.fig_g, master=parent)
        self.canvas_g.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self._placeholder(self.ax_g, self.canvas_g,
                          "Fitness history will appear after running GA")

    def _draw_fitness(self, history):
        ax = self.ax_g; ax.clear()
        ax.set_facecolor(BG); self.fig_g.patch.set_facecolor(PANEL)
        x = list(range(1, len(history) + 1))
        ax.plot(x, history, color=ACCENT, linewidth=2.2, zorder=3)
        ax.fill_between(x, history, alpha=0.15, color=ACCENT)
        best_g = history.index(max(history)) + 1
        ax.axvline(best_g, color=GREEN, linestyle="--", linewidth=1.3, alpha=0.8)
        ax.scatter([best_g], [max(history)], color=GREEN, zorder=5, s=70)
        ax.annotate(f"Best: {max(history)}", xy=(best_g, max(history)),
                    xytext=(best_g + 0.5, max(history) - 3),
                    color=GREEN, fontsize=10, fontfamily=FONT_NAME)
        ax.set_xlabel("Generation", color=SUBTEXT, fontfamily=FONT_NAME, fontsize=11)
        ax.set_ylabel("Fitness Score", color=SUBTEXT, fontfamily=FONT_NAME, fontsize=11)
        ax.set_title("GA Fitness Progression Over Generations",
                     color=TEXT, fontfamily=FONT_NAME, fontsize=14)
        ax.tick_params(colors=SUBTEXT, labelsize=9)
        for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
        for sp in ["bottom", "left"]: ax.spines[sp].set_color(BORDER)
        ax.grid(axis="y", color=BORDER, linestyle="--", alpha=0.5)
        self.canvas_g.draw()

    def _build_csp_tab(self, parent):
        self.fig_c, self.ax_c = plt.subplots(figsize=(9, 5))
        self.fig_c.patch.set_facecolor(PANEL)
        self.canvas_c = FigureCanvasTkAgg(self.fig_c, master=parent)
        self.canvas_c.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self._placeholder(self.ax_c, self.canvas_c,
                          "CSP constraint analysis will appear here")

    def _draw_csp(self, schedule, subjects_data):
        ax = self.ax_c; ax.clear()
        ax.set_facecolor(BG); self.fig_c.patch.set_facecolor(PANEL)
        subjects     = [s["name"] for s in subjects_data]
        subject_hours = {s["name"]: s["hours"] for s in subjects_data}
        violations   = get_violations(schedule, subject_hours, subjects)
        n = len(schedule)
        for i, (slot, sub) in enumerate(schedule):
            y = n - i - 1
            color = GREEN if sub == "Break" else ACCENT
            if i > 0 and schedule[i-1][1] == sub and sub != "Break":
                color = ACCENT2
            ax.barh(y, 1, height=0.72, color=color, alpha=0.88,
                    edgecolor=PANEL, linewidth=1.5)
            ax.text(0.025, y,
                    f"{slot}  {'Break' if sub == 'Break' else sub}",
                    va="center", color="white",
                    fontsize=10, fontfamily=FONT_NAME)
        valid = len(violations) == 0
        title = "All CSP Constraints Satisfied" if valid else \
                f"{len(violations)} Violation(s) Found"
        ax.set_title(title, color=GREEN if valid else ACCENT2,
                     fontfamily=FONT_NAME, fontsize=14, pad=8)
        if violations:
            ax.text(0.01, -0.08, "\n".join(violations),
                    transform=ax.transAxes, color=ACCENT2,
                    fontsize=9, fontfamily=FONT_NAME, va="top")
        ax.set_xlim(0, 1.02); ax.set_ylim(-0.6, n - 0.3)
        ax.axis("off")
        legend = [mpatches.Patch(color=GREEN, label="Break"),
                  mpatches.Patch(color=ACCENT, label="Valid Slot"),
                  mpatches.Patch(color=ACCENT2, label="Violation")]
        ax.legend(handles=legend, fontsize=9, loc="lower right",
                  facecolor=CARD, edgecolor=BORDER, labelcolor=TEXT)
        self.canvas_c.draw()

    def _build_summary_tab(self, parent):
        self.fig_sum, self.axes_sum = plt.subplots(1, 2, figsize=(9, 5))
        self.fig_sum.patch.set_facecolor(PANEL)
        self.canvas_sum = FigureCanvasTkAgg(self.fig_sum, master=parent)
        self.canvas_sum.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        for ax in self.axes_sum:
            self._placeholder(ax, None, "Run GA first")
        self.canvas_sum.draw()

    def _draw_summary(self, schedule, subjects_data):
        from collections import Counter
        ax1, ax2 = self.axes_sum
        ax1.clear(); ax2.clear()
        self.fig_sum.patch.set_facecolor(PANEL)
        counts = Counter(s for _, s in schedule if s != "Break")
        names  = [s["name"] for s in subjects_data]
        alloc  = [s["hours"] for s in subjects_data]
        sched  = [counts.get(n, 0) for n in names]
        colors = [SUBJECT_COLORS[i % len(SUBJECT_COLORS)] for i in range(len(names))]
        x = np.arange(len(names)); w = 0.35
        ax1.bar(x - w/2, alloc, w, label="Allocated", color=ACCENT, alpha=0.75)
        ax1.bar(x + w/2, sched, w, label="Scheduled", color=GREEN, alpha=0.9)
        ax1.set_xticks(x)
        ax1.set_xticklabels(names, color=SUBTEXT, fontsize=9,
                            rotation=20, fontfamily=FONT_NAME)
        ax1.set_ylabel("Hours", color=SUBTEXT, fontfamily=FONT_NAME)
        ax1.set_title("Hours Allocated vs Scheduled",
                      color=TEXT, fontfamily=FONT_NAME, fontsize=12)
        ax1.tick_params(colors=SUBTEXT, labelsize=9)
        ax1.set_facecolor(BG)
        ax1.legend(fontsize=9, facecolor=CARD, edgecolor=BORDER, labelcolor=TEXT)
        for sp in ["top", "right"]: ax1.spines[sp].set_visible(False)
        for sp in ["bottom", "left"]: ax1.spines[sp].set_color(BORDER)
        ax1.grid(axis="y", color=BORDER, linestyle="--", alpha=0.4)
        if sum(sched) > 0:
            ax2.pie(sched, labels=names, colors=colors, autopct="%1.0f%%",
                    textprops={"color": TEXT, "fontsize": 9, "fontfamily": FONT_NAME},
                    wedgeprops={"edgecolor": PANEL, "linewidth": 1.5})
        ax2.set_facecolor(BG)
        ax2.set_title("Schedule Distribution",
                      color=TEXT, fontfamily=FONT_NAME, fontsize=12)
        self.fig_sum.tight_layout(pad=2)
        self.canvas_sum.draw()

    def _placeholder(self, ax, canvas, msg):
        ax.clear(); ax.set_facecolor(BG)
        ax.text(0.5, 0.5, msg, ha="center", va="center",
                color=SUBTEXT, fontsize=12, fontfamily=FONT_NAME,
                transform=ax.transAxes)
        ax.axis("off")
        if canvas:
            canvas.draw()

    def _add_subject(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a subject name.")
            return
        if any(s["name"] == name for s in self.subjects_data):
            messagebox.showwarning("Duplicate", f"'{name}' is already added.")
            return
        s = {
            "name":      name,
            "hours":     self.hours_var.get(),
            "priority":  self.priority_var.get(),
            "difficulty":self.diff_var.get(),
            "preferred": self.pref_var.get(),
        }
        self.subjects_data.append(s)
        self.subject_listbox.insert(
            "end",
            f"  {name}  [{s['hours']}h | {priority_label(s['priority'])} | "
            f"D:{s['difficulty']} | {s['preferred']}]"
        )
        self.name_var.set("")
        self._update_count()
        self.status_var.set(
            f"{len(self.subjects_data)} subject(s) — click GENERATE"
        )

    def _remove_subject(self):
        sel = self.subject_listbox.curselection()
        if not sel: return
        idx = sel[0]
        self.subject_listbox.delete(idx)
        self.subjects_data.pop(idx)
        self._update_count()

    def _clear_subjects(self):
        self.subjects_data.clear()
        self.subject_listbox.delete(0, "end")
        self._update_count()
        self.status_var.set("Ready — add subjects then click Generate")

    def _update_count(self):
        n = len(self.subjects_data)
        self.count_label.config(
            text=f"{n} subject(s) added",
            fg=GREEN if n >= 2 else ACCENT2
        )
        self.gen_status.config(
            text="Ready to generate!" if n >= 2 else "Add 2+ subjects to begin",
            fg=GREEN if n >= 2 else SUBTEXT
        )

    def _run_ga(self):
        if len(self.subjects_data) < 2:
            messagebox.showwarning("Not Enough Subjects", "Add 2+ subjects.")
            return

        self.run_btn.config(state="disabled", text="  Running GA...  ", bg=SUBTEXT)
        self.status_var.set("Running Genetic Algorithm...")
        self.progress_var.set(0)

        def worker():
            preferred = {s["name"]: s["preferred"] for s in self.subjects_data}
            total     = sum(s["hours"] for s in self.subjects_data)
            gens      = self.gen_var.get()

            def on_progress(gen, fit):
                self.progress_var.set((gen / gens) * 100)
                self.status_var.set(f"Gen {gen}/{gens} | Best Fitness: {fit}")

            sched, fitness, history = run_ga(
                subjects_data    = self.subjects_data,
                preferred_times  = preferred,
                total_hours      = total,
                break_interval   = self.break_var.get(),
                population_size  = self.pop_var.get(),
                generations      = gens,
                base_mutation_rate = self.mut_var.get(),
                progress_callback  = on_progress,
            )
            self.root.after(0, lambda: self._on_done(sched, fitness, history))

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self, schedule, fitness, history):
        self.best_schedule   = schedule
        self.fitness_history = history
        self.fitness_label.config(text=f"Fitness: {fitness}")
        self.status_var.set(f"Done! | Fitness: {fitness}")
        self.progress_var.set(100)
        self.run_btn.config(state="normal", text="  GENERATE SCHEDULE  ", bg=GREEN)
        self._draw_schedule(schedule)
        self._draw_fitness(history)
        self._draw_csp(schedule, self.subjects_data)
        self._draw_summary(schedule, self.subjects_data)

def section_title(parent, text):
    tk.Label(parent, text=text, bg=PANEL, fg=ACCENT,
             font=(FONT_NAME, 11, "bold")).pack(anchor="w", padx=14, pady=(12, 2))

def divider(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=14, pady=6)

def mk_entry(parent, var):
    return tk.Entry(parent, textvariable=var, bg=CARD, fg=TEXT,
                    insertbackground=TEXT, relief="flat",
                    font=(FONT_NAME, 11), bd=4)

def mk_spin(parent, var, lo, hi):
    return tk.Spinbox(parent, textvariable=var, from_=lo, to=hi,
                      bg=CARD, fg=TEXT, buttonbackground=CARD,
                      relief="flat", font=(FONT_NAME, 11), width=8)

def mk_btn(parent, text, cmd, color):
    return tk.Button(parent, text=text, command=cmd,
                      bg=color, fg=TEXT, activebackground=color,
                      relief="flat", font=(FONT_NAME, 10, "bold"),
                      cursor="hand2", pady=6, bd=0)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyPlannerApp(root)
    demo = [
        {"name": "AI",       "hours": 2, "priority": 3, "difficulty": 5, "preferred": "Morning"},
        {"name": "OS",       "hours": 2, "priority": 2, "difficulty": 3, "preferred": "Morning"},
        {"name": "Database", "hours": 2, "priority": 2, "difficulty": 4, "preferred": "Evening"},
        {"name": "Networks", "hours": 1, "priority": 1, "difficulty": 2, "preferred": "Evening"},
        {"name": "Math",     "hours": 1, "priority": 3, "difficulty": 4, "preferred": "Morning"},
    ]
    for s in demo:
        app.subjects_data.append(s)
        app.subject_listbox.insert("end", f"  {s['name']}  [{s['hours']}h | Med | D:{s['difficulty']} | {s['preferred']}]")
    app._update_count()
    app.status_var.set("5 demo subjects loaded — click GENERATE!")
    root.mainloop()