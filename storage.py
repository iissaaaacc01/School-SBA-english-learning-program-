"""SQLite persistence for accounts, game content, and independent high scores."""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
import re
import secrets
import sqlite3

from seed_data import ALLOWED_WORDS, FILL_IN_BLANK_QUESTIONS, SCRAMBLE_WORDS, WORDLE_TARGETS

MODES = ("easy", "medium", "hard")
PASSWORD_ITERATIONS = 600_000
DEFAULT_DATABASE = Path(__file__).resolve().with_name("english_learning.db")


class Database:
    """Keep persistent state in one SQLite database, with safe account updates.

    Existing ``user-data.txt`` and ``questions.txt`` files beside the database
    are imported once, when present. Their originals are never rewritten.
    Use ``:memory:`` for an isolated database without automatic legacy import.
    """

    def __init__(self, path=None):
        self.path = Path(path).expanduser().resolve() if path not in (None, ":memory:") else path
        if self.path is None:
            self.path = DEFAULT_DATABASE
        self.conn = sqlite3.connect(str(self.path), timeout=10)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA busy_timeout = 10000")
        try:
            self._create_schema()
            self._seed()
            self._seed_dictionary()
            self.migration_report = self._empty_migration_report()
            if self.path != ":memory:":
                self.migration_report = self.import_legacy()
        except Exception:
            self.conn.close()
            raise

    def _create_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                password_iterations INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                mode TEXT NOT NULL CHECK (mode IN ('easy', 'medium', 'hard')),
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                UNIQUE (mode, question, answer)
            );
            CREATE TABLE IF NOT EXISTS high_scores (
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                mode TEXT NOT NULL CHECK (mode IN ('easy', 'medium', 'hard')),
                score INTEGER NOT NULL CHECK (score >= 0),
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, mode)
            );
            CREATE INDEX IF NOT EXISTS high_scores_mode_score
                ON high_scores(mode, score DESC);
            CREATE TABLE IF NOT EXISTS allowed_words (
                word TEXT PRIMARY KEY CHECK (length(word) = 5 AND word NOT GLOB '*[^a-z]*')
            );
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS legacy_scores (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                score INTEGER NOT NULL CHECK (score >= 0),
                imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS legacy_questions (
                id INTEGER PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                reason TEXT NOT NULL,
                UNIQUE (question, answer)
            );
        """)

    def _seed(self):
        with self.conn:
            # Claim initialization before inserting, making startup atomic even
            # if two application processes open a new database simultaneously.
            inserted = self.conn.execute(
                "INSERT OR IGNORE INTO metadata(key, value) VALUES ('seed_version', '1')"
            ).rowcount
            if not inserted:
                return
            questions = [("easy", "Unscramble the word.", word) for word in SCRAMBLE_WORDS]
            questions += [("medium", "Guess the five-letter word.", word) for word in WORDLE_TARGETS]
            questions += [("hard", question, answer) for question, answer in FILL_IN_BLANK_QUESTIONS]
            self.conn.executemany(
                "INSERT OR IGNORE INTO questions(mode, question, answer) VALUES (?, ?, ?)",
                questions,
            )
            self.conn.executemany("INSERT INTO allowed_words(word) VALUES (?)", ((w,) for w in sorted(ALLOWED_WORDS)))

    def _seed_dictionary(self):
        marker = "scowl_dictionary_version"
        if self.conn.execute("SELECT 1 FROM metadata WHERE key = ?", (marker,)).fetchone():
            return
        source = Path(__file__).resolve().with_name("wordle_dictionary.sql")
        if not source.is_file():
            return
        script = source.read_text(encoding="utf-8")
        with self.conn:
            if not self.conn.execute(
                "INSERT OR IGNORE INTO metadata(key, value) VALUES (?, '2026.02.25')", (marker,)
            ).rowcount:
                return
            # The bundled asset contains INSERT statements only. Execute each
            # in this transaction: executescript would commit the marker first.
            statement = ""
            for line in script.splitlines(keepends=True):
                statement += line
                if sqlite3.complete_statement(statement):
                    self.conn.execute(statement)
                    statement = ""

    @staticmethod
    def _validate_username(username):
        if not isinstance(username, str):
            raise ValueError("Please enter a username.")
        username = username.strip()
        if not username:
            raise ValueError("Please enter a username.")
        if len(username) > 32:
            raise ValueError("Your username must be 32 characters or fewer.")
        if not username.isprintable():
            raise ValueError("Your username cannot contain control characters.")
        return username

    @staticmethod
    def _validate_password(password):
        if not isinstance(password, str) or not password.strip():
            raise ValueError("Please enter a password.")
        if len(password) > 256:
            raise ValueError("Your password must be 256 characters or fewer.")
        return password

    @staticmethod
    def _password_record(password):
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), PASSWORD_ITERATIONS).hex()
        return hashed, salt, PASSWORD_ITERATIONS

    @staticmethod
    def _validate_mode(mode):
        if mode not in MODES:
            raise ValueError("Please choose easy, medium, or hard mode.")
        return mode

    def _insert_user(self, username, password):
        hashed, salt, iterations = self._password_record(password)
        cursor = self.conn.execute(
            "INSERT INTO users(username, password_hash, password_salt, password_iterations) VALUES (?, ?, ?, ?)",
            (username, hashed, salt, iterations),
        )
        return {"id": cursor.lastrowid, "username": username}

    def create_user(self, username, password):
        username = self._validate_username(username)
        password = self._validate_password(password)
        try:
            with self.conn:
                return self._insert_user(username, password)
        except sqlite3.IntegrityError as exc:
            raise ValueError("That username is already taken.") from exc

    def authenticate(self, username, password):
        if not isinstance(username, str) or not isinstance(password, str) or len(password) > 256:
            return None
        row = self.conn.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
        if row is None:
            return None
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(row["password_salt"]), row["password_iterations"]
        ).hex()
        if hmac.compare_digest(actual, row["password_hash"]):
            return {"id": row["id"], "username": row["username"]}
        return None

    def update_user(self, user_id, username, password=None):
        username = self._validate_username(username)
        if password not in (None, ""):
            self._validate_password(password)
        try:
            with self.conn:
                if password not in (None, ""):
                    hashed, salt, iterations = self._password_record(password)
                    cursor = self.conn.execute(
                        "UPDATE users SET username = ?, password_hash = ?, password_salt = ?, password_iterations = ? WHERE id = ?",
                        (username, hashed, salt, iterations, user_id),
                    )
                else:
                    cursor = self.conn.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))
                if cursor.rowcount != 1:
                    raise ValueError("This account no longer exists. Please log in again.")
        except sqlite3.IntegrityError as exc:
            raise ValueError("That username is already taken.") from exc
        return {"id": user_id, "username": username}

    def delete_user(self, user_id):
        with self.conn:
            self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    def get_high_scores(self, user_id):
        result = dict.fromkeys(MODES, 0)
        rows = self.conn.execute("SELECT mode, score FROM high_scores WHERE user_id = ?", (user_id,))
        result.update((row["mode"], row["score"]) for row in rows)
        return result

    def get_theme(self) -> str:
        """Return this installation's theme, including before anyone logs in."""
        row = self.conn.execute("SELECT value FROM metadata WHERE key = ?", ("ui_theme",)).fetchone()
        return row["value"] if row is not None and row["value"] in ("light", "dark") else "light"

    def set_theme(self, theme: str) -> None:
        """Save a supported appearance without changing accounts or scores."""
        if theme not in ("light", "dark"):
            raise ValueError("Please choose the light or dark theme.")
        with self.conn:
            self.conn.execute("""
                INSERT INTO metadata(key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, ("ui_theme", theme))

    def record_score(self, user_id, mode, score):
        self._validate_mode(mode)
        if type(score) is not int or not 0 <= score <= 2**63 - 1:
            raise ValueError("A score must be a non-negative whole number.")
        try:
            with self.conn:
                self.conn.execute("""
                    INSERT INTO high_scores(user_id, mode, score) VALUES (?, ?, ?)
                    ON CONFLICT(user_id, mode) DO UPDATE SET
                        score = MAX(high_scores.score, excluded.score),
                        updated_at = CASE WHEN excluded.score > high_scores.score
                            THEN CURRENT_TIMESTAMP ELSE high_scores.updated_at END
                """, (user_id, mode, score))
                row = self.conn.execute("SELECT score FROM high_scores WHERE user_id = ? AND mode = ?", (user_id, mode)).fetchone()
                return row["score"]
        except sqlite3.IntegrityError as exc:
            raise ValueError("This account no longer exists. Please log in again.") from exc

    def leaderboard(self, mode):
        self._validate_mode(mode)
        rows = self.conn.execute("""
            SELECT u.username, h.score FROM high_scores h
            JOIN users u ON u.id = h.user_id WHERE h.mode = ?
            ORDER BY h.score DESC, u.username COLLATE NOCASE, u.username
        """, (mode,)).fetchall()
        result, previous_score, rank = [], None, 0
        for position, row in enumerate(rows, 1):
            if row["score"] != previous_score:
                rank = position
            result.append({"rank": rank, "username": row["username"], "score": row["score"]})
            previous_score = row["score"]
        return result

    def get_questions(self, mode):
        self._validate_mode(mode)
        return [dict(row) for row in self.conn.execute(
            "SELECT id, question, answer FROM questions WHERE mode = ? ORDER BY id", (mode,)
        )]

    def get_allowed_words(self):
        return {row[0] for row in self.conn.execute(
            "SELECT word FROM allowed_words UNION SELECT answer FROM questions WHERE mode = 'medium'"
        )}

    @staticmethod
    def _empty_migration_report():
        return {
            "users_imported": 0, "users_skipped": 0, "legacy_scores_imported": 0,
            "questions_imported": 0, "questions_skipped": 0, "questions_archived": 0,
            "warnings": [],
        }

    def import_legacy(self, directory=None):
        """Import the original comma/pipe format, once per legacy file.

        Old cumulative scores are archived in ``legacy_scores`` because ten
        points per answer across all sessions cannot be compared with a new
        single-session high score. Non-fillable questions are preserved in
        ``legacy_questions``. No plaintext passwords are stored in SQLite.
        """
        if directory is None:
            directory = DEFAULT_DATABASE.parent if self.path == ":memory:" else self.path.parent
        directory = Path(directory)
        report = self._empty_migration_report()
        sources = (("user-data.txt", self._import_user_lines), ("questions.txt", self._import_question_lines))
        for filename, importer in sources:
            source = directory / filename
            marker = "legacy_import:" + filename
            if not source.is_file() or self.conn.execute("SELECT 1 FROM metadata WHERE key = ?", (marker,)).fetchone():
                continue
            try:
                # UTF-8 with BOM is accepted; preserve old Windows text files too.
                raw = source.read_bytes()
                try:
                    content = raw.decode("utf-8-sig")
                except UnicodeDecodeError:
                    content = raw.decode("cp1252")
                    report["warnings"].append(f"{filename}: imported using Windows text encoding.")
            except (OSError, UnicodeError) as exc:
                report["warnings"].append(f"Could not import {filename}: {exc}")
                continue
            with self.conn:
                # Claim before importing and commit together so concurrent
                # launches cannot replay the same input after a deletion.
                if not self.conn.execute("INSERT OR IGNORE INTO metadata(key, value) VALUES (?, ?)", (marker, str(source.resolve()))).rowcount:
                    continue
                importer(content.splitlines(), report)
        self.migration_report = report
        return report

    def _import_user_lines(self, lines, report):
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            parts = line.strip().split(",")
            try:
                if len(parts) != 3:
                    raise ValueError("expected username,password,score")
                username = self._validate_username(parts[0])
                password = self._validate_password(parts[1])
                if not parts[2].isascii() or not parts[2].isdigit():
                    raise ValueError("score must be a non-negative whole number")
                score = int(parts[2])
                if score > 2**63 - 1:
                    raise ValueError("score is too large")
                if self.conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
                    raise ValueError("duplicate username")
                user = self._insert_user(username, password)
                self.conn.execute("INSERT INTO legacy_scores(user_id, score) VALUES (?, ?)", (user["id"], score))
                report["users_imported"] += 1
                report["legacy_scores_imported"] += 1
            except ValueError as exc:
                report["users_skipped"] += 1
                report["warnings"].append(f"user-data.txt line {number}: skipped ({exc}).")

    def _import_question_lines(self, lines, report):
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            parts = line.strip().split("|")
            if len(parts) != 2 or not all(part.strip() for part in parts):
                report["questions_skipped"] += 1
                report["warnings"].append(f"questions.txt line {number}: skipped malformed question|answer.")
                continue
            original, answer = (part.strip() for part in parts)
            answer = answer.lower()
            question, reason = re.sub(r"_{2,}", "____", original), None
            if not re.fullmatch(r"[a-z]+", answer):
                reason = "Answer must be a single English word."
            elif not re.search(r"_{2,}", question):
                pattern = re.compile(r"(?<!\w)" + re.escape(answer) + r"(?!\w)", re.IGNORECASE)
                question, count = pattern.subn("____", question, count=1)
                if not count:
                    reason = "Question has no blank and does not contain its answer."
            if reason:
                inserted = self.conn.execute(
                    "INSERT OR IGNORE INTO legacy_questions(question, answer, reason) VALUES (?, ?, ?)",
                    (original, answer, reason),
                ).rowcount
                report["questions_archived"] += inserted
                report["questions_skipped"] += 1 - inserted
                report["warnings"].append(f"questions.txt line {number}: archived for review. {reason}")
                continue
            inserted = self.conn.execute(
                "INSERT OR IGNORE INTO questions(mode, question, answer) VALUES ('hard', ?, ?)",
                (question, answer),
            ).rowcount
            report["questions_imported"] += inserted
            report["questions_skipped"] += 1 - inserted
            if not inserted:
                report["warnings"].append(f"questions.txt line {number}: skipped duplicate question.")

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
