"""기본 퀴즈 데이터와 초기 state 생성을 담당하는 모듈.

프로그램을 처음 실행하거나 `state.json`이 손상되었을 때 복구 기준점으로
사용되는 데이터가 이 파일에 들어 있다. 즉 이 파일은 "아무 저장 정보도
없을 때 프로그램이 어디에서 출발할 것인가"를 정의하는 기준점이다.
"""

from __future__ import annotations

from game_constants import (
    STATE_KEY_BEST_SCORE,
    STATE_KEY_HISTORY,
    STATE_KEY_NEXT_QUIZ_ID,
    STATE_KEY_QUIZZES,
    STATE_KEY_VERSION,
    STATE_VERSION,
)
from quiz import Quiz


# 프로젝트 기본 제공 문제집.
# 사용자가 저장 파일 없이 시작해도 바로 게임을 해 볼 수 있도록 최소 문제 세트를 제공한다.
# 딕셔너리 형태로 두는 이유는, 이후 `Quiz.from_dict()`를 거치며 저장 파일과
# 동일한 복원 경로를 재사용하기 위해서다.
DEFAULT_QUIZ_DATA: list[dict[str, object]] = [
    {
        "id": 1,
        "question": "컴퓨터의 두뇌라고 자주 불리는 부품은 무엇일까요?",
        "choices": ["RAM", "CPU", "SSD", "GPU"],
        "answer": 2,
        "hint": "명령을 실행하고 계산을 수행하는 부품입니다.",
    },
    {
        "id": 2,
        "question": "원격 저장소의 새 변경 사항을 내려받아 현재 브랜치에 병합하는 명령어는 무엇일까요?",
        "choices": ["git clone", "git commit", "git pull", "git add"],
        "answer": 3,
        "hint": "가져오기와 병합을 한 번에 수행하는 명령어입니다.",
    },
    {
        "id": 3,
        "question": "RAM은 실행 중인 프로그램에 주로 무엇을 제공할까요?",
        "choices": ["임시 작업 메모리", "영구 백업 저장소", "네트워크 접속", "프린터 제어"],
        "answer": 1,
        "hint": "전원이 꺼지면 보통 내용이 사라집니다.",
    },
    {
        "id": 4,
        "question": "파이썬에서 순서가 있고 수정 가능한 여러 항목을 저장하는 자료형은 무엇일까요?",
        "choices": ["튜플", "리스트", "딕셔너리", "집합"],
        "answer": 2,
        "hint": "[1, 2, 3]처럼 대괄호를 사용합니다.",
    },
    {
        "id": 5,
        "question": "브라우저에서 웹 페이지를 불러올 때 흔히 사용하는 프로토콜은 무엇일까요?",
        "choices": ["FTP", "SSH", "HTTP", "SMTP"],
        "answer": 3,
        "hint": "웹사이트 주소에서 보안 버전인 HTTPS를 자주 볼 수 있습니다.",
    },
    {
        "id": 6,
        "question": "인터넷에서 DNS는 어떤 역할을 할까요?",
        "choices": ["배터리를 충전한다", "이름을 IP 주소로 변환한다", "이미지를 압축한다", "코드를 수정한다"],
        "answer": 2,
        "hint": "브라우저가 도메인 이름에 해당하는 서버를 찾도록 도와줍니다.",
    },
    {
        "id": 7,
        "question": "새 브랜치를 만들고 바로 그 브랜치로 이동하는 Git 명령어는 무엇일까요?",
        "choices": ["git status", "git branch main", "git switch -c feature", "git merge feature"],
        "answer": 3,
        "hint": "최근 방식의 명령어는 switch로 시작합니다.",
    },
    {
        "id": 8,
        "question": "파이썬에서 len('python')의 결과는 무엇일까요?",
        "choices": ["5", "6", "7", "8"],
        "answer": 2,
        "hint": "단어를 이루는 글자 수를 세어 보세요.",
    },
]


def get_default_quizzes() -> list[Quiz]:
    """기본 퀴즈 payload를 `Quiz` 객체 목록으로 변환한다.

    기본 데이터라고 해서 예외 없이 신뢰하지 않고, 실제 저장 파일을 읽을 때와
    같은 방식으로 `Quiz.from_dict()` 검증을 거쳐 객체를 만든다.
    """
    return [Quiz.from_dict(item) for item in DEFAULT_QUIZ_DATA]


def build_default_state() -> dict[str, object]:
    """첫 실행에 사용할 기본 상태 딕셔너리를 만든다.

    저장 구조의 키 이름은 `game_constants.py`에서 가져와, 코드 전체에서
    같은 이름을 일관되게 사용하도록 한다.
    """
    quizzes = get_default_quizzes()
    # `next_quiz_id`는 현재 존재하는 가장 큰 ID 다음 값이어야 하므로,
    # 기본 문제 수에 1을 더한 값으로 시작한다.
    return {
        STATE_KEY_VERSION: STATE_VERSION,
        STATE_KEY_NEXT_QUIZ_ID: len(quizzes) + 1,
        STATE_KEY_BEST_SCORE: 0,
        STATE_KEY_QUIZZES: [quiz.to_dict() for quiz in quizzes],
        STATE_KEY_HISTORY: [],
    }
