"""퀴즈 플레이 세션을 담당하는 모듈.

문제 수 선택, 랜덤 출제, 힌트 처리, 채점, 중단 시 부분 결과 계산까지
"한 번의 플레이"에 필요한 세부 흐름을 이 파일에서 관리한다.
"""

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
    """퀴즈 세션이 끝난 뒤 상위 레이어로 넘길 결과 묶음."""

    selected_count: int
    answered_count: int
    correct_count: int
    total_score: int
    hint_used_count: int
    interrupted: bool = False


def calculate_points(*, correct: bool, hint_used: bool) -> int:
    """정답 여부와 힌트 사용 여부를 바탕으로 획득 점수를 계산한다."""
    if not correct:
        return 0
    return HINT_POINTS if hint_used else BASE_POINTS


class QuizSessionRunner:
    """퀴즈 풀이 한 판의 진행을 담당하는 실행기."""

    def __init__(
        self,
        input_fn: InputFn,
        output_fn: OutputFn,
        *,
        sample_fn: Callable[[list[Quiz], int], list[Quiz]] | None = None,
    ) -> None:
        self.input_fn = input_fn
        self.output_fn = output_fn
        # 테스트에서는 랜덤 대신 고정 순서를 주입할 수 있도록 함수 의존성을 분리한다.
        self.sample_fn = sample_fn or random.sample

    def play(self, quizzes: list[Quiz]) -> QuizSessionResult:
        """주어진 퀴즈 목록으로 실제 플레이를 진행하고 결과를 반환한다."""
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
            # 세션 중간에 종료되더라도, 여기까지 누적한 결과를 상위 레이어가
            # history에 남길 수 있도록 "부분 결과"를 반환한다.
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
        """한 문제에 대한 최종 답안과 힌트 사용 여부를 돌려준다."""
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
                # 힌트는 정답 공개가 아니라 보조 설명만 제공하도록 설계했다.
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
