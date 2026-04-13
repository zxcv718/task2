"""게임 전체 흐름을 조율하는 상위 모듈.

실제 세부 작업은 세션, 카탈로그, 저장소, 점수판 모듈이 나눠 맡고,
`QuizGame`은 그들을 연결해 메뉴 기반 콘솔 프로그램으로 동작하게 만든다.
"""

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
    """퀴즈 게임 전체 라이프사이클을 관리하는 상위 객체."""

    def __init__(
        self,
        state_path: str | Path = DEFAULT_STATE_PATH,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        """실행에 필요한 하위 서비스들을 구성하고 저장 상태를 불러온다."""
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
        """메뉴를 반복 출력하며 사용자의 선택에 따라 기능을 실행한다."""
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
        """메인 메뉴를 화면에 출력한다."""
        self.output_fn("")
        self.output_fn(MENU_DIVIDER)
        for option in MENU_OPTIONS:
            self.output_fn(option)
        self.output_fn(MENU_DIVIDER)

    def load_state(self) -> None:
        """저장소에서 읽은 게임 상태를 현재 객체 속성에 반영한다."""
        state = self.state_store.load_state()
        self.quizzes = state.quizzes
        self.best_score = state.best_score
        self.history = state.history
        self.next_quiz_id = state.next_quiz_id

    def save_state(self) -> bool:
        """현재 메모리 상태를 `state_store`를 통해 저장한다."""
        return self.state_store.save_state(
            GameState(
                quizzes=self.quizzes,
                best_score=self.best_score,
                history=self.history,
                next_quiz_id=self.next_quiz_id,
            )
        )

    def play_quiz(self) -> None:
        """퀴즈 세션을 실행하고 결과를 history 및 최고 점수에 반영한다."""
        if not self.quizzes:
            self.output_fn(NO_REGISTERED_QUIZZES_MESSAGE)
            return

        # 테스트에서는 이 함수를 patch해서 문제 순서를 고정할 수 있다.
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
            # 세션 내부에서 입력 중단이 발생했더라도 결과는 이미 기록했으므로,
            # 여기서는 안전 종료 흐름으로만 넘긴다.
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
        """새 퀴즈를 추가하고 저장 파일에 즉시 반영한다."""
        self.next_quiz_id = self.catalog.add_quiz(self.quizzes, self.next_quiz_id)
        self.save_state()

    def list_quizzes(self) -> None:
        """등록된 퀴즈 목록을 출력한다."""
        self.catalog.list_quizzes(self.quizzes)

    def delete_quiz(self) -> None:
        """퀴즈 삭제가 실제로 일어났을 때만 상태를 저장한다."""
        if self.catalog.delete_quiz(self.quizzes):
            self.save_state()

    def show_scores(self) -> None:
        """최고 점수와 최근 히스토리를 출력한다."""
        show_scores(self.output_fn, best_score=self.best_score, history=self.history)

    def prompt_int(
        self,
        prompt: str,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int:
        """하위 입력 함수에 접근하기 위한 래퍼 메서드."""
        return prompt_int(
            self.input_fn,
            self.output_fn,
            prompt,
            minimum=minimum,
            maximum=maximum,
        )

    def prompt_text(self, prompt: str) -> str:
        """텍스트 입력 함수를 객체 메서드 형태로 노출하는 래퍼다."""
        return prompt_text(self.input_fn, self.output_fn, prompt)

    def safe_exit(self) -> None:
        """가능한 범위에서 상태를 저장한 뒤 종료 메시지를 출력한다."""
        saved = self.save_state()
        if saved:
            self.output_fn(SAVE_AND_EXIT_MESSAGE)
        else:
            self.output_fn(EXIT_MESSAGE)

    def calculate_points(self, *, correct: bool, hint_used: bool) -> int:
        """기존 테스트 호환을 위해 점수 계산 함수를 메서드 형태로 제공한다."""
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
        """현재 세션 결과를 history에 추가하고 최고 점수를 갱신한다."""
        self.best_score = record_history(
            self.history,
            self.best_score,
            selected_count=selected_count,
            answered_count=answered_count,
            correct_count=correct_count,
            total_score=total_score,
            hint_used_count=hint_used_count,
        )
