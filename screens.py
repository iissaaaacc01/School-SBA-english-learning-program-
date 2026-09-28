"""Screen layouts for English Learner, built from a small shared UI toolkit."""

import tkinter as tk
from tkinter import ttk

from ui_components import ActionButton, ScrollPage, card, label

MODES = {
    "easy": ("Easy", "Word Scramble", "Unscramble the word. Three mistakes in total end the run."),
    "medium": ("Medium", "Wordle", "Guess the five-letter word in five tries."),
    "hard": ("Hard", "Fill in the Blank", "Complete the sentence. Three consecutive mistakes end the run."),
}
TILE_COLORS = {"correct": "#147D64", "present": "#966715", "absent": "#596579"}


class AppScreens:
    """Presentation only: callbacks and account/game state belong to main.py."""

    def _page(self):
        page = ScrollPage(self.content, max_width=1000, padding=24)
        self.frames.append(page)
        return page

    def _heading(self, parent, title):
        title_label = label(parent, title, size=26, bold=True, wraplength=850, justify="left", anchor="w")
        title_label.pack(anchor="w", fill="x", pady=(0, 22))
        return title_label

    def _field(self, parent, title, *, password=False, variable=None, hint=""):
        label(parent, title, size=10, bold=True).pack(anchor="w", pady=(12, 6))
        outline = tk.Frame(parent, bg=self.colors["surface"], highlightthickness=1, highlightbackground=self.colors["border"])
        outline.pack(fill="x")
        entry = tk.Entry(outline, textvariable=variable, show="*" if password else "", bg=self.colors["surface"], fg=self.colors["ink"],
                         font=("Segoe UI", 12), relief="flat", bd=0, insertbackground=self.colors["primary"],
                         selectbackground=self.colors["primary"], selectforeground=self.colors["on_primary"])
        entry.pack(side="left", fill="x", expand=True, padx=12, ipady=11)
        entry.bind("<FocusIn>", lambda event: outline.config(highlightbackground=self.colors["primary"]))
        entry.bind("<FocusOut>", lambda event: outline.config(highlightbackground=self.colors["border"]))
        reveal = None
        if password:
            reveal = ActionButton(outline, text="Show", variant="ghost", compact=True,
                                  command=lambda: self.toggle_password(entry, reveal))
            reveal.pack(side="right", padx=4, pady=3)
        if hint:
            label(parent, hint, size=9, color=self.colors["muted"], wraplength=600, justify="left").pack(anchor="w", fill="x", pady=(5, 0))
        return entry, reveal

    def setup_shell(self):
        self.topbar = tk.Frame(self.root, bg=self.colors["bg"], padx=16, pady=8)
        self.topbar.pack(fill="x")
        self.btn_theme = ActionButton(
            self.topbar, text="Dark mode" if self.theme_name == "light" else "Light mode",
            variant="secondary", compact=True, command=self.toggle_theme)
        self.btn_theme.pack(side="right")
        self.navigation = tk.Frame(self.topbar, bg=self.colors["bg"])
        self.nav_buttons = {}
        for route, text in (("dashboard", "Dashboard"), ("play", "Play"),
                            ("leaderboard", "Leaderboards"), ("profile", "Profile")):
            button = ActionButton(self.navigation, text=text, variant="ghost", compact=True,
                                  command=lambda r=route: self._navigate(r))
            button.pack(side="left", padx=2)
            self.nav_buttons[route] = button
        ActionButton(self.navigation, text="Log out", variant="ghost", compact=True,
                     command=lambda: self._navigate("logout")).pack(side="left", padx=2)
        self.content = tk.Frame(self.root, bg=self.colors["bg"])
        self.content.pack(fill="both", expand=True)

    def setup_login_screen(self):
        self.frame_login = self._page()
        self.frame_login.max_width = 640
        body = self.frame_login.body
        self._heading(body, "English Learner")
        form = card(body, padding=24)
        form.pack(fill="x")
        tabs = tk.Frame(form, bg=self.colors["surface"])
        tabs.pack(fill="x", pady=(0, 12))
        self.auth_tabs = {}
        for mode, text in (("login", "Log in"), ("register", "Create account")):
            button = ActionButton(tabs, text=text, variant="primary" if mode == "login" else "secondary",
                                  command=lambda m=mode: self.set_auth_mode(m))
            button.pack(side="left", fill="x", expand=True, padx=(0, 8) if mode == "login" else 0)
            self.auth_tabs[mode] = button
        self.entry_username, _ = self._field(form, "Username")
        self.entry_password, self.btn_show_password = self._field(form, "Password", password=True)
        self.auth_feedback = label(form, "", color=self.colors["muted"], wraplength=780, justify="left")
        self.btn_auth = ActionButton(form, text="Log in", command=self.submit_auth)
        self.btn_auth.pack(fill="x", pady=(20, 0))

    def setup_menu_screen(self):
        self.frame_menu = self._page()
        body = self.frame_menu.body
        self.lbl_welcome = self._heading(body, "Dashboard")
        self.notice = label(body, "", color=self.colors["success"], wraplength=850, justify="left")
        self.btn_play = ActionButton(body, text="Play a Game", command=self.show_mode_selection)
        self.btn_play.pack(anchor="w", pady=(0, 28))
        label(body, "Best scores", size=15, bold=True).pack(anchor="w", pady=(0, 12))
        row = tk.Frame(body, bg=self.colors["bg"])
        row.pack(fill="x")
        self.best_value_labels = {}
        for column, (mode, (difficulty, name, _)) in enumerate(MODES.items()):
            row.columnconfigure(column, weight=1, uniform="scores")
            box = card(row, padding=18)
            box.grid(row=0, column=column, sticky="nsew", padx=(0, 12) if column < 2 else 0)
            label(box, difficulty, size=10, color=self.colors["mode_" + mode]).pack(anchor="w")
            label(box, name, size=12, bold=True, wraplength=260, justify="left", anchor="w").pack(anchor="w", fill="x", pady=(5, 14))
            self.best_value_labels[mode] = label(box, "0", size=34, bold=True)
            self.best_value_labels[mode].pack(anchor="w")

    def setup_mode_screen(self):
        self.frame_modes = self._page()
        body = self.frame_modes.body
        self._heading(body, "Choose a game")
        self.mode_buttons = {}
        for mode, (difficulty, name, rules) in MODES.items():
            box = card(body, padding=20)
            box.pack(fill="x", pady=(0, 14))
            top = tk.Frame(box, bg=self.colors["surface"])
            top.pack(fill="x")
            button = ActionButton(top, text=f"Play {difficulty}", command=lambda m=mode: self.start_game(m))
            button.pack(side="right", padx=(14, 0))
            self.mode_buttons[mode] = button
            info = tk.Frame(top, bg=self.colors["surface"])
            info.pack(side="left", fill="x", expand=True)
            label(info, difficulty, size=10, bold=True, color=self.colors["mode_" + mode]).pack(anchor="w")
            label(info, name, size=19, bold=True, wraplength=500, justify="left").pack(anchor="w", fill="x", pady=(3, 0))
            label(box, rules, color=self.colors["muted"], wraplength=850, justify="left").pack(anchor="w", fill="x", pady=(12, 0))

    def setup_game_screen(self):
        self.frame_game = self._page()
        body = self.frame_game.body
        top = tk.Frame(body, bg=self.colors["bg"])
        top.pack(fill="x", pady=(0, 14))
        ActionButton(top, text="End run", variant="secondary", compact=True, command=self.finish_to_menu).pack(side="right")
        self.lbl_game_title = label(top, "", size=23, bold=True, wraplength=650, justify="left")
        self.lbl_game_title.pack(side="left", fill="x", expand=True)
        stats = card(body, padding=14)
        stats.pack(fill="x", pady=(0, 16))
        self.game_stat_labels = {}
        for index, (key, caption) in enumerate((("score", "Score"), ("best", "Best"), ("remaining", "Tries left"))):
            stats.columnconfigure(index, weight=1, uniform="game-stats")
            box = tk.Frame(stats, bg=self.colors["surface"])
            box.grid(row=0, column=index, sticky="nsew", padx=8)
            label(box, caption, size=10, bold=True, color=self.colors["muted"]).pack(anchor="w")
            value = label(box, "0", size=23, bold=True, color=self.colors["primary"] if key == "score" else self.colors["ink"])
            value.pack(anchor="w", pady=(4, 0))
            self.game_stat_labels[key] = value
        self.game_card = card(body, padding=20)
        self.game_card.pack(fill="x")
        self.puzzle_area = tk.Frame(self.game_card, bg=self.colors["surface"])
        self.answer_area = tk.Frame(self.game_card, bg=self.colors["surface"])
        self.game_card.bind("<Configure>", self._layout_game)
        self.lbl_question = label(self.puzzle_area, "", size=27, bold=True, wraplength=780, justify="center")
        self.wordle_panel = tk.Frame(self.puzzle_area, bg=self.colors["surface"])
        board = tk.Frame(self.wordle_panel, bg=self.colors["surface"])
        board.pack()
        self.wordle_tiles = []
        for row in range(5):
            cells = []
            for column in range(5):
                tile = tk.Label(board, text="", bg=self.colors["tile_empty"], fg=self.colors["ink"],
                                width=3, font=("Segoe UI", 17, "bold"), pady=3, relief="flat",
                                highlightthickness=1, highlightbackground=self.colors["border"])
                tile.grid(row=row, column=column, padx=3, pady=3)
                cells.append(tile)
            self.wordle_tiles.append(cells)
        legend = tk.Frame(self.wordle_panel, bg=self.colors["surface"])
        legend.pack(pady=(12, 9))
        self.legend_swatches = {}
        for status, text in (("correct", "Right place"), ("present", "Elsewhere"), ("absent", "Absent")):
            swatch = label(legend, "■", color=TILE_COLORS[status], size=12)
            swatch.pack(side="left", padx=(9, 3))
            self.legend_swatches[status] = swatch
            label(legend, text, size=10, color=self.colors["muted"]).pack(side="left")
        self.keyboard = {}
        self.keyboard_panel = tk.Frame(self.wordle_panel, bg=self.colors["surface"])
        self.keyboard_panel.pack(pady=(2, 3))
        for letters in ("qwertyuiop", "asdfghjkl", "zxcvbnm"):
            row_frame = tk.Frame(self.keyboard_panel, bg=self.colors["surface"])
            row_frame.pack(pady=2)
            for letter in letters:
                key = ActionButton(row_frame, text=letter.upper(), variant="secondary", compact=True,
                                   command=lambda key=letter: self.type_letter(key), width=2, padx=3, pady=4,
                                   font=("Segoe UI", 9, "bold"), takefocus=False)
                key.pack(side="left", padx=2)
                self.keyboard[letter] = key
        ActionButton(self.keyboard_panel, text="Delete letter", variant="ghost", compact=True,
                     command=self.backspace_guess, takefocus=False).pack(pady=(4, 0))
        self.lbl_rules = label(self.answer_area, "", color=self.colors["muted"], wraplength=750, justify="left")
        self.lbl_rules.pack(anchor="w", fill="x", pady=(0, 8))
        self.entry_guess, _ = self._field(self.answer_area, "Your answer", variable=self.guess_var)
        self.entry_guess.config(font=("Segoe UI", 16), justify="center")
        self.btn_submit = ActionButton(self.answer_area, text="Check answer", command=self.check_guess, state="disabled")
        self.btn_submit.pack(fill="x", pady=(14, 7))
        self.feedback_box = tk.Frame(self.answer_area, bg=self.colors["soft"], padx=14, pady=12)
        self.lbl_feedback = label(self.feedback_box, "", color=self.colors["primary"], wraplength=700, justify="left")
        self.lbl_feedback.pack(fill="x")

    def setup_end_screen(self):
        self.frame_end = self._page()
        self.frame_end.max_width = 820
        body = self.frame_end.body
        self.end_title = self._heading(body, "Game over")
        summary = card(body, padding=24)
        summary.pack(fill="x")
        self.lbl_end_mode = label(summary, "", size=12, bold=True, color=self.colors["primary"])
        self.lbl_end_mode.pack()
        self.lbl_final_score = label(summary, "0", size=60, bold=True)
        self.lbl_final_score.pack(pady=(6, 0))
        label(summary, "Final score", size=10, bold=True, color=self.colors["muted"]).pack()
        self.lbl_end_details = label(summary, "", color=self.colors["muted"], wraplength=800, justify="center")
        self.lbl_end_details.pack(fill="x", pady=18)
        self.btn_replay = ActionButton(summary, text="Play again", command=self.play_again)
        self.btn_replay.pack(fill="x", pady=(0, 8))
        ActionButton(summary, text="Choose another game", variant="secondary", command=self.show_mode_selection).pack(fill="x")
        ActionButton(body, text="View this leaderboard", variant="ghost", command=self.show_current_leaderboard).pack(pady=(14, 0))

    def setup_leaderboard_screen(self):
        self.frame_leaderboard = self._page()
        body = self.frame_leaderboard.body
        self._heading(body, "Leaderboards")
        tabs = tk.Frame(body, bg=self.colors["bg"])
        tabs.pack(fill="x", pady=(0, 18))
        self.leaderboard_buttons = {}
        for index, (mode, (difficulty, _, _)) in enumerate(MODES.items()):
            tabs.columnconfigure(index, weight=1, uniform="tabs")
            button = ActionButton(tabs, text=difficulty, variant="secondary", command=lambda m=mode: self.select_leaderboard(m))
            button.grid(row=0, column=index, sticky="ew", padx=(0, 8) if index < 2 else 0)
            self.leaderboard_buttons[mode] = button
        container = card(body, padding=20)
        container.pack(fill="x")
        self.lbl_board_title = label(container, "Word Scramble", size=19, bold=True)
        self.lbl_board_title.pack(anchor="w")
        self.lbl_board_personal = label(container, "", color=self.colors["muted"], wraplength=850, justify="left")
        self.lbl_board_personal.pack(anchor="w", fill="x", pady=(6, 18))
        table = tk.Frame(container, bg=self.colors["surface"])
        table.pack(fill="x")
        self.score_tree = ttk.Treeview(table, columns=("rank", "username", "score"), show="headings", selectmode="browse", height=8, takefocus=True)
        for column, heading, width, anchor in (("rank", "RANK", 80, "center"), ("username", "PLAYER", 350, "w"), ("score", "BEST SCORE", 110, "center")):
            self.score_tree.heading(column, text=heading)
            self.score_tree.column(column, width=width, minwidth=65, anchor=anchor, stretch=column == "username")
        scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.score_tree.yview)
        self.score_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.score_tree.pack(side="left", fill="x", expand=True)
        self.score_tree.tag_configure("odd", background=self.colors["tile_empty"])
        self.score_tree.tag_configure("you", background=self.colors["soft"], foreground=self.colors["primary"], font=("Segoe UI", 11, "bold"))
        self.lbl_board_note = label(container, "", color=self.colors["muted"], wraplength=850, justify="left")
        self.lbl_board_note.pack(anchor="w", fill="x", pady=(15, 0))
        ActionButton(body, text="Play a Game", command=self.show_mode_selection).pack(anchor="w", pady=(18, 0))

    def setup_edit_profile_screen(self):
        self.frame_edit_profile = self._page()
        self.frame_edit_profile.max_width = 900
        body = self.frame_edit_profile.body
        self._heading(body, "Profile")
        form = card(body, padding=24)
        form.pack(fill="x")
        self.entry_new_username, _ = self._field(form, "Username")
        self.entry_new_password, self.btn_show_new_password = self._field(form, "New password", password=True, hint="Leave blank to keep your current password.")
        self.profile_feedback = label(form, "", color=self.colors["muted"], wraplength=800, justify="left")
        buttons = tk.Frame(form, bg=self.colors["surface"])
        self.profile_actions = buttons
        buttons.pack(fill="x", pady=(20, 0))
        ActionButton(buttons, text="Save changes", command=self.save_profile).pack(side="left", padx=(0, 8))
        ActionButton(buttons, text="Cancel", variant="secondary", command=self.show_menu).pack(side="left")
        danger = card(body, padding=22, bg=self.colors["danger_bg"])
        danger.pack(fill="x", pady=(20, 0))
        label(danger, "Delete account", size=15, bold=True, color=self.colors["danger"]).pack(anchor="w")
        label(danger, "This permanently removes your account and all three leaderboard scores.", color=self.colors["muted"],
              wraplength=800, justify="left").pack(anchor="w", fill="x", pady=(7, 14))
        self.btn_delete_account = ActionButton(danger, text="Delete Account", variant="danger", command=self.delete_account)
        self.btn_delete_account.pack(anchor="w")
