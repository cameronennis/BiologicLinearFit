"""Paste a Linear Fit result block and get the x-intercept (-offset / slope).

Run:  python3 x_intercept.py
"""
import re
import tkinter as tk

SIG_FIGS = 4  # significant figures for the displayed/copied value

PREFIXES = {"": 1, "m": 1e-3, "u": 1e-6, "µ": 1e-6, "k": 1e3, "M": 1e6, "G": 1e9}
# Digits may be grouped with spaces as thousands separators, e.g. "-1 025"
SPACES = "    "
NUM = rf"([-+]?[\d.{SPACES}]+(?:[eE][-+]?\d+)?)"


def parse_value(text, name):
    """Return the numeric value of 'name = <number> [prefix]Ohm...', scaled by any SI prefix."""
    m = re.search(rf"{name}\s*=\s*{NUM}\s*([mukMGµ]?)Ohm", text)
    if not m:
        raise ValueError(f"Could not find '{name}' in pasted text")
    number = re.sub(f"[{SPACES}]", "", m.group(1))
    try:
        return float(number) * PREFIXES[m.group(2)]
    except ValueError:
        raise ValueError(f"Could not read '{name}' value: {m.group(1).strip()}")


def x_intercept(text):
    slope = parse_value(text, "slope")
    offset = parse_value(text, "offset")
    if slope == 0:
        raise ValueError("Slope is zero")
    return -offset / slope


class App:
    def __init__(self, root):
        self.root = root
        self.value = None
        root.title("Linear Fit x-intercept")

        tk.Label(root, text="Paste Linear Fit results:").pack(anchor="w", padx=10, pady=(10, 0))
        self.box = tk.Text(root, width=45, height=7)
        self.box.pack(padx=10, pady=5)
        self.box.bind("<<Modified>>", self.on_change)

        buttons = tk.Frame(root)
        buttons.pack(pady=5)
        tk.Button(buttons, text="Paste from clipboard", command=self.paste).pack(side="left", padx=5)
        tk.Button(buttons, text="Copy value", command=self.copy).pack(side="left", padx=5)
        tk.Button(buttons, text="Clear", command=self.clear).pack(side="left", padx=5)

        self.result = tk.Label(root, text="x-intercept: —", font=("Helvetica", 16))
        self.result.pack(pady=5)
        self.status = tk.Label(root, text="", fg="gray")
        self.status.pack(pady=(0, 10))

        self.box.focus_set()

    def on_change(self, _event=None):
        self.box.edit_modified(False)
        text = self.box.get("1.0", "end")
        try:
            x = x_intercept(text)
            self.value = f"{x:.{SIG_FIGS}g}"
            self.result.config(text=f"x-intercept: {self.value} Ohm", fg="black")
            self.status.config(text="")
        except ValueError as e:
            self.value = None
            self.result.config(text="x-intercept: —")
            self.status.config(text=str(e) if text.strip() else "")

    def paste(self):
        try:
            clip = self.root.clipboard_get()
        except tk.TclError:
            self.status.config(text="Clipboard is empty")
            return
        self.box.delete("1.0", "end")
        self.box.insert("1.0", clip)

    def copy(self):
        if self.value is None:
            self.status.config(text="Nothing to copy")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.value)
        self.root.update()
        self.status.config(text=f"Copied {self.value}")

    def clear(self):
        self.box.delete("1.0", "end")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
