from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Quiz:
    quiz_id: int
    question: str
    choices: list[str]
    answer: int
    hint: str

    def __post_init__(self) -> None:
        if not isinstance(self.quiz_id, int) or self.quiz_id < 1:
            raise ValueError("quiz_id must be a positive integer.")

        if not isinstance(self.question, str) or not self.question.strip():
            raise ValueError("question must be a non-empty string.")

        if not isinstance(self.choices, list) or len(self.choices) != 4:
            raise ValueError("choices must contain exactly four items.")

        cleaned_choices: list[str] = []
        for choice in self.choices:
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError("each choice must be a non-empty string.")
            cleaned_choices.append(choice.strip())

        if not isinstance(self.answer, int) or not 1 <= self.answer <= 4:
            raise ValueError("answer must be an integer from 1 to 4.")

        if not isinstance(self.hint, str) or not self.hint.strip():
            raise ValueError("hint must be a non-empty string.")

        self.question = self.question.strip()
        self.choices = cleaned_choices
        self.hint = self.hint.strip()

    def display(self) -> str:
        lines = [self.question]
        for index, choice in enumerate(self.choices, start=1):
            lines.append(f"{index}. {choice}")
        return "\n".join(lines)

    def is_correct(self, user_answer: int) -> bool:
        return user_answer == self.answer

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.quiz_id,
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Quiz":
        if not isinstance(data, dict):
            raise ValueError("Quiz data must be a dictionary.")

        quiz_id = data["id"]
        question = data["question"]
        choices = data["choices"]
        answer = data["answer"]
        hint = data["hint"]

        if not isinstance(quiz_id, int):
            raise ValueError("Quiz id must be an integer.")
        if not isinstance(question, str):
            raise ValueError("Quiz question must be a string.")
        if not isinstance(choices, list):
            raise ValueError("Quiz choices must be a list.")
        if not isinstance(answer, int):
            raise ValueError("Quiz answer must be an integer.")
        if not isinstance(hint, str):
            raise ValueError("Quiz hint must be a string.")

        return cls(
            quiz_id=quiz_id,
            question=question,
            choices=choices,
            answer=answer,
            hint=hint,
        )
