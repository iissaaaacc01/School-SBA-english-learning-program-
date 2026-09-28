"""English Learner: desktop UI, account actions, and gameplay coordination.

Run python main.py. Layouts and UI components are separate from game rules
and SQLite storage so each part is easy to follow and extend.
"""
import argparse
from pathlib import Path
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from game_logic import GameSession
from screens import AppScreens, MODES, TILE_COLORS
from storage import Database
from ui_components import COLORS, THEMES, apply_theme, configure_styles

BG, INK, MUTED = COLORS["bg"], COLORS["ink"], COLORS["muted"]
BLUE, GREEN, RED = COLORS["primary"], COLORS["success"], COLORS["danger"]


class EnglishLearningApp(AppScreens):
    """Connect the interface to persistent accounts and independent game runs."""

    def __init__(self, root, database=None):
        self.root = root
        self.db = database if database is not None else Database()
        self.theme_name = self.db.get_theme()
        self.colors = THEMES[self.theme_name]
        root._theme_colors = self.colors
        self._feedback_status = "info"
        self.active_user = None
        self.session = None
        self.best_score = self.starting_best = 0
        self.frames = []
        self.current_frame = None
        self.auth_mode = tk.StringVar(root, value="login")
        self.leaderboard_mode = tk.StringVar(root, value="easy")
        self.guess_var = tk.StringVar(root)
        self._game_is_wide = None
        self._closing = False
        root.title("English Learner")
        root.configure(bg=self.colors["bg"])
        width = min(1080, root.winfo_screenwidth() - 60)
        height = min(850, root.winfo_screenheight() - 90)
        root.geometry(f"{width}x{height}")
        root.minsize(760, 640)
        root.protocol("WM_DELETE_WINDOW", self.close)
        configure_styles(root)
        self._set_window_icon()
        self.setup_shell()
        self.setup_login_screen()
        self.setup_menu_screen()
        self.setup_mode_screen()
        self.setup_game_screen()
        self.setup_end_screen()
        self.setup_leaderboard_screen()
        self.setup_edit_profile_screen()
        self.guess_var.trace_add("write", self._on_guess_changed)
        root.bind("<Return>", self._on_enter)
        root.bind("<KP_Enter>", self._on_enter)
        root.bind("<MouseWheel>", self._on_mousewheel)
        root.bind("<Button-4>", lambda event: self._on_mousewheel(event, -3))
        root.bind("<Button-5>", lambda event: self._on_mousewheel(event, 3))
        root.bind("<FocusIn>", self._on_focus)
        root.bind("<Control-a>", self._select_all)
        self.show_screen(self.frame_login)
        self.entry_username.focus_set()

    def _set_window_icon(self):
        self.icon_image = tk.PhotoImage(master=self.root, width=32, height=32)
        self.icon_image.put(self.colors["navy"], to=(0, 0, 32, 32))
        self.icon_image.put(self.colors["primary"], to=(3, 3, 29, 29))
        for rectangle in ((9, 8, 13, 25), (13, 8, 23, 11), (13, 15, 21, 18), (13, 22, 23, 25)):
            self.icon_image.put("white", to=rectangle)
        self.root.iconphoto(True, self.icon_image)

    def show_screen(self, frame):
        for other in self.frames:
            other.pack_forget()
        self.current_frame = frame
        if self.active_user is not None and frame is not self.frame_game:
            self.navigation.pack(side="left")
        else:
            self.navigation.pack_forget()
        selected = {self.frame_menu: "dashboard", self.frame_modes: "play",
                    self.frame_leaderboard: "leaderboard", self.frame_edit_profile: "profile",
                    self.frame_end: "play"}.get(frame)
        for route, button in self.nav_buttons.items():
            button.config(variant="secondary" if route == selected else "ghost")
        frame.pack(fill="both", expand=True)
        frame.reset_scroll()
        focus = {self.frame_login: self.entry_username, self.frame_menu: self.btn_play,
                 self.frame_modes: self.mode_buttons["easy"],
                 self.frame_game: self.entry_guess, self.frame_end: self.btn_replay,
                 self.frame_edit_profile: self.entry_new_username,
                 self.frame_leaderboard: self.leaderboard_buttons[self.leaderboard_mode.get()]}.get(frame)
        (focus or self.nav_buttons["play"]).focus_set()

    def _navigate(self, route):
        routes = {"dashboard": self.show_menu, "play": self.show_mode_selection,
                  "leaderboard": self.show_leaderboard, "profile": self.show_edit_profile,
                  "logout": self.logout}
        if route not in routes or self.active_user is None or not self._persist_score():
            return
        routes[route]()
        if self.current_frame is not self.frame_game and self.current_frame is not self.frame_end:
            self.session = None

    def toggle_theme(self):
        """Recolor existing widgets without restarting a run or clearing inputs."""
        next_theme = "dark" if self.theme_name == "light" else "light"
        try:
            self.db.set_theme(next_theme)
        except (ValueError, sqlite3.Error) as error:
            self._error(error)
            return
        page = self.current_frame
        scroll_position = page.canvas.yview()[0] if page is not None else 0
        apply_theme(self.root, next_theme)
        self.theme_name = next_theme
        self.colors = THEMES[next_theme]
        self.btn_theme.config(text="Light mode" if next_theme == "dark" else "Dark mode")
        self.score_tree.tag_configure("odd", background=self.colors["tile_empty"])
        self.score_tree.tag_configure("you", background=self.colors["soft"], foreground=self.colors["primary"])
        for status, swatch in self.legend_swatches.items():
            swatch.config(fg=TILE_COLORS[status])
        if self.session is not None:
            self.render_game()
        self._set_game_feedback(self.lbl_feedback.cget("text"), self._feedback_status)
        self.root.update_idletasks()
        if page is not None:
            page.canvas.yview_moveto(scroll_position)

    def _on_focus(self, event):
        if self.current_frame is not None and not self._closing:
            self.current_frame.scroll_to_widget(event.widget)

    def _on_mousewheel(self, event, units=None):
        if self.current_frame is None or isinstance(event.widget, (ttk.Treeview, ttk.Scrollbar)):
            return
        ancestor = event.widget
        while ancestor is not None and ancestor is not self.current_frame:
            ancestor = getattr(ancestor, "master", None)
        if ancestor is None:
            return
        if units is None:
            if not event.delta:
                return
            units = -int(event.delta / 120) * 3 if abs(event.delta) >= 120 else (-1 if event.delta > 0 else 1)
        return self.current_frame.scroll(units)

    @staticmethod
    def _select_all(event):
        if isinstance(event.widget, tk.Entry):
            event.widget.selection_range(0, tk.END)
            event.widget.icursor(tk.END)
            return "break"

    def _on_enter(self, event):
        if not isinstance(event.widget, tk.Entry):
            return
        if self.current_frame is self.frame_login:
            self.submit_auth()
        elif self.current_frame is self.frame_game:
            self.check_guess()
        elif self.current_frame is self.frame_edit_profile:
            self.save_profile()
        return "break"

    def toggle_password(self, entry, button):
        visible = bool(entry.cget("show"))
        entry.config(show="" if visible else "*")
        button.config(text="Hide" if visible else "Show")
        entry.focus_set()

    def _hide_passwords(self):
        for entry, button in ((self.entry_password, self.btn_show_password),
                              (self.entry_new_password, self.btn_show_new_password)):
            entry.config(show="*")
            button.config(text="Show")

    def set_auth_mode(self, mode):
        if mode not in ("login", "register"):
            return
        self.auth_mode.set(mode)
        registering = mode == "register"
        self.btn_auth.config(text="Create account" if registering else "Log in")
        self._form_message(self.auth_feedback, "")
        for key, button in self.auth_tabs.items():
            button.config(variant="primary" if key == mode else "secondary")
        self.entry_password.delete(0, tk.END)
        self._hide_passwords()
        self.entry_username.focus_set()

    def submit_auth(self):
        if self.auth_mode.get() == "register":
            self.register()
        else:
            self.login()

    def _form_message(self, target, text, error=False):
        target.config(text=text, fg=self.colors["danger"] if error else self.colors["success"])
        if text:
            before = {self.auth_feedback: self.btn_auth,
                      self.profile_feedback: self.profile_actions,
                      self.notice: self.btn_play}[target]
            target.pack(anchor="w", fill="x", pady=(10, 8), before=before)
        else:
            target.pack_forget()

    def _error(self, error):
        messagebox.showerror("Unable to complete action", str(error), parent=self.root)

    def login(self):
        username, password = self.entry_username.get().strip(), self.entry_password.get()
        if not username or not password:
            self._form_message(self.auth_feedback, "Enter your username and password to continue.", error=True)
            (self.entry_username if not username else self.entry_password).focus_set()
            return
        try:
            user = self.db.authenticate(username, password)
        except (ValueError, sqlite3.Error) as error:
            self._form_message(self.auth_feedback, str(error), error=True)
            return
        if user is None:
            self._form_message(self.auth_feedback, "That username and password do not match. Please try again.", error=True)
            self.entry_password.focus_set()
            self.entry_password.selection_range(0, tk.END)
            return
        self.active_user = user
        self.entry_password.delete(0, tk.END)
        self._hide_passwords()
        self._form_message(self.notice, "")
        self.show_menu()

    def register(self):
        try:
            self.db.create_user(self.entry_username.get().strip(), self.entry_password.get())
        except (ValueError, sqlite3.Error) as error:
            self._form_message(self.auth_feedback, str(error), error=True)
            return
        self.set_auth_mode("login")
        self._form_message(self.auth_feedback, "Account created. Enter your password to log in.")
        self.entry_password.focus_set()

    def _persist_score(self):
        if self.session is None or self.active_user is None:
            return True
        try:
            self.best_score = self.db.record_score(self.active_user["id"], self.session.mode, self.session.score)
            return True
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror("Score could not be saved",
                                 f"Your run is still open. Please retry before leaving.\n\n{error}", parent=self.root)
            return False

    def show_menu(self):
        if self.active_user is None or not self._persist_score():
            return
        try:
            scores = self.db.get_high_scores(self.active_user["id"])
        except sqlite3.Error as error:
            self._error(error)
            return
        self.session = None
        self.lbl_welcome.config(text="Dashboard")
        for mode, value_label in self.best_value_labels.items():
            value_label.config(text=str(scores.get(mode, 0)))
        self.show_screen(self.frame_menu)

    def logout(self):
        if not self._persist_score():
            return
        self.active_user = None
        self.session = None
        for entry in (self.entry_username, self.entry_password, self.entry_new_username,
                      self.entry_new_password, self.entry_guess):
            entry.delete(0, tk.END)
        self._hide_passwords()
        self.set_auth_mode("login")
        self.show_screen(self.frame_login)

    def show_mode_selection(self):
        if self.active_user is not None and self._persist_score():
            self.session = None
            self.show_screen(self.frame_modes)

    def start_game(self, mode="easy"):
        if self.active_user is None or not self._persist_score():
            return
        try:
            session = GameSession(mode, self.db.get_questions(mode),
                                  allowed_words=self.db.get_allowed_words() if mode == "medium" else None)
            best_score = self.db.record_score(self.active_user["id"], mode, 0)
        except (ValueError, sqlite3.Error) as error:
            self._error(error)
            return
        self.session = session
        self.best_score = self.starting_best = best_score
        difficulty, name, rules = MODES[mode]
        self.lbl_game_title.config(text=f"{name}  /  {difficulty}")
        self.lbl_rules.config(text=rules)
        self.btn_submit.config(text="Check word" if mode == "medium" else "Check answer")
        self._set_game_feedback("")
        self.guess_var.set("")
        self.render_game()
        self.show_screen(self.frame_game)

    def _layout_game(self, event):
        wide = event.width >= 820 and self.session is not None and self.session.mode == "medium"
        if wide == self._game_is_wide:
            return
        self._game_is_wide = wide
        self.puzzle_area.grid_forget()
        self.answer_area.grid_forget()
        self.game_card.columnconfigure(0, weight=1)
        self.game_card.columnconfigure(1, weight=1 if wide else 0)
        self.puzzle_area.grid(row=0, column=0, sticky="nsew",
                              padx=(0, 25) if wide else 0, pady=0 if wide else (0, 25))
        self.answer_area.grid(row=0 if wide else 1, column=1 if wide else 0, sticky="nsew")

    def _set_game_feedback(self, text, status="info"):
        self._feedback_status = status
        foreground, background = {
            "info": (self.colors["primary"], self.colors["soft"]),
            "correct": (self.colors["success"], self.colors["success_bg"]),
            "incorrect": (self.colors["danger"], self.colors["danger_bg"]),
            "invalid": (self.colors["danger"], self.colors["danger_bg"]),
        }.get(status, (self.colors["muted"], self.colors["bg"]))
        self.feedback_box.config(bg=background)
        self.lbl_feedback.config(text=text, fg=foreground, bg=background)
        if text:
            self.feedback_box.pack(fill="x", pady=(18, 0))
        else:
            self.feedback_box.pack_forget()

    def _on_guess_changed(self, *_args):
        can_submit = bool(self.guess_var.get().strip()) and self.session is not None and not self.session.finished
        self.btn_submit.config(state="normal" if can_submit else "disabled")
        self._render_pending_guess()

    def _render_pending_guess(self):
        if self.session is None or self.session.mode != "medium" or self.session.finished:
            return
        row = len(self.session.history)
        if row >= 5:
            return
        pending = self.guess_var.get().strip().upper()[:5]
        for index, tile in enumerate(self.wordle_tiles[row]):
            tile.config(text=pending[index] if index < len(pending) else "", bg=self.colors["tile_empty"], fg=self.colors["ink"],
                        highlightbackground=self.colors["primary"] if index < len(pending) else self.colors["border"])

    def type_letter(self, letter):
        if (self.current_frame is not self.frame_game or self.session is None
                or self.session.mode != "medium" or self.session.finished):
            return
        if self.entry_guess.selection_present():
            position = self.entry_guess.index(tk.SEL_FIRST)
            self.entry_guess.delete(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            position = self.entry_guess.index(tk.INSERT)
        if len(self.entry_guess.get()) < 5:
            self.entry_guess.insert(position, letter.upper())
            self.entry_guess.icursor(position + 1)
        self.entry_guess.focus_set()

    def backspace_guess(self):
        if self.current_frame is not self.frame_game or self.session is None or self.session.finished:
            return
        if self.entry_guess.selection_present():
            self.entry_guess.delete(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            position = self.entry_guess.index(tk.INSERT)
            if position:
                self.entry_guess.delete(position - 1, position)
        self.entry_guess.focus_set()

    def render_game(self):
        session = self.session
        if session is None:
            return
        self.game_stat_labels["score"].config(text=str(session.score))
        self.game_stat_labels["best"].config(text=str(max(self.best_score, session.score)))
        limit = 5 if session.mode == "medium" else 3
        self.game_stat_labels["remaining"].config(
            text=f"{session.remaining_attempts} / {limit}",
            fg=self.colors["danger"] if session.remaining_attempts == 1 else self.colors["ink"])
        self._game_is_wide = None
        self._layout_game(type("Layout", (), {"width": self.game_card.winfo_width()})())
        if session.mode == "medium":
            self.lbl_question.pack_forget()
            self.wordle_panel.pack()
            priorities = {"absent": 0, "present": 1, "correct": 2}
            key_statuses = {}
            for row, cells in enumerate(self.wordle_tiles):
                for column, tile in enumerate(cells):
                    if row < len(session.history):
                        guess, statuses = session.history[row]
                        status = statuses[column]
                        tile.config(text=guess[column].upper(), bg=TILE_COLORS[status], fg="white",
                                    highlightbackground=TILE_COLORS[status])
                        letter = guess[column]
                        if letter not in key_statuses or priorities[status] > priorities[key_statuses[letter]]:
                            key_statuses[letter] = status
                    else:
                        tile.config(text="", bg=self.colors["tile_empty"], fg=self.colors["ink"], highlightbackground=self.colors["border"])
            for letter, key in self.keyboard.items():
                if letter in key_statuses:
                    key.set_palette(TILE_COLORS[key_statuses[letter]])
                else:
                    key.reset_palette()
            self._render_pending_guess()
        else:
            self.wordle_panel.pack_forget()
            question = "  ".join(session.prompt) if session.mode == "easy" else session.prompt
            self.lbl_question.config(text=question, font=("Segoe UI", 27 if session.mode == "easy" else 22, "bold"))
            self.lbl_question.pack(fill="x", pady=(12, 22))

    def check_guess(self):
        if self.current_frame is not self.frame_game or self.session is None or self.session.finished:
            return
        guess = self.entry_guess.get()
        result = self.session.submit(guess)
        status = result["status"]
        if status == "invalid":
            self._set_game_feedback(result["message"], "invalid")
            self.entry_guess.focus_set()
            return
        self.guess_var.set("")
        saved = self._persist_score() if status in ("correct", "finished") else True
        feedback = result["message"]
        if status == "correct":
            feedback = f"Correct: {guess.strip().upper()}  +1"
        elif self.session.mode == "medium" and result.get("feedback"):
            descriptions = {"correct": "right place", "present": "elsewhere", "absent": "absent"}
            feedback += "\n" + " · ".join(
                f"{letter.upper()}: {descriptions[mark]}" for letter, mark in zip(guess.strip(), result["feedback"]))
        self._set_game_feedback(feedback, status)
        self.render_game()
        if status == "finished":
            self.show_end_screen(result["message"], saved=saved)
        else:
            self.entry_guess.focus_set()

    def show_end_screen(self, reason, saved=True):
        session = self.session
        difficulty, name, _ = MODES[session.mode]
        personal_best = session.score > self.starting_best and saved
        self.end_title.config(text="New best score" if personal_best else "Game over")
        self.lbl_end_mode.config(text=f"{difficulty.upper()}  /  {name}", fg=self.colors["mode_" + session.mode])
        self.lbl_final_score.config(text=str(session.score))
        save_note = f"Personal best: {self.best_score} points" if saved else "Score not saved yet. Choose an action below to retry."
        self.lbl_end_details.config(text=f"{reason}\nThe answer was {session.answer.upper()}.\n{save_note}")
        self.show_screen(self.frame_end)

    def finish_to_menu(self):
        self.show_menu()

    def play_again(self):
        if self.session is not None:
            self.start_game(self.session.mode)

    def show_current_leaderboard(self):
        if self.session is not None:
            self.leaderboard_mode.set(self.session.mode)
        self.show_leaderboard()

    def select_leaderboard(self, mode):
        self.leaderboard_mode.set(mode)
        self.refresh_leaderboard()

    def show_leaderboard(self):
        if self.active_user is not None and self._persist_score() and self.refresh_leaderboard():
            self.show_screen(self.frame_leaderboard)

    def refresh_leaderboard(self):
        mode = self.leaderboard_mode.get()
        try:
            rows = self.db.leaderboard(mode)
        except (ValueError, sqlite3.Error) as error:
            self._error(error)
            return False
        self.lbl_board_title.config(text=MODES[mode][1])
        for key, button in self.leaderboard_buttons.items():
            button.config(variant="primary" if key == mode else "secondary")
        for item in self.score_tree.get_children():
            self.score_tree.delete(item)
        your_row = None
        for index, row in enumerate(rows):
            is_you = self.active_user is not None and row["username"] == self.active_user["username"]
            tags = ("you",) if is_you else (("odd",) if index % 2 else ())
            self.score_tree.insert("", "end", values=(f"#{row['rank']}",
                                   row["username"] + ("  (you)" if is_you else ""), row["score"]), tags=tags)
            if is_you:
                your_row = row
        self.lbl_board_personal.config(
            text=f"Your rank: #{your_row['rank']}   ·   Your best: {your_row['score']} points" if your_row
            else "No personal score yet.")
        self.lbl_board_note.config(
            text=f"{len(rows)} {'player' if len(rows) == 1 else 'players'}  ·  Ties share a rank"
            if rows else "No scores yet.")
        return True

    def show_edit_profile(self):
        if self.active_user is None or not self._persist_score():
            return
        self.session = None
        self.entry_new_username.delete(0, tk.END)
        self.entry_new_username.insert(0, self.active_user["username"])
        self.entry_new_password.delete(0, tk.END)
        self._form_message(self.profile_feedback, "")
        self._hide_passwords()
        self.show_screen(self.frame_edit_profile)

    def save_profile(self):
        if self.active_user is None:
            return
        try:
            self.active_user = self.db.update_user(
                self.active_user["id"], self.entry_new_username.get().strip(),
                self.entry_new_password.get() or None)
        except (ValueError, sqlite3.Error) as error:
            self._form_message(self.profile_feedback, str(error), error=True)
            return
        self.entry_new_password.delete(0, tk.END)
        self._hide_passwords()
        self._form_message(self.notice, "Profile saved.")
        self.show_menu()

    def delete_account(self):
        if self.active_user is None:
            return
        if not messagebox.askyesno(
                "Delete account?", "Permanently delete your account and all three leaderboard scores? This cannot be undone.",
                icon="warning", default="no", parent=self.root):
            return
        try:
            self.db.delete_user(self.active_user["id"])
        except sqlite3.Error as error:
            self._error(error)
            return
        self.session = None
        self.logout()
        self._form_message(self.auth_feedback, "Your account and scores have been deleted.")

    def close(self):
        if not self._persist_score():
            return
        self._closing = True
        self.db.close()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description="Play three English word games with SQLite leaderboards.")
    parser.add_argument("--database", type=Path, help="Use a different SQLite database (default: beside main.py).")
    args = parser.parse_args()
    root = tk.Tk()
    try:
        database = Database(args.database) if args.database else Database()
    except (OSError, ValueError, sqlite3.Error) as error:
        root.withdraw()
        messagebox.showerror("Database could not be opened", str(error), parent=root)
        root.destroy()
        return
    EnglishLearningApp(root, database)
    report = database.migration_report
    if any(report[key] for key in ("users_imported", "questions_imported", "questions_archived",
                                  "users_skipped", "questions_skipped")) or report["warnings"]:
        details = (f"Imported {report['users_imported']} accounts and {report['questions_imported']} questions.\n"
                   f"Preserved {report['legacy_scores_imported']} old cumulative scores separately from the new leaderboards.\n"
                   f"Archived {report['questions_archived']} questions that need a fill-in-the-blank rewrite.\n\n"
                   "Original text files have been left unchanged. Each file is imported once.")
        if report["warnings"]:
            details += "\n\n" + "\n".join(report["warnings"][:6])
            if len(report["warnings"]) > 6:
                details += f"\n...and {len(report['warnings']) - 6} more import notices."
        root.after_idle(lambda: messagebox.showinfo("Previous data imported", details, parent=root))
    root.mainloop()


if __name__ == "__main__":
    main()
