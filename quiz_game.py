from __future__ import annotations

import random
from pathlib import Path
from typing import Callable

from console_io import SafeExitRequest, prompt_int, prompt_text
from game_constants import (
    APP_STATE_NOTICE,
    APP_TITLE,
    BASE_POINTS,
    DEFAULT_STATE_PATH,
    EXIT_MESSAGE,
    HINT_POINTS,
    MENU_DIVIDER,
    MENU_OPTIONS,
    MENU_PROMPT,
    NO_REGISTERED_QUIZZES_MESSAGE,
    QUIZ_FINISHED_MESSAGE,
    QUIZ_INTERRUPTED_RECORDED_MESSAGE,
    SAVE_AND_EXIT_MESSAGE,
    SUMMARY_ANSWERED_COUNT_LABEL,
    SUMMARY_BEST_SCORE_LABEL,
    SUMMARY_CORRECT_COUNT_LABEL,
    SUMMARY_SCORE_LABEL,
    SUMMARY_SELECTED_COUNT_LABEL,
)
from quiz_catalog import QuizCatalogManager
from quiz import Quiz
from quiz_session import QuizSessionRunner, calculate_points
from scoreboard import record_history, show_scores
from state_store import GameState, StateStore


class QuizGame:
    def __init__(
        self,
        state_path: str | Path = DEFAULT_STATE_PATH,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self.state_store = StateStore(state_path, output_fn)
        self.state_path = self.state_store.state_path
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.catalog = QuizCatalogManager(input_fn, output_fn)
        self.session_runner = QuizSessionRunner(input_fn, output_fn)
        self.quizzes: list[Quiz] = []
        self.best_score = 0
        self.history: list[dict[str, object]] = []
        self.next_quiz_id = 1
        self.load_state()

    def run(self) -> None:
        self.output_fn(APP_TITLE)
        self.output_fn(APP_STATE_NOTICE)

        while True:
            try:
                self.show_menu()
                choice = self.prompt_int(MENU_PROMPT, minimum=1, maximum=6)

                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.delete_quiz()
                elif choice == 5:
                    self.show_scores()
                else:
                    self.safe_exit()
                    return
            except SafeExitRequest:
                self.safe_exit()
                return

    def show_menu(self) -> None:
        self.output_fn("")
        self.output_fn(MENU_DIVIDER)
        for option in MENU_OPTIONS:
            self.output_fn(option)
        self.output_fn(MENU_DIVIDER)

    def load_state(self) -> None:
        state = self.state_store.load_state()
        self.quizzes = state.quizzes
        self.best_score = state.best_score
        self.history = state.history
        self.next_quiz_id = state.next_quiz_id

    def save_state(self) -> bool:
        return self.state_store.save_state(
            GameState(
                quizzes=self.quizzes,
                best_score=self.best_score,
                history=self.history,
                next_quiz_id=self.next_quiz_id,
            )
        )

    def play_quiz(self) -> None:
        if not self.quizzes:
            self.output_fn(NO_REGISTERED_QUIZZES_MESSAGE)
            return

        self.session_runner.sample_fn = random.sample
        result = self.session_runner.play(self.quizzes)

        self._record_history(
            selected_count=result.selected_count,
            answered_count=result.answered_count,
            correct_count=result.correct_count,
            total_score=result.total_score,
            hint_used_count=result.hint_used_count,
        )
        self.save_state()

        if result.interrupted:
            self.output_fn(QUIZ_INTERRUPTED_RECORDED_MESSAGE)
            raise SafeExitRequest

        self.output_fn("")
        self.output_fn(QUIZ_FINISHED_MESSAGE)
        self.output_fn(f"{SUMMARY_SELECTED_COUNT_LABEL}: {result.selected_count}")
        self.output_fn(f"{SUMMARY_ANSWERED_COUNT_LABEL}: {result.answered_count}")
        self.output_fn(f"{SUMMARY_CORRECT_COUNT_LABEL}: {result.correct_count}")
        self.output_fn(f"{SUMMARY_SCORE_LABEL}: {result.total_score}")
        self.output_fn(f"{SUMMARY_BEST_SCORE_LABEL}: {self.best_score}")

    def add_quiz(self) -> None:
        self.next_quiz_id = self.catalog.add_quiz(self.quizzes, self.next_quiz_id)
        self.save_state()

    def list_quizzes(self) -> None:
        self.catalog.list_quizzes(self.quizzes)

    def delete_quiz(self) -> None:
        if self.catalog.delete_quiz(self.quizzes):
            self.save_state()

    def show_scores(self) -> None:
        show_scores(self.output_fn, best_score=self.best_score, history=self.history)

    def prompt_int(
        self,
        prompt: str,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int:
        return prompt_int(
            self.input_fn,
            self.output_fn,
            prompt,
            minimum=minimum,
            maximum=maximum,
        )

    def prompt_text(self, prompt: str) -> str:
        return prompt_text(self.input_fn, self.output_fn, prompt)

    def safe_exit(self) -> None:
        saved = self.save_state()
        if saved:
            self.output_fn(SAVE_AND_EXIT_MESSAGE)
        else:
            self.output_fn(EXIT_MESSAGE)

    def calculate_points(self, *, correct: bool, hint_used: bool) -> int:
        return calculate_points(correct=correct, hint_used=hint_used)

    def _record_history(
        self,
        *,
        selected_count: int,
        answered_count: int,
        correct_count: int,
        total_score: int,
        hint_used_count: int,
    ) -> None:
        self.best_score = record_history(
            self.history,
            self.best_score,
            selected_count=selected_count,
            answered_count=answered_count,
            correct_count=correct_count,
            total_score=total_score,
            hint_used_count=hint_used_count,
        )
