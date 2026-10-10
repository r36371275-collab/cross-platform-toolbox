#!/usr/bin/env python3
"""A harmless, animated fake-screen-artifact preview built with Tkinter."""

from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk


class ArtifactPreview:
    MODES = ("Color bands", "Scan lines", "Pixel noise", "RGB split")
    PALETTE = ("#ff375f", "#25d9ff", "#ffd166", "#a970ff", "#8cff6b")

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Screen Artifact Simulator")
        self.root.geometry("960x620")
        self.root.minsize(720, 460)
        self.root.configure(bg="#10141d")

        self.running = False
        self.after_id: str | None = None
        self.settings: tk.Toplevel | None = None
        self.mode = tk.StringVar(value=self.MODES[0])
        self.intensity = tk.IntVar(value=45)
        self.speed = tk.IntVar(value=12)
        self.use_color = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Stopped")

        self._build_main_window()
        self.root.bind_all("<Control-KeyPress>", self._handle_hotkey)

    def _build_main_window(self) -> None:
        header = tk.Frame(self.root, bg="#10141d")
        header.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(
            header, text="SCREEN ARTIFACT SIMULATOR", bg="#10141d", fg="#f3f6ff",
            font=("TkDefaultFont", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header, text="A fake glitch effect, drawn only inside this preview window.",
            bg="#10141d", fg="#9ca8bc", font=("TkDefaultFont", 10),
        ).pack(anchor="w", pady=(4, 0))

        self.canvas = tk.Canvas(
            self.root, bg="#080b12", highlightthickness=1,
            highlightbackground="#354055",
        )
        self.canvas.pack(fill="both", expand=True, padx=24, pady=12)
        self.canvas.bind("<Configure>", lambda _event: self._draw_frame())

        footer = tk.Frame(self.root, bg="#10141d")
        footer.pack(fill="x", padx=24, pady=(0, 20))
        self.toggle_button = ttk.Button(footer, text="Start effect", command=self.toggle_effect)
        self.toggle_button.pack(side="left")
        ttk.Button(footer, text="Settings  ·  Ctrl+Num 0", command=self.show_settings).pack(
            side="left", padx=(10, 0)
        )
        tk.Label(footer, textvariable=self.status, bg="#10141d", fg="#9ca8bc").pack(
            side="right"
        )
        self._draw_frame()

    def _handle_hotkey(self, event: tk.Event) -> str | None:
        if event.keysym in {"KP_0", "KP_Insert", "0"}:
            self.show_settings()
            return "break"
        return None

    def show_settings(self) -> None:
        if self.settings is not None and self.settings.winfo_exists():
            self.settings.deiconify()
            self.settings.lift()
            self.settings.focus_force()
            return

        dialog = tk.Toplevel(self.root)
        self.settings = dialog
        dialog.title("Artifact settings")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.configure(bg="#171d29")
        dialog.protocol("WM_DELETE_WINDOW", dialog.withdraw)

        body = tk.Frame(dialog, bg="#171d29", padx=20, pady=18)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Effect settings", bg="#171d29", fg="#f3f6ff",
                 font=("TkDefaultFont", 14, "bold")).pack(anchor="w", pady=(0, 14))

        tk.Label(body, text="Style", bg="#171d29", fg="#c4ccda").pack(anchor="w")
        ttk.Combobox(body, textvariable=self.mode, values=self.MODES, state="readonly",
                     width=28).pack(fill="x", pady=(4, 12))

        tk.Label(body, text="Intensity", bg="#171d29", fg="#c4ccda").pack(anchor="w")
        ttk.Scale(body, from_=5, to=100, variable=self.intensity, orient="horizontal").pack(
            fill="x", pady=(4, 12)
        )

        tk.Label(body, text="Animation speed", bg="#171d29", fg="#c4ccda").pack(anchor="w")
        ttk.Scale(body, from_=3, to=30, variable=self.speed, orient="horizontal").pack(
            fill="x", pady=(4, 8)
        )
        ttk.Checkbutton(body, text="Use bright colors", variable=self.use_color,
                        command=self._draw_frame).pack(anchor="w", pady=(2, 14))

        buttons = tk.Frame(body, bg="#171d29")
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Start / stop", command=self.toggle_effect).pack(side="left")
        ttk.Button(buttons, text="Close", command=dialog.withdraw).pack(side="right")

    def toggle_effect(self) -> None:
        if self.running:
            self.running = False
            if self.after_id is not None:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            self.toggle_button.configure(text="Start effect")
            self.status.set("Stopped")
            self._draw_frame()
            return

        self.running = True
        self.toggle_button.configure(text="Stop effect")
        self.status.set("Running — preview only")
        self._animate()

    def _draw_frame(self) -> None:
        if not hasattr(self, "canvas"):
            return
        canvas = self.canvas
        width, height = canvas.winfo_width(), canvas.winfo_height()
        if width < 10 or height < 10:
            return
        canvas.delete("all")
        canvas.create_rectangle(0, 0, width, height, fill="#080b12", outline="")

        # A subdued monitor grid gives the effect a clear preview surface.
        for y in range(0, height, 4):
            canvas.create_line(0, y, width, y, fill="#111722")
        canvas.create_text(width // 2, 26, text="GLITCH PREVIEW", fill="#6d7b92",
                           font=("TkFixedFont", 10, "bold"))

        if not self.running:
            canvas.create_text(width // 2, height // 2, text="EFFECT OFF", fill="#647087",
                               font=("TkDefaultFont", 20, "bold"))
            return

        count = max(3, int(self.intensity.get() / 5))
        mode = self.mode.get()
        for _ in range(count):
            y = random.randrange(45, max(46, height - 8))
            band_h = random.randint(1, max(2, self.intensity.get() // 5))
            x = random.randrange(0, max(1, width - 1))
            band_w = random.randint(max(2, width // 18), max(3, width))
            color = random.choice(self.PALETTE) if self.use_color.get() else "#d8e0ee"

            if mode == "Scan lines":
                canvas.create_line(0, y, width, y, fill=color, width=band_h)
            elif mode == "Pixel noise":
                size = random.randint(2, max(3, self.intensity.get() // 3))
                canvas.create_rectangle(x, y, x + size, y + size, fill=color, outline="")
            elif mode == "RGB split":
                canvas.create_rectangle(x, y, min(width, x + band_w), y + band_h,
                                        fill=color, outline="")
                canvas.create_rectangle(max(0, x - 5), y + band_h + 1,
                                        min(width, x + band_w - 5), y + band_h + 3,
                                        fill="#45eaff", outline="")
            else:
                canvas.create_rectangle(0, y, min(width, band_w), y + band_h,
                                        fill=color, outline="")

        delay = max(35, 1000 // max(3, self.speed.get()))
        self.after_id = self.root.after(delay, self._animate)

    def _animate(self) -> None:
        if self.running:
            self._draw_frame()


def main() -> None:
    root = tk.Tk()
    ArtifactPreview(root)
    root.mainloop()


if __name__ == "__main__":
    main()
