"""Small, accessible Tkinter components shared by the application screens.

The interface deliberately uses real Tk widgets: keyboard navigation, native
commands, and widget configuration continue to work without extra packages.
"""

import tkinter as tk
from tkinter import ttk


COLORS = {
    "bg": "#F4F6FB",
    "surface": "#FFFFFF",
    "ink": "#18243D",
    "muted": "#647087",
    "border": "#E1E6F0",
    "primary": "#4F46E5",
    "primary_hover": "#4338CA",
    "primary_pressed": "#3730A3",
    "on_primary": "#FFFFFF",
    "accent": "#4F46E5",
    "success": "#147D64",
    "success_bg": "#EAF7F1",
    "danger": "#C3394A",
    "danger_hover": "#AB2E3E",
    "danger_pressed": "#902535",
    "on_danger": "#FFFFFF",
    "danger_bg": "#FFF1F3",
    "navy": "#15243F",
    "soft": "#EEF0FF",
    "secondary_hover": "#E1E3FF",
    "secondary_pressed": "#D3D5F7",
    "ghost_hover": "#E9EDF5",
    "ghost_pressed": "#DBE1ED",
    "disabled_bg": "#E7EAF0",
    "disabled_fg": "#7A8598",
    "tile_empty": "#F6F7FC",
    "mode_easy": "#147D64",
    "mode_medium": "#4F46E5",
    "mode_hard": "#B43F65",
    "scroll": "#C7CEDD",
    "scroll_hover": "#A3AEC2",
}


THEMES = {
    "light": COLORS,
    "dark": {
        "bg": "#111827", "surface": "#1B2435", "ink": "#EDF2FA",
        "muted": "#B3BED2", "border": "#3E4C64",
        "primary": "#A79BFF", "primary_hover": "#B8AEFF",
        "primary_pressed": "#9788F2", "on_primary": "#171331",
        "accent": "#A79BFF", "success": "#6CD8B3",
        "success_bg": "#193B34", "danger": "#FF97A6",
        "danger_hover": "#FFADB9", "danger_pressed": "#EE8295",
        "on_danger": "#34121B", "danger_bg": "#3D2431",
        "navy": "#172039", "soft": "#302E50",
        "secondary_hover": "#3B365F", "secondary_pressed": "#453D70",
        "ghost_hover": "#2B374B", "ghost_pressed": "#35435A",
        "disabled_bg": "#303B4E", "disabled_fg": "#97A5BD",
        "tile_empty": "#232E43", "mode_easy": "#6CD8B3",
        "mode_medium": "#A79BFF", "mode_hard": "#F2A1BE",
        "scroll": "#52617A", "scroll_hover": "#7184A3",
    },
}


def colors_for(widget):
    """Read this window's palette without changing other application windows."""
    return getattr(widget.winfo_toplevel(), "_theme_colors", COLORS)


def apply_theme(root, theme_name):
    """Recolor existing controls in place, retaining form and keyboard state.

    Semantic roles are remembered after the first change so a light/dark round
    trip does not confuse colors shared by multiple roles. Explicit feedback
    palettes on ActionButton instances remain under the game renderer's control.
    """
    if theme_name not in THEMES:
        raise ValueError(f"Unknown theme: {theme_name}")
    old, new = colors_for(root), THEMES[theme_name]
    root._theme_colors = new
    root._theme_name = theme_name
    color_roles = {}
    for role, value in old.items():
        color_roles.setdefault(root.winfo_rgb(value), role)
    foreground_options = {
        "foreground", "activeforeground", "disabledforeground",
        "selectforeground", "insertbackground",
    }
    options = (
        "background", "foreground", "activebackground", "activeforeground",
        "disabledforeground", "highlightbackground", "highlightcolor",
        "insertbackground", "selectbackground", "selectforeground",
        "readonlybackground", "disabledbackground", "troughcolor",
    )
    white = root.winfo_rgb("white")

    def visit(widget):
        if isinstance(widget, ActionButton):
            widget.apply_theme()
            return
        if not isinstance(widget, ttk.Widget):
            roles = getattr(widget, "_theme_roles", {})
            updates = {}
            available = widget.keys()
            # Filled game tiles use white letters and stable feedback colors.
            fixed_fill = False
            if "foreground" in available and "background" in available:
                fixed_fill = (
                    widget.winfo_rgb(widget.cget("foreground")) == white
                    and widget.winfo_rgb(widget.cget("background")) != white
                )
            for option in options:
                if option not in available:
                    continue
                value = widget.cget(option)
                if not value:
                    continue
                try:
                    rgb = widget.winfo_rgb(value)
                except tk.TclError:
                    continue
                role = roles.get(option)
                if role and rgb != root.winfo_rgb(old[role]):
                    role = None  # A screen has assigned a different role.
                if role is None:
                    if option == "selectforeground" and rgb == root.winfo_rgb(old["on_primary"]):
                        role = "on_primary"
                    # White foregrounds on colored illustrations and tiles are
                    # intentionally constant; white surfaces still follow theme.
                    if role is None and option in foreground_options and rgb == white:
                        continue
                    if fixed_fill and option in ("background", "highlightbackground"):
                        continue
                    role = role or color_roles.get(rgb)
                if role:
                    roles[option] = role
                    updates[option] = new[role]
            widget._theme_roles = roles
            if updates:
                widget.configure(**updates)
        for child in widget.winfo_children():
            visit(child)

    visit(root)
    configure_styles(root)
    return new


