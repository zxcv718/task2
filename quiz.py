"""퀴즈 한 문제를 표현하는 데이터 모델 모듈.

평가자가 이 파일만 봐도 "퀴즈 1개가 어떤 정보로 구성되는지"와
"생성 시 어떤 유효성 검사를 하는지"를 이해할 수 있도록 작성한다.
게임의 나머지 부분은 이 객체를 신뢰하고 사용하므로, 데이터 모델 단계에서
기본 정합성을 보장하는 것이 중요하다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Quiz:
    """객관식 퀴즈 1문제를 표현한다.

    속성은 문제 ID, 문제 문장, 선택지 4개, 정답 번호, 힌트로 구성된다.
    `slots=True`를 사용해 고정된 속성만 가지도록 하여 단순한 모델 역할에
    집중하게 한다. 즉 이 클래스는 "가벼운 데이터 객체이면서도, 생성 순간에
    기본 규칙을 지키는지 검사하는 모델"이라고 볼 수 있다.
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
        # 퀴즈 ID는 저장 파일과 삭제 기능에서 식별자로 쓰이므로 1 이상의 정수만 허용한다.
        if not isinstance(self.quiz_id, int) or self.quiz_id < 1:
            raise ValueError("quiz_id must be a positive integer.")

        # 문제 문장은 화면에 출력되므로 비어 있거나 공백뿐인 값이면 안 된다.
        if not isinstance(self.question, str) or not self.question.strip():
            raise ValueError("question must be a non-empty string.")

        # 현재 게임은 4지선다형으로 고정되어 있으므로 선택지 개수를 정확히 맞춘다.
        if not isinstance(self.choices, list) or len(self.choices) != 4:
            raise ValueError("choices must contain exactly four items.")

        cleaned_choices: list[str] = []
        for choice in self.choices:
            # 선택지는 화면에 그대로 출력되므로, 공백만 있는 값은 허용하지 않는다.
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError("each choice must be a non-empty string.")
            cleaned_choices.append(choice.strip())

        # 정답 번호는 사람이 보는 번호 체계와 맞추기 위해 1~4 범위로 유지한다.
        if not isinstance(self.answer, int) or not 1 <= self.answer <= 4:
            raise ValueError("answer must be an integer from 1 to 4.")

        # 힌트 역시 실제 플레이 중 그대로 노출되므로 비어 있지 않아야 한다.
        if not isinstance(self.hint, str) or not self.hint.strip():
            raise ValueError("hint must be a non-empty string.")

        # 사용자가 앞뒤 공백을 섞어 입력해도 저장되는 값은 정돈된 형태가 되도록 맞춘다.
        self.question = self.question.strip()
        self.choices = cleaned_choices
        self.hint = self.hint.strip()

    def display(self) -> str:
        """콘솔 화면에 그대로 출력할 수 있는 문제 문자열을 만든다.

        출력 형식을 객체 안에서 책임지게 하면, 퀴즈를 보여 주는 쪽에서는
        줄바꿈 규칙을 매번 다시 조합하지 않아도 된다.
        """
        lines = [self.question]
        for index, choice in enumerate(self.choices, start=1):
            lines.append(f"{index}. {choice}")
        return "\n".join(lines)

    def is_correct(self, user_answer: int) -> bool:
        """사용자 입력 번호가 정답 번호와 같은지 판정한다.

        채점 기준을 한 군데로 모아 두면, 상위 로직은 "점수 계산과 결과 처리"에
        집중할 수 있고 정답 비교 규칙이 흩어지지 않는다.
        """
        return user_answer == self.answer

    def to_dict(self) -> dict[str, object]:
        """JSON 저장이 가능한 딕셔너리 형태로 변환한다.

        파일에는 파이썬 객체를 그대로 저장할 수 없으므로, 직렬화 가능한 기본
        자료형 구조로 바꿔 주어야 한다.
        """
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

        # 키를 먼저 명시적으로 꺼내 두면, 누락 시 즉시 실패하고 어떤 필드가
        # 필요한지도 코드에서 바로 드러난다.
        quiz_id = data["id"]
        question = data["question"]
        choices = data["choices"]
        answer = data["answer"]
        hint = data["hint"]

        # 여기서는 "대략적인 타입"만 먼저 확인하고, 더 세부적인 규칙은
        # 생성자와 __post_init__에 맡겨 검증 책임을 한 번 더 모은다.
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
