from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from console_io import InputFn, OutputFn, SafeExitRequest, prompt_int, prompt_text
from game_constants import (
    ANSWER_INPUT_PROMPT,
    ANSWER_OR_HINT_ONLY_MESSAGE,
    ANSWER_RANGE_OR_HINT_MESSAGE,
    BASE_POINTS,
    CORRECT_ANSWER_MESSAGE_TEMPLATE,
    HINT_ALREADY_USED_MESSAGE,
    HINT_COMMAND,
    HINT_MESSAGE_TEMPLATE,
    HINT_POINTS,
    QUESTION_COUNT_PROMPT_TEMPLATE,
    QUESTION_PROGRESS_TEMPLATE,
    QUIZ_START_MESSAGE_TEMPLATE,
    SECTION_DIVIDER,
    WRONG_ANSWER_MESSAGE_TEMPLATE,
)
from quiz import Quiz


@dataclass(slots=True)
class QuizSessionResult:
    selected_count: int
    answered_count: int
    correct_count: int
    total_score: int
    hint_used_count: int
    interrupted: bool = False


def calculate_points(*, correct: bool, hint_used: bool) -> int:
    if not correct:
        return 0
    return HINT_POINTS if hint_used else BASE_POINTS


class QuizSessionRunner:
    def __init__(
        self,
        input_fn: InputFn,
        output_fn: OutputFn,
        *,
        sample_fn: Callable[[list[Quiz], int], list[Quiz]] | None = None,
    ) -> None:
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.sample_fn = sample_fn or random.sample

    def play(self, quizzes: list[Quiz]) -> QuizSessionResult:
        selected_count = prompt_int(
            self.input_fn,
            self.output_fn,
            QUESTION_COUNT_PROMPT_TEMPLATE.format(quiz_count=len(quizzes)),
            minimum=1,
            maximum=len(quizzes),
        )

        selected_quizzes = self.sample_fn(quizzes, selected_count)
        answered_count = 0
        correct_count = 0
        total_score = 0
        hint_used_count = 0

        self.output_fn("")
        self.output_fn(QUIZ_START_MESSAGE_TEMPLATE.format(selected_count=selected_count))

        try:
            for question_index, quiz in enumerate(selected_quizzes, start=1):
                self.output_fn("")
                self.output_fn(SECTION_DIVIDER)
                self.output_fn(
                    QUESTION_PROGRESS_TEMPLATE.format(
                        question_index=question_index,
                        selected_count=selected_count,
                    )
                )
                self.output_fn(quiz.display())

                answer, used_hint = self._prompt_answer_for_quiz(quiz)
                answered_count += 1
                if used_hint:
                    hint_used_count += 1

                if quiz.is_correct(answer):
                    correct_count += 1
                    points = calculate_points(correct=True, hint_used=used_hint)
                    total_score += points
                    self.output_fn(CORRECT_ANSWER_MESSAGE_TEMPLATE.format(points=points))
                else:
                    correct_text = quiz.choices[quiz.answer - 1]
                    self.output_fn(
                        WRONG_ANSWER_MESSAGE_TEMPLATE.format(
                            answer=quiz.answer,
                            correct_text=correct_text,
                        )
                    )
        except SafeExitRequest:
            return QuizSessionResult(
                selected_count=selected_count,
                answered_count=answered_count,
                correct_count=correct_count,
                total_score=total_score,
                hint_used_count=hint_used_count,
                interrupted=True,
            )

        return QuizSessionResult(
            selected_count=selected_count,
            answered_count=answered_count,
            correct_count=correct_count,
            total_score=total_score,
            hint_used_count=hint_used_count,
        )

    def _prompt_answer_for_quiz(self, quiz: Quiz) -> tuple[int, bool]:
        hint_used = False

        while True:
            answer_text = prompt_text(
                self.input_fn,
                self.output_fn,
                ANSWER_INPUT_PROMPT,
            ).lower()
            if answer_text == HINT_COMMAND:
                if hint_used:
                    self.output_fn(HINT_ALREADY_USED_MESSAGE)
                    continue
                hint_used = True
                self.output_fn(HINT_MESSAGE_TEMPLATE.format(hint=quiz.hint))
                continue

            try:
                answer = int(answer_text)
            except ValueError:
                self.output_fn(ANSWER_OR_HINT_ONLY_MESSAGE)
                continue

            if 1 <= answer <= 4:
                return answer, hint_used

            self.output_fn(ANSWER_RANGE_OR_HINT_MESSAGE)