def configure_styles(root):
    """Apply a consistent font and neutral, readable ttk table controls."""
    colors = colors_for(root)
    root.option_add("*Font", ("Segoe UI", 11))
    root.option_add("*Entry.selectBackground", colors["primary"])
    root.option_add("*Entry.selectForeground", colors["on_primary"])
    root.option_add("*Listbox.selectBackground", colors["primary"])
    root.option_add("*Listbox.selectForeground", colors["on_primary"])
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure(
        "Treeview", background=colors["surface"],
        fieldbackground=colors["surface"], foreground=colors["ink"],
        borderwidth=0, relief="flat", rowheight=42,
        font=("Segoe UI", 11),
    )
    style.configure(
        "Treeview.Heading", background=colors["bg"],
        foreground=colors["muted"], borderwidth=0, relief="flat",
        padding=(12, 12), font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "Treeview", background=[("selected", colors["soft"])],
        foreground=[("selected", colors["primary"])],
    )
    style.map("Treeview.Heading", background=[("active", colors["ghost_hover"])])
    style.configure(
        "Vertical.TScrollbar", background=colors["scroll"],
        troughcolor=colors["bg"], bordercolor=colors["bg"],
        arrowcolor=colors["muted"], lightcolor=colors["scroll"],
        darkcolor=colors["scroll"], gripcount=0, borderwidth=0,
        arrowsize=12,
    )
    style.map("Vertical.TScrollbar", background=[("active", colors["scroll_hover"])])
    return style


def label(parent, text="", size=11, bold=False, color=None,
          wraplength=None, **kwargs):
    """Create a label, optionally wrapping inside its parent as it resizes.

    Labels keep their natural width unless ``wraplength`` is supplied. An
    explicit positive value is a maximum that shrinks with the parent, keeping
    long headings and hints within a responsive page.
    Explicit widget options (including a background) take precedence.
    """
    options = {
        "text": text, "bg": parent.cget("bg"),
        "fg": color or colors_for(parent)["ink"],
        "font": ("Segoe UI", size, "bold" if bold else "normal"),
        "wraplength": wraplength or 0,
        "borderwidth": 0, "highlightthickness": 0,
    }
    options.update(kwargs)
    widget = tk.Label(parent, **options)
    if not wraplength or float(wraplength) <= 0:
        return widget
    maximum = float(wraplength)

    def fit(event):
        if event.width < 20 or not widget.winfo_exists():
            return
        try:
            parent_padding = parent.winfo_pixels(parent.cget("padx")) * 2
        except tk.TclError:
            parent_padding = 0
        available = max(40, event.width - parent_padding - 4)
        available = min(maximum, available)
        if float(widget.cget("wraplength")) != available:
            widget.configure(wraplength=available)

    binding = parent.bind("<Configure>", fit, add="+")

    def remove_binding(event):
        if event.widget is widget:
            try:
                parent.unbind("<Configure>", binding)
            except tk.TclError:
                pass  # The parent can be destroyed along with this label.

    widget.bind("<Destroy>", remove_binding, add="+")
    return widget


def card(parent, padding=20, bg=None):
    """Return a flat card with generous internal spacing and a subtle edge."""
    colors = colors_for(parent)
    return tk.Frame(
        parent, bg=bg or colors["surface"], padx=padding, pady=padding,
        bd=0, highlightthickness=1, highlightbackground=colors["border"],
        highlightcolor=colors["border"],
    )


