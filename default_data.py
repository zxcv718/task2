from __future__ import annotations

from quiz import Quiz


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
    return [Quiz.from_dict(item) for item in DEFAULT_QUIZ_DATA]


def build_default_state() -> dict[str, object]:
    quizzes = get_default_quizzes()
    return {
        "version": 1,
        "next_quiz_id": len(quizzes) + 1,
        "best_score": 0,
        "quizzes": [quiz.to_dict() for quiz in quizzes],
        "history": [],
    }
