# Interactive English Learning

A Python/Tkinter desktop application with three English word games and SQLite persistence. It uses Python's standard library; no pip packages, database server, or internet connection are needed to play.

## Run on Windows

Install Python 3.10 or newer with Tcl/Tk support, then double-click **Run English Learner.bat**. Alternatively, open a terminal in this folder and run:

```powershell
python main.py
```

Select the **Create account** tab, enter a username and password, and select **Create account**. The app then returns to **Log in**; enter your password to continue. From the dashboard, select **Play a Game** to choose Easy, Medium, or Hard. The app creates `english_learning.db` beside the Python files on first launch. Keep that database to preserve accounts and scores.

An alternate database location can be supplied for testing or separate groups of players:

```powershell
python main.py --database "C:\path\to\classroom.db"
```

The parent folder must already exist. Python's Windows installer normally includes Tkinter. To check that it is available, run `python -m tkinter`.

## Using the interface

The dashboard contains a **Play a Game** button and your best scores. The top navigation provides **Dashboard**, **Play**, **Leaderboards**, **Profile**, and **Log out**. The current section is highlighted. During a game, use **End run** to return to the dashboard while keeping your best score.

Use **Dark mode** or **Light mode** at the top right to change the theme. This button is available on every screen, including login and gameplay. The whole interface changes immediately, including inputs, buttons, cards, tables, and scrollbars. Switching preserves your game, typed answers, and unsaved profile changes. The preference is saved in SQLite for the next launch; it applies to this database, including before login.

Screens use short titles and essential instructions. Game screens show the score, personal best, and remaining chances together. Feedback appears after an answer is submitted, and **Check answer** becomes available when an answer is entered. Login, registration, and profile validation messages appear only when needed. Password fields include **Show** and **Hide** controls.

The window can be resized, with a minimum size of 760 × 640. Text wraps to the available width, and longer pages can be scrolled using the mouse wheel or their scrollbar. The Wordle layout places the board beside the answer controls when there is enough room and stacks them at smaller widths.

- Use **Tab** and **Shift+Tab** to move between fields and controls. Focused buttons have a visible outline, and scrolling pages reveal the focused control.
- Use **Enter** or **Space** to activate a focused button. In an answer field, **Enter** submits the answer; in an account form, it submits that form.
- Use **Ctrl+A** to select all text in an entry field.
- In Wordle, type into **Your answer** or click the letter keys. **Delete letter** removes a letter, and the current board row previews the answer before submission. Use **Check word** to submit it.
- Wordle includes a labeled color legend and written feedback describing each submitted letter's result, so clues are also available as text.

## Game rules

| Mode | Game | Correct answer | Game ends when |
| --- | --- | --- | --- |
| Easy | Word Scramble | +1 point; a new scrambled word appears | Three wrong answers **in total across the run**, even if correct answers come between them |
| Medium | Wordle | +1 point; a new five-letter word with five fresh guesses | One word is not solved within **five valid guesses** |
| Hard | Fill in the Blank | +1 point; a new sentence appears; consecutive mistake count resets | Three wrong answers **in a row** |

Wrong answers let you retry the current puzzle. In hard mode, a correct answer resets the wrong-answer counter; in easy mode, it does not. Empty answers never consume an attempt. Answers ignore surrounding spaces and letter case.

Wordle uses green tiles for letters in the right position, gold for letters present elsewhere, and gray for absent letters. Repeated letters are counted correctly. The on-screen keyboard keeps track of previous clues, and feedback also describes the colors in words. A valid guess must be an English word of exactly five ASCII letters from the bundled dictionary. Invalid guesses do not consume an attempt. A correct answer on the fifth guess still earns a point. As requested, this version gives five guesses per word and continues across multiple words in one run.

The guess vocabulary contains more than 7,000 words from a permissively licensed offline dictionary, including American and British spellings. It is independent of the New York Times dictionary. The answer bank uses a smaller selection of common words. See `THIRD_PARTY_NOTICES.md` for sources and licensing.

Every new run starts at **0**. The game-over screen shows the final score, the missed answer, and the personal best, with buttons to **Play again**, **Choose another game**, or **View this leaderboard**. **End run** ends a run early and returns to the dashboard while keeping any personal best earned so far.

## Accounts and leaderboards

- Each player has an independent highest score for each of the three modes. Scores never add up across runs.
- Scores are saved after every correct answer and when a run ends. A lower later score never overwrites a higher one.
- The leaderboards rank scores from highest to lowest. Equal scores share a rank, using competition ranking such as `1, 1, 3`; tied names appear alphabetically.
- An account appears on a mode's leaderboard after starting that mode, including a score of zero.
- **Profile** allows username changes and optional password changes. Leave the new password blank to keep the existing password. Scores remain associated with the same account.
- The red **Delete Account** button is on **Profile**. The app asks for confirmation and deletes the account and all associated scores.
- Usernames may have up to 32 characters and are case-insensitive for ASCII letters. Passwords preserve spaces and case and may have up to 256 characters. SQLite stores salted PBKDF2-SHA256 password hashes, rather than plaintext passwords.

## Moving data from the original version

Place the original `user-data.txt` and/or `questions.txt` beside the selected database, then start the app. Each source file is automatically imported once. Original files are left unchanged, and a startup notice reports imported, skipped, or archived records.

