from __future__ import annotations

from console_io import InputFn, OutputFn, prompt_int, prompt_text
from game_constants import (
    ADD_QUIZ_TITLE,
    ANSWER_LABEL,
    ANSWER_NUMBER_PROMPT,
    CHOICE_PROMPTS,
    DELETE_QUIZ_PROMPT,
    DELETE_QUIZ_TITLE,
    HINT_LABEL,
    HINT_PROMPT,
    NO_QUIZZES_TO_DELETE_MESSAGE,
    NO_QUIZZES_TO_LIST_MESSAGE,
    QUESTION_LABEL,
    QUESTION_PROMPT,
    QUIZ_ADDED_MESSAGE_TEMPLATE,
    QUIZ_DELETED_MESSAGE_TEMPLATE,
    QUIZ_ID_LABEL,
    QUIZ_ID_NOT_FOUND_MESSAGE,
    QUIZ_LIST_TITLE,
    SECTION_DIVIDER,
)
from quiz import Quiz


class QuizCatalogManager:
    def __init__(self, input_fn: InputFn, output_fn: OutputFn) -> None:
        self.input_fn = input_fn
        self.output_fn = output_fn

    def add_quiz(self, quizzes: list[Quiz], next_quiz_id: int) -> int:
        self.output_fn("")
        self.output_fn(ADD_QUIZ_TITLE)

        question = prompt_text(self.input_fn, self.output_fn, QUESTION_PROMPT)
        choices = [prompt_text(self.input_fn, self.output_fn, prompt) for prompt in CHOICE_PROMPTS]
        answer = prompt_int(
            self.input_fn,
            self.output_fn,
            ANSWER_NUMBER_PROMPT,
            minimum=1,
            maximum=4,
        )
        hint = prompt_text(self.input_fn, self.output_fn, HINT_PROMPT)

        quiz = Quiz(
            quiz_id=next_quiz_id,
            question=question,
            choices=choices,
            answer=answer,
            hint=hint,
        )
        quizzes.append(quiz)
        self.output_fn(QUIZ_ADDED_MESSAGE_TEMPLATE.format(quiz_id=quiz.quiz_id))
        return next_quiz_id + 1

    def list_quizzes(self, quizzes: list[Quiz]) -> None:
        if not quizzes:
            self.output_fn(NO_QUIZZES_TO_LIST_MESSAGE)
            return

        self.output_fn("")
        self.output_fn(QUIZ_LIST_TITLE)
        for quiz in sorted(quizzes, key=lambda item: item.quiz_id):
            self.output_fn(SECTION_DIVIDER)
            self.output_fn(f"{QUIZ_ID_LABEL}: {quiz.quiz_id}")
            self.output_fn(f"{QUESTION_LABEL}: {quiz.question}")
            for index, choice in enumerate(quiz.choices, start=1):
                self.output_fn(f"  {index}. {choice}")
            self.output_fn(f"{ANSWER_LABEL}: {quiz.answer}")
            self.output_fn(f"{HINT_LABEL}: {quiz.hint}")

    def delete_quiz(self, quizzes: list[Quiz]) -> bool:
        if not quizzes:
            self.output_fn(NO_QUIZZES_TO_DELETE_MESSAGE)
            return False

        self.output_fn("")
        self.output_fn(DELETE_QUIZ_TITLE)
        for quiz in sorted(quizzes, key=lambda item: item.quiz_id):
            self.output_fn(f"{quiz.quiz_id}. {quiz.question}")

        max_quiz_id = max(quiz.quiz_id for quiz in quizzes)
        while True:
            quiz_id = prompt_int(
                self.input_fn,
                self.output_fn,
                DELETE_QUIZ_PROMPT,
                minimum=1,
                maximum=max_quiz_id,
            )
            target = self._find_quiz(quizzes, quiz_id)
            if target is None:
                self.output_fn(QUIZ_ID_NOT_FOUND_MESSAGE)
                continue
            break

        quizzes[:] = [quiz for quiz in quizzes if quiz.quiz_id != quiz_id]
        self.output_fn(QUIZ_DELETED_MESSAGE_TEMPLATE.format(quiz_id=quiz_id))
        return True

    def _find_quiz(self, quizzes: list[Quiz], quiz_id: int) -> Quiz | None:
        for quiz in quizzes:
            if quiz.quiz_id == quiz_id:
                return quiz
        return None
