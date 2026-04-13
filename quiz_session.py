from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from console_io import InputFn, OutputFn, SafeExitRequest, prompt_int, prompt_text
from game_constants import BASE_POINTS, HINT_POINTS
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
            f"몇 문제를 풀까요? (1-{len(quizzes)}): ",
            minimum=1,
            maximum=len(quizzes),
        )

        selected_quizzes = self.sample_fn(quizzes, selected_count)
        answered_count = 0
        correct_count = 0
        total_score = 0
        hint_used_count = 0

        self.output_fn("")
        self.output_fn(f"총 {selected_count}문제를 시작합니다.")

        try:
            for question_index, quiz in enumerate(selected_quizzes, start=1):
                self.output_fn("")
                self.output_fn("-" * 40)
                self.output_fn(f"문제 {question_index}/{selected_count}")
                self.output_fn(quiz.display())

                answer, used_hint = self._prompt_answer_for_quiz(quiz)
                answered_count += 1
                if used_hint:
                    hint_used_count += 1

                if quiz.is_correct(answer):
                    correct_count += 1
                    points = calculate_points(correct=True, hint_used=used_hint)
                    total_score += points
                    self.output_fn(f"정답입니다! +{points}점")
                else:
                    correct_text = quiz.choices[quiz.answer - 1]
                    self.output_fn(f"오답입니다. 정답은 {quiz.answer}번, {correct_text}입니다.")
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
                "정답 입력 (1-4, 힌트는 h): ",
            ).lower()
            if answer_text == "h":
                if hint_used:
                    self.output_fn("이 문제에서는 이미 힌트를 사용했습니다.")
                    continue
                hint_used = True
                self.output_fn(f"힌트: {quiz.hint}")
                continue

            try:
                answer = int(answer_text)
            except ValueError:
                self.output_fn("1, 2, 3, 4 또는 h만 입력해주세요.")
                continue

            if 1 <= answer <= 4:
                return answer, hint_used

            self.output_fn("1부터 4까지의 숫자 또는 h를 입력해주세요.")