- `user-data.txt` uses the original `username,password,score` format. Valid unique accounts are imported, and passwords are hashed during import. Malformed rows or duplicate usernames are skipped and reported.
- The old scores were cumulative and awarded ten points per answer. They cannot represent the new best-run scores, so their original values are preserved in the **`legacy_scores`** SQL table. All new leaderboards begin at zero.
- `questions.txt` uses `question|answer`. Valid fill-in-the-blank questions are imported into hard mode. Runs of underscores are normalized to `____`. If a sentence contains its answer but has no blank, the importer replaces that answer with `____`.
- Questions that cannot safely become fill-in-the-blank puzzles, including the original sample placeholder, are preserved in **`legacy_questions`** with a reason for review. They are not added to gameplay.
- Import markers prevent deleted accounts from being recreated by the old text file on the next launch. Editing an already imported text file will not update the database; edit the SQL content instead.

Once imported, all live account, score, question, answer, and Wordle dictionary reads/writes use SQLite. `seed_data.py` and `wordle_dictionary.sql` only provide initial content. The app does not write progress back to text files. When handling backups, remember that original legacy user files still contain their original passwords; the new database contains hashes.

## Database and content

The schema is created automatically by `storage.py`:

| Table | Purpose |
| --- | --- |
| `users` | Stable user IDs, unique usernames, salted password hashes |
| `high_scores` | One maximum score per user and mode |
| `questions` | Mode, question/prompt text, and answer |
| `allowed_words` | Accepted five-letter Wordle guesses |
| `metadata` | Seed and migration markers, plus the saved light/dark preference |
| `legacy_scores` | Imported old cumulative scores |
| `legacy_questions` | Imported question/answer records needing review |

SQL statements use parameters for input values. Foreign keys remove a user's scores when the account is deleted. Each score update uses SQLite's `MAX` in an upsert so a lower score cannot replace a higher one.

To add content to an existing database, run SQL in a SQLite editor, for example:

```sql
INSERT OR IGNORE INTO questions (mode, question, answer)
VALUES ('easy', 'Unscramble the word.', 'sunflower');

INSERT OR IGNORE INTO questions (mode, question, answer)
VALUES ('medium', 'Guess the five-letter word.', 'bloom');

INSERT OR IGNORE INTO allowed_words (word) VALUES ('bloom');

INSERT OR IGNORE INTO questions (mode, question, answer)
VALUES ('hard', 'The past tense of swim is ____.', 'swam');
```

Use lowercase answers. Easy answers must contain ASCII letters and at least two different letters. Medium answers must have exactly five ASCII letters and are always accepted as guesses. Hard prompts must contain `____`; use clear sentences with an unambiguous expected answer. Identical mode/question/answer records are unique, so an existing record should be updated or skipped rather than inserted twice. New sessions read the updated content from SQL.

To inspect archived scores:

```sql
SELECT u.username, l.score AS original_cumulative_score
FROM legacy_scores AS l JOIN users AS u ON u.id = l.user_id
ORDER BY l.score DESC;
```

Close the app before copying `english_learning.db` as a backup.

## Project files and checks

- `main.py`: application entry point, account and game actions, and screen navigation.
- `screens.py`: screen layouts, form fields, game boards, and leaderboard presentation.
- `ui_components.py`: shared colors, typography, button interaction states, and scrolling page components.
- `storage.py`: SQL schema, account operations, high scores, and legacy imports.
- `game_logic.py`: scoring, attempts, puzzle selection, scrambling, and Wordle feedback.
- `seed_data.py`: initial questions and answer words.
- `wordle_dictionary.sql`: offline Wordle guess dictionary, imported once.
- `tests/`: gameplay, persistence, migration, and real Tkinter/SQLite integration checks.

Run the tests from this folder:

```powershell
python -m unittest discover -s tests -v
```

The integration tests require a desktop with Tkinter available and use disposable databases. No test accounts are added to your real database.

## Student demonstration walkthrough

For a demonstration with separate accounts and scores, launch from the project folder with:

```powershell
python main.py --database "demo.db"
```

This creates or reopens `demo.db` in that folder. The normal launcher continues to use `english_learning.db`.

1. Create a demonstration account and log in. Point out the three personal best cards on the dashboard and the separate game choices.
2. Start **Easy**. Solve a scramble to show the score increasing, then submit a wrong answer to demonstrate feedback and the total mistake counter. Use **End run** and check the saved best on the dashboard.
3. Start **Medium**. Enter a five-letter word to demonstrate the pending row, submit it to show the board and keyboard clues, and explain that invalid guesses do not use a chance. Use **End run** when ready to continue.
4. Start **Hard**. Explain that this mode ends after three consecutive mistakes and that a correct answer resets that count. End the run or continue to the game-over screen to show the replay choices.
5. Open **Leaderboards**, switch between difficulty tabs, and explain that each player keeps a separate maximum score per mode. A new run always begins at zero.
6. Open **Profile**, change the demonstration username, and show that the scores stay with the account. Log out and back in to demonstrate persistence.
7. Resize the window and use Tab, Enter, and the page scrollbar to demonstrate the interface controls. When presenting the code, follow the flow from `screens.py` through `main.py` to `game_logic.py` and `storage.py`.