class ActionButton(tk.Button):
    """A real Tk button with clear hover, pressed, focus, and disabled states."""

    _PALETTES = {
        "primary": ("primary", "primary_hover", "primary_pressed", "on_primary"),
        "secondary": ("soft", "secondary_hover", "secondary_pressed", "primary"),
        "ghost": (None, "ghost_hover", "ghost_pressed", "muted"),
        "danger": ("danger", "danger_hover", "danger_pressed", "on_danger"),
    }

    def __init__(self, parent, text="", command=None, variant="primary",
                 compact=False, **kwargs):
        if variant not in self._PALETTES:
            raise ValueError(f"Unknown button variant: {variant}")
        self.variant = variant
        self._hovered = False
        self._pointer_down = False
        self._keyboard_down = None
        self._palette_override = None
        self._parent_bg = parent.cget("bg")
        options = {
            "text": text, "command": command, "relief": "flat",
            "borderwidth": 0, "highlightthickness": 2,
            "highlightbackground": self._parent_bg,
            "highlightcolor": colors_for(parent)["primary"],
            "padx": 13 if compact else 20,
            "pady": 7 if compact else 11,
            "font": ("Segoe UI", 10 if compact else 11, "bold"),
            "cursor": "hand2", "takefocus": True,
        }
        options.update(kwargs)
        super().__init__(parent, **options)
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<ButtonPress-1>", self._mouse_press)
        self.bind("<ButtonRelease-1>", self._mouse_release)
        self.bind("<KeyPress-Return>", self._key_press)
        self.bind("<KeyRelease-Return>", self._key_release)
        self.bind("<KeyPress-KP_Enter>", self._key_press)
        self.bind("<KeyRelease-KP_Enter>", self._key_release)
        self.bind("<KeyPress-space>", self._key_press)
        self.bind("<KeyRelease-space>", self._key_release)
        self.bind("<Escape>", self._cancel_press)
        self.bind("<FocusOut>", self._cancel_press)
        self._render()

    def configure(self, cnf=None, **kwargs):
        # Preserve Tk's querying API, including button.config("state").
        if cnf is not None and not isinstance(cnf, dict):
            return super().configure(cnf, **kwargs)
        updates = dict(cnf or {})
        updates.update(kwargs)
        if not updates:
            return super().configure()
        variant = updates.pop("variant", None)
        if variant is not None:
            if variant not in self._PALETTES:
                raise ValueError(f"Unknown button variant: {variant}")
            self.variant = variant
        result = super().configure(**updates) if updates else None
        if variant is not None or "state" in updates:
            if self.cget("state") == tk.DISABLED:
                self._pointer_down = False
                self._keyboard_down = None
            self._render()
        return result

    config = configure

    def set_palette(self, background, foreground="white", hover=None, pressed=None):
        """Keep semantic colors, such as Wordle feedback, across interactions.

        Feedback remains the same color on hover or press unless explicit
        alternatives are supplied. Disabled controls retain their neutral style
        and restore the semantic palette when they are enabled again.
        """
        palette = (background, hover or background, pressed or background, foreground)
        for color in palette:
            self.winfo_rgb(color)
        self._palette_override = palette
        self._render()

    def reset_palette(self):
        """Return to the current variant's standard interaction colors."""
        self._palette_override = None
        self._render()

    def apply_theme(self):
        """Refresh colors while keeping the current interaction and game state."""
        self._parent_bg = self.master.cget("bg")
        tk.Button.configure(
            self, highlightbackground=self._parent_bg,
            highlightcolor=colors_for(self)["primary"],
        )
        self._render()

    def _render(self):
        colors = colors_for(self)
        palette = self._palette_override or tuple(
            colors[role] if role else None for role in self._PALETTES[self.variant]
        )
        base, hover, pressed, foreground = palette
        background = base or self._parent_bg
        disabled = self.cget("state") == tk.DISABLED
        if disabled:
            background, foreground = colors["disabled_bg"], colors["disabled_fg"]
        elif self._keyboard_down or (self._pointer_down and self._hovered):
            background = pressed
        elif self._hovered:
            background = hover
        tk.Button.configure(
            self, bg=background, fg=foreground,
            activebackground=background, activeforeground=foreground,
            disabledforeground=colors["disabled_fg"], cursor="arrow" if disabled else "hand2",
        )

    def _enter(self, _event):
        self._hovered = True
        self._render()

    def _leave(self, _event):
        self._hovered = False
        self._render()

    def _mouse_press(self, _event):
        if self.cget("state") != tk.DISABLED:
            self.focus_set()
            self._hovered = True
            self._pointer_down = True
            self._render()
        return "break"

    def _mouse_release(self, event):
        invoke = self._pointer_down and self.cget("state") != tk.DISABLED
        invoke = invoke and 0 <= event.x < self.winfo_width() and 0 <= event.y < self.winfo_height()
        self._pointer_down = False
        self._render()
        if invoke:
            self.invoke()
        return "break"

    def _key_press(self, event):
        if self.cget("state") != tk.DISABLED and self._keyboard_down is None:
            self._keyboard_down = event.keysym
            self._render()
            # Return activates immediately; Space follows native release behavior.
            if event.keysym != "space":
                self.invoke()
        return "break"

    def _key_release(self, event):
        invoke = self._keyboard_down == "space" and event.keysym == "space"
        self._keyboard_down = None
        self._render()
        if invoke and self.cget("state") != tk.DISABLED:
            self.invoke()
        return "break"

    def _cancel_press(self, _event):
        self._keyboard_down = None
        self._pointer_down = False
        self._render()


