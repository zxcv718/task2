from __future__ import annotations

from console_io import InputFn, OutputFn, prompt_int, prompt_text
from quiz import Quiz


class QuizCatalogManager:
    def __init__(self, input_fn: InputFn, output_fn: OutputFn) -> None:
        self.input_fn = input_fn
        self.output_fn = output_fn

    def add_quiz(self, quizzes: list[Quiz], next_quiz_id: int) -> int:
        self.output_fn("")
        self.output_fn("새 퀴즈 추가")

        question = prompt_text(self.input_fn, self.output_fn, "문제: ")
        choices = [
            prompt_text(self.input_fn, self.output_fn, "선택지 1: "),
            prompt_text(self.input_fn, self.output_fn, "선택지 2: "),
            prompt_text(self.input_fn, self.output_fn, "선택지 3: "),
            prompt_text(self.input_fn, self.output_fn, "선택지 4: "),
        ]
        answer = prompt_int(
            self.input_fn,
            self.output_fn,
            "정답 번호를 입력하세요 (1-4): ",
            minimum=1,
            maximum=4,
        )
        hint = prompt_text(self.input_fn, self.output_fn, "힌트: ")

        quiz = Quiz(
            quiz_id=next_quiz_id,
            question=question,
            choices=choices,
            answer=answer,
            hint=hint,
        )
        quizzes.append(quiz)
        self.output_fn(f"{quiz.quiz_id}번 퀴즈가 추가되었습니다.")
        return next_quiz_id + 1

    def list_quizzes(self, quizzes: list[Quiz]) -> None:
        if not quizzes:
            self.output_fn("표시할 퀴즈가 없습니다.")
            return

        self.output_fn("")
        self.output_fn("저장된 퀴즈 목록")
        for quiz in sorted(quizzes, key=lambda item: item.quiz_id):
            self.output_fn("-" * 40)
            self.output_fn(f"ID: {quiz.quiz_id}")
            self.output_fn(f"문제: {quiz.question}")
            for index, choice in enumerate(quiz.choices, start=1):
                self.output_fn(f"  {index}. {choice}")
            self.output_fn(f"정답 번호: {quiz.answer}")
            self.output_fn(f"힌트: {quiz.hint}")

    def delete_quiz(self, quizzes: list[Quiz]) -> bool:
        if not quizzes:
            self.output_fn("삭제할 퀴즈가 없습니다.")
            return False

        self.output_fn("")
        self.output_fn("삭제할 퀴즈 ID를 선택하세요.")
        for quiz in sorted(quizzes, key=lambda item: item.quiz_id):
            self.output_fn(f"{quiz.quiz_id}. {quiz.question}")

        max_quiz_id = max(quiz.quiz_id for quiz in quizzes)
        while True:
            quiz_id = prompt_int(
                self.input_fn,
                self.output_fn,
                "삭제할 퀴즈 ID: ",
                minimum=1,
                maximum=max_quiz_id,
            )
            target = self._find_quiz(quizzes, quiz_id)
            if target is None:
                self.output_fn("해당 ID의 퀴즈가 없습니다. 다시 입력하세요.")
                continue
            break

        quizzes[:] = [quiz for quiz in quizzes if quiz.quiz_id != quiz_id]
        self.output_fn(f"{quiz_id}번 퀴즈를 삭제했습니다.")
        return True

    def _find_quiz(self, quizzes: list[Quiz], quiz_id: int) -> Quiz | None:
        for quiz in quizzes:
            if quiz.quiz_id == quiz_id:
                return quiz
        return None
