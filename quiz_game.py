from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable

from console_io import SafeExitRequest, prompt_int, prompt_text
from game_constants import BASE_POINTS, HINT_POINTS, RECENT_HISTORY_LIMIT
from quiz import Quiz
from quiz_session import QuizSessionRunner, calculate_points
from state_store import GameState, StateStore


class QuizGame:
    def __init__(
        self,
        state_path: str | Path = "state.json",
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self.state_store = StateStore(state_path, output_fn)
        self.state_path = self.state_store.state_path
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.session_runner = QuizSessionRunner(input_fn, output_fn)
        self.quizzes: list[Quiz] = []
        self.best_score = 0
        self.history: list[dict[str, object]] = []
        self.next_quiz_id = 1
        self.load_state()

    def run(self) -> None:
        self.output_fn("나만의 퀴즈 게임")
        self.output_fn("진행 상황은 state.json에 저장됩니다.")

        while True:
            try:
                self.show_menu()
                choice = self.prompt_int("메뉴 번호를 선택하세요: ", minimum=1, maximum=6)

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
        self.output_fn("=" * 40)
        self.output_fn("1. 퀴즈 풀기")
        self.output_fn("2. 퀴즈 추가")
        self.output_fn("3. 퀴즈 목록")
        self.output_fn("4. 퀴즈 삭제")
        self.output_fn("5. 점수 확인")
        self.output_fn("6. 종료")
        self.output_fn("=" * 40)

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
            self.output_fn("현재 등록된 퀴즈가 없습니다.")
            return

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
            self.output_fn("퀴즈 진행이 중단되어 현재까지의 결과를 기록했습니다.")
            raise SafeExitRequest

        self.output_fn("")
        self.output_fn("퀴즈가 끝났습니다.")
        self.output_fn(f"선택한 문제 수: {result.selected_count}")
        self.output_fn(f"푼 문제 수: {result.answered_count}")
        self.output_fn(f"맞힌 문제 수: {result.correct_count}")
        self.output_fn(f"점수: {result.total_score}")
        self.output_fn(f"최고 점수: {self.best_score}")

    def add_quiz(self) -> None:
        self.output_fn("")
        self.output_fn("새 퀴즈 추가")

        question = self.prompt_text("문제: ")
        choices = [
            self.prompt_text("선택지 1: "),
            self.prompt_text("선택지 2: "),
            self.prompt_text("선택지 3: "),
            self.prompt_text("선택지 4: "),
        ]
        answer = self.prompt_int("정답 번호를 입력하세요 (1-4): ", minimum=1, maximum=4)
        hint = self.prompt_text("힌트: ")

        quiz = Quiz(
            quiz_id=self.next_quiz_id,
            question=question,
            choices=choices,
            answer=answer,
            hint=hint,
        )
        self.quizzes.append(quiz)
        self.next_quiz_id += 1
        self.save_state()

        self.output_fn(f"{quiz.quiz_id}번 퀴즈가 추가되었습니다.")

    def list_quizzes(self) -> None:
        if not self.quizzes:
            self.output_fn("표시할 퀴즈가 없습니다.")
            return

        self.output_fn("")
        self.output_fn("저장된 퀴즈 목록")
        for quiz in sorted(self.quizzes, key=lambda item: item.quiz_id):
            self.output_fn("-" * 40)
            self.output_fn(f"ID: {quiz.quiz_id}")
            self.output_fn(f"문제: {quiz.question}")
            for index, choice in enumerate(quiz.choices, start=1):
                self.output_fn(f"  {index}. {choice}")
            self.output_fn(f"정답 번호: {quiz.answer}")
            self.output_fn(f"힌트: {quiz.hint}")

    def delete_quiz(self) -> None:
        if not self.quizzes:
            self.output_fn("삭제할 퀴즈가 없습니다.")
            return

        self.output_fn("")
        self.output_fn("삭제할 퀴즈 ID를 선택하세요.")
        for quiz in sorted(self.quizzes, key=lambda item: item.quiz_id):
            self.output_fn(f"{quiz.quiz_id}. {quiz.question}")

        max_quiz_id = max(quiz.quiz_id for quiz in self.quizzes)
        while True:
            quiz_id = self.prompt_int(
                "삭제할 퀴즈 ID: ",
                minimum=1,
                maximum=max_quiz_id,
            )
            target = self._find_quiz(quiz_id)
            if target is None:
                self.output_fn("해당 ID의 퀴즈가 없습니다. 다시 입력하세요.")
                continue
            break

        self.quizzes = [quiz for quiz in self.quizzes if quiz.quiz_id != quiz_id]
        self.save_state()
        self.output_fn(f"{quiz_id}번 퀴즈를 삭제했습니다.")

    def show_scores(self) -> None:
        self.output_fn("")
        self.output_fn(f"최고 점수: {self.best_score}")
        self.output_fn(f"총 플레이 횟수: {len(self.history)}")

        if not self.history:
            self.output_fn("아직 저장된 플레이 기록이 없습니다.")
            return

        self.output_fn("최근 5개 기록:")
        for entry in reversed(self.history[-RECENT_HISTORY_LIMIT:]):
            self.output_fn(
                " | ".join(
                    [
                        f"플레이 시각: {entry['played_at']}",
                        f"선택 문제 수: {entry['selected_count']}",
                        f"푼 문제 수: {entry['answered_count']}",
                        f"맞힌 문제 수: {entry['correct_count']}",
                        f"점수: {entry['score']}",
                        f"힌트 사용 수: {entry['hint_used_count']}",
                    ]
                )
            )

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
            self.output_fn("진행 상황을 저장하고 종료합니다.")
        else:
            self.output_fn("프로그램을 종료합니다.")

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
        played_at = datetime.now().astimezone().isoformat(timespec="seconds")
        self.best_score = max(self.best_score, total_score)
        self.history.append(
            {
                "played_at": played_at,
                "selected_count": selected_count,
                "answered_count": answered_count,
                "correct_count": correct_count,
                "score": total_score,
                "hint_used_count": hint_used_count,
            }
        )

    def _find_quiz(self, quiz_id: int) -> Quiz | None:
        for quiz in self.quizzes:
            if quiz.quiz_id == quiz_id:
                return quiz
        return None
