"""Game rules shared by the Tkinter app and tests, without UI or database access."""

from collections import Counter
import random


MODES = ("easy", "medium", "hard")


def _is_word(value, length=None):
    return (
        isinstance(value, str)
        and value.isascii()
        and value.isalpha()
        and (length is None or len(value) == length)
    )


def wordle_feedback(guess, answer):
    """Return five correct/present/absent marks, respecting repeated letters.

    Exact matches consume their answer letters first. A second pass assigns
    yellow marks only while unmatched copies of that letter remain.
    """
    if not isinstance(guess, str) or not isinstance(answer, str):
        raise ValueError("Wordle guesses and answers must contain five English letters.")
    guess, answer = guess.strip().lower(), answer.strip().lower()
    if not _is_word(guess, 5) or not _is_word(answer, 5):
        raise ValueError("Wordle guesses and answers must contain five English letters.")

    marks = ["absent"] * 5
    unmatched = Counter()
    for index, (guessed_letter, answer_letter) in enumerate(zip(guess, answer)):
        if guessed_letter == answer_letter:
            marks[index] = "correct"
        else:
            unmatched[answer_letter] += 1

    for index, letter in enumerate(guess):
        if marks[index] != "correct" and unmatched[letter] > 0:
            marks[index] = "present"
            unmatched[letter] -= 1
    return tuple(marks)


class GameSession:
    """One score streak in easy scramble, medium Wordle, or hard fill-in.

    A correct answer earns one point and immediately loads another question.
    Start a new GameSession to play again with a score of zero. Storage remains
    the caller's responsibility, so no database writes occur in this class.
    """

    def __init__(self, mode, questions, allowed_words=None, rng=None):
        if mode not in MODES:
            raise ValueError("Choose a game mode: easy, medium, or hard.")
        self.mode = mode
        self._rng = rng if rng is not None else random.Random()
        self._questions = self._validate_questions(questions)
        self._allowed_words = {
            word.strip().lower()
            for word in (allowed_words if allowed_words is not None else ())
            if isinstance(word, str) and _is_word(word.strip(), 5)
        }
        self._allowed_words.update(question["answer"] for question in self._questions)
        self.score = 0
        self.mistakes = 0
        self.attempts = 0
        self.finished = False
        self.history = []
        self.current_question = None
        self.prompt = ""
        self.answer = ""
        self._bag = []
        self._last_question = None
        self._new_question()

    def _validate_questions(self, questions):
        if questions is None:
            raise ValueError(f"No questions are available for {self.mode} mode.")
        validated = []
        seen = set()
        for index, question in enumerate(questions, start=1):
            if not isinstance(question, dict):
                raise ValueError(f"Question {index} must contain a question and answer.")
            answer = question.get("answer")
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError(f"Question {index} has no answer.")
            answer = answer.strip().lower()
            sentence = question.get("question", "")
            if not isinstance(sentence, str):
                raise ValueError(f"Question {index} has invalid question text.")
            sentence = sentence.strip()
            if self.mode == "easy" and (not _is_word(answer) or len(set(answer)) < 2):
                raise ValueError(
                    f"Easy question {index} needs an English word with at least "
                    "two different letters so it can be scrambled."
                )
            if self.mode == "medium" and not _is_word(answer, 5):
                raise ValueError(f"Medium question {index} needs a five-letter English answer.")
            if self.mode == "hard" and "____" not in sentence:
                raise ValueError(f"Hard question {index} needs a sentence with a ____ blank.")
            # Repeated database rows must not make identical puzzles repeat.
            identity = (sentence if self.mode == "hard" else "", answer)
            if identity not in seen:
                normalized = dict(question)
                normalized.update(question=sentence, answer=answer)
                validated.append(normalized)
                seen.add(identity)
        if not validated:
            raise ValueError(f"No questions are available for {self.mode} mode.")
        return validated

    @property
    def remaining_attempts(self):
        """Attempts left on this word, or remaining mistakes in easy/hard."""
        if self.mode == "medium":
            return max(0, 5 - self.attempts)
        return max(0, 3 - self.mistakes)

    def _new_question(self):
        if not self._bag:
            self._bag = list(range(len(self._questions)))
            self._rng.shuffle(self._bag)
            # Avoid repeating the final puzzle of the previous shuffled bag.
            if len(self._bag) > 1 and self._bag[-1] == self._last_question:
                self._bag[0], self._bag[-1] = self._bag[-1], self._bag[0]
        index = self._bag.pop()
        self._last_question = index
        self.current_question = dict(self._questions[index])
        self.answer = self.current_question["answer"]
        self.attempts = 0
        self.history = []
        if self.mode == "easy":
            self.prompt = self._scramble(self.answer).upper()
        elif self.mode == "medium":
            self.prompt = "Guess the five-letter word. You have 5 tries."
        else:
            self.prompt = self.current_question["question"]

    def _scramble(self, answer):
        letters = list(answer)
        for _ in range(8):
            self._rng.shuffle(letters)
            scrambled = "".join(letters)
            if scrambled != answer:
                return scrambled
        # Even an unlucky shuffle (or a deterministic test RNG) must produce
        # a different arrangement. Validation guarantees a distinct letter.
        for index in range(1, len(letters)):
            if letters[index] != letters[0]:
                letters[0], letters[index] = letters[index], letters[0]
                break
        return "".join(letters)

    def submit(self, guess):
        """Submit a guess and return a status/message dictionary.

        Valid Wordle guesses also return a feedback tuple. Only a finished
        result reveals the answer. Invalid input never consumes a chance.
        """
        if self.finished:
            return self._finished_result()
        if not isinstance(guess, str) or not guess.strip():
            return {"status": "invalid", "message": "Enter an answer first."}
        guess = guess.strip().lower()
        feedback = None
        if self.mode == "medium":
            if not _is_word(guess, 5):
                return {"status": "invalid", "message": "Enter exactly five English letters."}
            if guess not in self._allowed_words:
                return {"status": "invalid", "message": "That word is not in the word list."}
            feedback = wordle_feedback(guess, self.answer)
            self.history.append((guess, feedback))
        self.attempts += 1

        if guess == self.answer:
            self.score += 1
            if self.mode == "hard":
                self.mistakes = 0
            self._new_question()
            result = {"status": "correct", "message": "Correct! +1 point. Try the next question."}
        else:
            if self.mode != "medium":
                self.mistakes += 1
            if self.remaining_attempts == 0:
                self.finished = True
                result = self._finished_result()
            else:
                remaining = self.remaining_attempts
                unit = "try" if remaining == 1 else "tries"
                result = {
                    "status": "incorrect",
                    "message": f"Not quite. {remaining} {unit} remaining.",
                }
        if feedback is not None:
            result["feedback"] = feedback
        return result

    def _finished_result(self):
        return {
            "status": "finished",
            "message": f"Game over! Your final score is {self.score}.",
            "answer": self.answer,
        }
