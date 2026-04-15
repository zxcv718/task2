"""퀴즈 추가, 목록 조회, 삭제를 담당하는 모듈.

`QuizGame`이 모든 세부 동작을 직접 들고 있지 않도록, 퀴즈 목록 관리 책임을
이 파일로 분리했다. 즉 이 모듈은 "퀴즈 데이터 집합을 수정하거나 보여 주는
관리자" 역할에 집중하고, 메뉴 제어와 저장 시점 결정은 상위 객체가 맡는다.
"""

from __future__ import annotations

from console_io import InputFn, OutputFn, prompt_int, prompt_text
from game_constants import (
    ADD_QUIZ_TITLE,
    ANSWER_NUMBER_PROMPT,
    CHOICE_PROMPTS,
    DELETE_QUIZ_PROMPT,
    DELETE_QUIZ_TITLE,
    HINT_PROMPT,
    NO_QUIZZES_TO_DELETE_MESSAGE,
    NO_QUIZZES_TO_LIST_MESSAGE,
    QUESTION_PROMPT,
    QUIZ_ADDED_MESSAGE_TEMPLATE,
    QUIZ_DELETED_MESSAGE_TEMPLATE,
    QUIZ_ID_NOT_FOUND_MESSAGE,
    QUIZ_LIST_TITLE,
    SECTION_DIVIDER,
)
from quiz import Quiz


class QuizCatalogManager:
    """퀴즈 컬렉션을 수정하거나 화면에 보여 주는 역할을 담당한다.

    상위 게임 객체는 이 클래스를 통해 퀴즈 목록 관리 기능을 위임받는다.
    이렇게 하면 카탈로그 관리 규칙이 한 군데에 모여, 읽는 사람이 책임 범위를
    더 쉽게 파악할 수 있다.
    """

    def __init__(self, input_fn: InputFn, output_fn: OutputFn) -> None:
        self.input_fn = input_fn
        self.output_fn = output_fn

    def add_quiz(self, quizzes: list[Quiz], next_quiz_id: int) -> int:
        """사용자 입력을 받아 새 퀴즈를 만들고 목록에 추가한다.

        반환값은 다음에 사용할 퀴즈 ID다. ID 계산 책임까지 여기서 처리해
        상위 객체는 "증가된 값만 받아 저장"하면 되도록 설계했다.
        """
        self.output_fn("")
        self.output_fn(ADD_QUIZ_TITLE)

        # 문제, 선택지, 정답, 힌트를 순서대로 묻는 단순한 흐름으로 구성해
        # 사용자와 평가자 모두 입력 절차를 직관적으로 이해할 수 있게 한다.
        question = prompt_text(self.input_fn, self.output_fn, QUESTION_PROMPT)
        # 선택지는 4개 고정 정책이므로 프롬프트도 상수 튜플로 관리한다.
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
        # 검증을 통과해 생성된 객체만 목록에 추가하므로, 이후 저장 시점에는
        # 이미 기본 형식이 보장된 상태라고 볼 수 있다.
        quizzes.append(quiz)
        self.output_fn(QUIZ_ADDED_MESSAGE_TEMPLATE.format(quiz_id=quiz.quiz_id))
        return next_quiz_id + 1

    def list_quizzes(self, quizzes: list[Quiz]) -> None:
        """현재 등록된 퀴즈를 화면용 순서 번호와 함께 출력한다.

        내부 저장 순서가 어떻든, 화면에는 ID 기준으로 정렬된 결과를
        `문제 1: 질문 내용`처럼 읽기 쉬운 형식으로 보여 준다. 목록 화면은
        퀴즈 존재 여부와 문제 구성을 확인하는 용도이므로, 내부 ID와
        정답 번호, 힌트는 여기서 노출하지 않는다.
        """
        if not quizzes:
            self.output_fn(NO_QUIZZES_TO_LIST_MESSAGE)
            return

        self.output_fn("")
        self.output_fn(QUIZ_LIST_TITLE)
        for display_index, quiz in enumerate(sorted(quizzes, key=lambda item: item.quiz_id), start=1):
            self.output_fn(SECTION_DIVIDER)
            self.output_fn(f"문제 {display_index}: {quiz.question}")
            for index, choice in enumerate(quiz.choices, start=1):
                self.output_fn(f"  {index}. {choice}")

    def delete_quiz(self, quizzes: list[Quiz]) -> bool:
        """사용자가 고른 퀴즈 ID를 삭제하고 성공 여부를 반환한다.

        삭제 성공 여부를 반환하는 이유는, 상위 객체가 "실제로 변경이 일어난
        경우에만 저장"하도록 제어하기 위해서다.
        """
        if not quizzes:
            self.output_fn(NO_QUIZZES_TO_DELETE_MESSAGE)
            return False

        self.output_fn("")
        self.output_fn(DELETE_QUIZ_TITLE)
        for quiz in sorted(quizzes, key=lambda item: item.quiz_id):
            self.output_fn(f"{quiz.quiz_id}. {quiz.question}")

        # ID가 중간에 비어 있을 수 있으므로, 먼저 입력 범위만 넓게 받고
        # 실제 존재 여부는 아래에서 한 번 더 확인한다.
        max_quiz_id = max(quiz.quiz_id for quiz in quizzes)
        while True:
            quiz_id = prompt_int(
                self.input_fn,
                self.output_fn,
                DELETE_QUIZ_PROMPT,
                minimum=1,
                maximum=max_quiz_id,
            )
            target_index = None
            for index, quiz in enumerate(quizzes):
                if quiz.quiz_id == quiz_id:
                    target_index = index
                    break

            if target_index is None:
                self.output_fn(QUIZ_ID_NOT_FOUND_MESSAGE)
                continue
            break

        quizzes.pop(target_index)
        self.output_fn(QUIZ_DELETED_MESSAGE_TEMPLATE.format(quiz_id=quiz_id))
        return True
