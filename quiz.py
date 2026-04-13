"""퀴즈 한 문제를 표현하는 데이터 모델 모듈.

평가자가 이 파일만 봐도 "퀴즈 1개가 어떤 정보로 구성되는지"와
"생성 시 어떤 유효성 검사를 하는지"를 이해할 수 있도록 작성한다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Quiz:
    """객관식 퀴즈 1문제를 표현한다.

    속성은 문제 ID, 문제 문장, 선택지 4개, 정답 번호, 힌트로 구성된다.
    `slots=True`를 사용해 고정된 속성만 가지도록 하여 단순한 모델 역할에
    집중하게 한다.
    """

    quiz_id: int
    question: str
    choices: list[str]
    answer: int
    hint: str

    def __post_init__(self) -> None:
        """생성 직후 퀴즈 데이터의 기본 형식과 범위를 검사한다.

        이 단계에서 잘못된 데이터를 빨리 막아 두면, 이후 저장/출제/채점
        흐름에서 별도의 방어 코드를 반복해서 쓰지 않아도 된다.
        """
        if not isinstance(self.quiz_id, int) or self.quiz_id < 1:
            raise ValueError("quiz_id must be a positive integer.")

        if not isinstance(self.question, str) or not self.question.strip():
            raise ValueError("question must be a non-empty string.")

        if not isinstance(self.choices, list) or len(self.choices) != 4:
            raise ValueError("choices must contain exactly four items.")

        cleaned_choices: list[str] = []
        for choice in self.choices:
            # 선택지는 화면에 그대로 출력되므로, 공백만 있는 값은 허용하지 않는다.
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError("each choice must be a non-empty string.")
            cleaned_choices.append(choice.strip())

        if not isinstance(self.answer, int) or not 1 <= self.answer <= 4:
            raise ValueError("answer must be an integer from 1 to 4.")

        if not isinstance(self.hint, str) or not self.hint.strip():
            raise ValueError("hint must be a non-empty string.")

        # 사용자가 앞뒤 공백을 섞어 입력해도 저장되는 값은 정돈된 형태가 되도록 맞춘다.
        self.question = self.question.strip()
        self.choices = cleaned_choices
        self.hint = self.hint.strip()

    def display(self) -> str:
        """콘솔 화면에 그대로 출력할 수 있는 문제 문자열을 만든다."""
        lines = [self.question]
        for index, choice in enumerate(self.choices, start=1):
            lines.append(f"{index}. {choice}")
        return "\n".join(lines)

    def is_correct(self, user_answer: int) -> bool:
        """사용자 입력 번호가 정답 번호와 같은지 판정한다."""
        return user_answer == self.answer

    def to_dict(self) -> dict[str, object]:
        """JSON 저장이 가능한 딕셔너리 형태로 변환한다."""
        return {
            "id": self.quiz_id,
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Quiz":
        """딕셔너리 payload를 읽어 `Quiz` 객체로 복원한다.

        저장 파일이나 기본 데이터에서 읽은 값을 바로 신뢰하지 않고,
        최소한의 타입 검사를 거친 뒤 생성자로 넘긴다.
        """
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