class ScrollPage(tk.Frame):
    """A centered, width-limited page with scrolling when content needs it.

    The owning application routes mouse-wheel and focus events to ``scroll``
    and ``scroll_to_widget``. No global bindings survive page destruction.
    """

    def __init__(self, parent, max_width=1000, padding=28, **kwargs):
        kwargs.setdefault("bg", colors_for(parent)["bg"])
        super().__init__(parent, **kwargs)
        self.max_width = max_width
        self._layout_after = None
        self._scrollbar_visible = False
        self._content_height = 1
        self.canvas = tk.Canvas(
            self, bg=self.cget("bg"), bd=0, highlightthickness=0,
            yscrollincrement=24, takefocus=False,
        )
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview,
            style="Vertical.TScrollbar", takefocus=False,
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.body = tk.Frame(
            self.canvas, bg=self.cget("bg"), padx=padding, pady=padding,
        )
        self._window = self.canvas.create_window(0, 0, anchor="nw", window=self.body)
        self.body.bind("<Configure>", self._schedule_layout)
        self.canvas.bind("<Configure>", self._schedule_layout)
        self.bind("<Destroy>", self._destroy_page, add="+")

    def _schedule_layout(self, _event=None):
        if self._layout_after is None:
            self._layout_after = self.after_idle(self._layout)

    def _layout(self):
        self._layout_after = None
        if not self.winfo_exists():
            return
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        body_width = min(self.max_width, width)
        self.canvas.itemconfigure(self._window, width=body_width)
        self.canvas.coords(self._window, max(0, (width - body_width) // 2), 0)
        self._content_height = self.body.winfo_reqheight()
        overflow = self._content_height > height + 1
        if overflow != self._scrollbar_visible:
            self._scrollbar_visible = overflow
            if overflow:
                self.scrollbar.pack(side="right", fill="y", before=self.canvas)
            else:
                self.scrollbar.pack_forget()
                self.canvas.yview_moveto(0)
        self.canvas.configure(scrollregion=(0, 0, width, max(height, self._content_height)))

    def _destroy_page(self, event):
        if event.widget is self and self._layout_after is not None:
            self.after_cancel(self._layout_after)
            self._layout_after = None

    def scroll(self, units):
        """Scroll by line units and consume a wheel event only when scrollable."""
        if self._content_height > self.canvas.winfo_height() + 1:
            self.canvas.yview_scroll(int(units), "units")
            return "break"
        return None

    def reset_scroll(self):
        self.canvas.yview_moveto(0)

    def scroll_to_widget(self, widget):
        """Reveal a descendant reached with Tab without disturbing other pages."""
        ancestor = widget
        while ancestor is not None and ancestor is not self.body:
            ancestor = getattr(ancestor, "master", None)
        if ancestor is None or not widget.winfo_exists():
            return
        self.update_idletasks()
        if self._content_height <= self.canvas.winfo_height() + 1:
            return
        top = widget.winfo_rooty() - self.body.winfo_rooty()
        bottom = top + widget.winfo_height()
        visible_top = self.canvas.canvasy(0)
        visible_height = self.canvas.winfo_height()
        margin = 12
        target = None
        if top < visible_top + margin:
            target = top - margin
        elif bottom > visible_top + visible_height - margin:
            target = bottom + margin - visible_height
        if target is not None:
            self.canvas.yview_moveto(max(0, target) / self._content_height)
