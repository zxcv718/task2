"""state.json 로드/저장과 검증을 담당하는 모듈.

파일 입출력과 데이터 구조 검증을 한 곳에 모아 두면, 게임 로직은
"언제 저장할지"에만 집중할 수 있고 저장 포맷 변경도 관리하기 쉬워진다.
또한 파일이 없거나 깨졌을 때의 복구 정책을 이 모듈에 모아 둘 수 있어,
상위 로직이 예외 처리로 복잡해지는 것을 막는다.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from console_io import OutputFn
from default_data import build_default_state
from game_constants import (
    BEST_SCORE_NEGATIVE_ERROR,
    HISTORY_LIST_ERROR,
    NEXT_QUIZ_ID_MIN_ERROR,
    QUIZZES_LIST_ERROR,
    STATE_DATA_DICT_ERROR,
    STATE_FILE_MISSING_MESSAGE,
    STATE_FILE_RECOVERY_MESSAGE_TEMPLATE,
    STATE_KEY_BEST_SCORE,
    STATE_KEY_HISTORY,
    STATE_KEY_NEXT_QUIZ_ID,
    STATE_KEY_QUIZZES,
    STATE_KEY_VERSION,
    STATE_SAVE_FAILED_MESSAGE_TEMPLATE,
    STATE_VERSION,
    UNSUPPORTED_STATE_VERSION_ERROR_TEMPLATE,
)
from history_entry import HistoryEntry
from quiz import Quiz


@dataclass(slots=True)
class GameState:
    """메모리 위에서 다루는 게임 상태 묶음.

    JSON 파일을 바로 여기저기서 다루기보다, 검증을 거친 뒤 이 객체 형태로
    올려 두면 나머지 코드가 더 단순한 파이썬 객체만 다루게 된다.
    """

    quizzes: list[Quiz]
    best_score: int
    history: list[HistoryEntry]
    next_quiz_id: int


class StateStore:
    """`state.json`을 읽고 쓰는 저장소 객체.

    이 객체는 파일 시스템과 JSON 포맷을 상대하는 계층이다. `QuizGame`은
    이 클래스를 통해 상태를 읽고 저장하며, 파일의 구체적인 형식은 몰라도 된다.
    """

    def __init__(self, state_path: str | Path, output_fn: OutputFn) -> None:
        self.state_path = Path(state_path)
        self.output_fn = output_fn

    def load_state(self) -> GameState:
        """저장 파일을 읽어 `GameState`로 복원한다.

        파일이 없거나 손상된 경우에도 프로그램이 시작 가능해야 하므로,
        기본 상태로 복구하는 흐름을 함께 제공한다.
        """
        # 첫 실행처럼 파일이 아예 없을 수 있으므로, 존재 여부를 먼저 확인한다.
        if not self.state_path.exists():
            self.output_fn(STATE_FILE_MISSING_MESSAGE)
            state = self._parse_state(build_default_state())
            self.save_state(state)
            return state

        try:
            # 텍스트 모드 + UTF-8로 열어 JSON 문자열을 읽어 온다.
            with self.state_path.open("r", encoding="utf-8") as file:
                raw_state = json.load(file)
            # JSON 문법상 읽기에 성공해도 구조가 틀릴 수 있으므로 별도 검증을 거친다.
            return self._parse_state(raw_state)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            # 파일이 깨졌더라도 프로그램 전체가 멈추지 않도록 기본 상태로 복구한다.
            self.output_fn(STATE_FILE_RECOVERY_MESSAGE_TEMPLATE.format(error=error))
            state = self._parse_state(build_default_state())
            self.save_state(state)
            return state

    def save_state(self, state: GameState) -> bool:
        """현재 메모리 상태를 JSON 파일에 저장하고 성공 여부를 반환한다.

        메모리 속 객체를 바로 저장할 수는 없으므로, JSON으로 직렬화 가능한
        기본 자료형 구조로 먼저 바꾼 뒤 파일에 기록한다.
        """
        data = {
            STATE_KEY_VERSION: STATE_VERSION,
            STATE_KEY_NEXT_QUIZ_ID: state.next_quiz_id,
            STATE_KEY_BEST_SCORE: state.best_score,
            STATE_KEY_QUIZZES: [quiz.to_dict() for quiz in state.quizzes],
            STATE_KEY_HISTORY: [entry.to_dict() for entry in state.history],
        }

        try:
            # 상위 폴더가 없어도 저장이 가능하도록 먼저 디렉터리를 보장한다.
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with self.state_path.open("w", encoding="utf-8") as file:
                # ensure_ascii=False를 사용해 한글이 유니코드 이스케이프 대신
                # 실제 문자로 저장되도록 한다.
                json.dump(data, file, ensure_ascii=False, indent=2)
                # 마지막 줄바꿈을 추가해 일반 텍스트 파일처럼 읽기 편하게 만든다.
                file.write("\n")
        except OSError as error:
            self.output_fn(STATE_SAVE_FAILED_MESSAGE_TEMPLATE.format(error=error))
            return False

        return True

    def _parse_state(self, data: object) -> GameState:
        """읽어 온 payload를 검증하고 `GameState`로 변환한다.

        이 단계는 "JSON으로 읽을 수 있음"과 "우리 프로그램이 이해할 수 있는
        정상 state 구조임"을 구분하는 검증 단계다.
        """
        if not isinstance(data, dict):
            raise ValueError(STATE_DATA_DICT_ERROR)

        version = self._require_int(data[STATE_KEY_VERSION], field_name=STATE_KEY_VERSION)
        # 저장 포맷 버전이 다르면 키 구조나 의미가 달라졌을 수 있으므로 거부한다.
        if version != STATE_VERSION:
            raise ValueError(UNSUPPORTED_STATE_VERSION_ERROR_TEMPLATE.format(version=version))

        quizzes_raw = data[STATE_KEY_QUIZZES]
        best_score = self._require_int(data[STATE_KEY_BEST_SCORE], field_name=STATE_KEY_BEST_SCORE)
        history_raw = data[STATE_KEY_HISTORY]
        next_quiz_id = self._require_int(
            data[STATE_KEY_NEXT_QUIZ_ID],
            field_name=STATE_KEY_NEXT_QUIZ_ID,
        )

        # 기본적인 수치 조건과 컨테이너 타입을 먼저 검사해 이후 변환 로직의
        # 전제를 안전하게 만든다.
        if best_score < 0:
            raise ValueError(BEST_SCORE_NEGATIVE_ERROR)
        if next_quiz_id < 1:
            raise ValueError(NEXT_QUIZ_ID_MIN_ERROR)
        if not isinstance(quizzes_raw, list):
            raise ValueError(QUIZZES_LIST_ERROR)
        if not isinstance(history_raw, list):
            raise ValueError(HISTORY_LIST_ERROR)

        # 각 항목도 개별 검증을 거쳐 "신뢰 가능한 객체/기록"으로 바꾼다.
        quizzes = [Quiz.from_dict(item) for item in quizzes_raw]
        history = [HistoryEntry.from_dict(item) for item in history_raw]
        highest_quiz_id = max((quiz.quiz_id for quiz in quizzes), default=0)

        return GameState(
            quizzes=quizzes,
            best_score=best_score,
            history=history,
            # 저장 파일의 next_quiz_id가 잘못되어도 기존 최대 ID보다 작아지지 않게 보정한다.
            next_quiz_id=max(next_quiz_id, highest_quiz_id + 1),
        )

    def _require_int(self, value: object, *, field_name: str) -> int:
        """bool/float/문자열 숫자를 배제한 "진짜 int"만 허용한다."""
        if type(value) is not int:
            raise ValueError(f"{field_name}는 정수여야 합니다.")
        return value
