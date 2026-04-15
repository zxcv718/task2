"""플레이 히스토리 1건의 생성, 검증, 직렬화를 담당하는 모듈.

history 항목 스키마를 여러 파일이 따로 알지 않도록, 이 모듈이 단일
소유권을 가진다. 저장소 계층은 `from_dict()`와 `to_dict()`만 사용하고,
상위 로직은 `HistoryEntry` 객체 자체를 다루면 된다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from game_constants import (
    HISTORY_ANSWERED_GT_SELECTED_ERROR,
    HISTORY_CORRECT_GT_ANSWERED_ERROR,
    HISTORY_ENTRY_DICT_ERROR,
    HISTORY_HINT_GT_ANSWERED_ERROR,
    HISTORY_KEY_ANSWERED_COUNT,
    HISTORY_KEY_CORRECT_COUNT,
    HISTORY_KEY_HINT_USED_COUNT,
    HISTORY_KEY_PLAYED_AT,
    HISTORY_KEY_SCORE,
    HISTORY_KEY_SELECTED_COUNT,
    HISTORY_NEGATIVE_VALUES_ERROR,
)

PLAYED_AT_FORMAT = "%Y년 %m월 %d일 %H시 %M분 %S초"


@dataclass(slots=True)
class HistoryEntry:
    """퀴즈 플레이 1회의 결과를 표현한다."""

    played_at: str
    selected_count: int
    answered_count: int
    correct_count: int
    score: int
    hint_used_count: int

    def __post_init__(self) -> None:
        """생성 직후 타입과 값 범위를 검증한다."""
        self.played_at = self._normalize_played_at(
            self.played_at,
            field_name=HISTORY_KEY_PLAYED_AT,
        )
        self.selected_count = self._require_int(
            self.selected_count,
            field_name=HISTORY_KEY_SELECTED_COUNT,
        )
        self.answered_count = self._require_int(
            self.answered_count,
            field_name=HISTORY_KEY_ANSWERED_COUNT,
        )
        self.correct_count = self._require_int(
            self.correct_count,
            field_name=HISTORY_KEY_CORRECT_COUNT,
        )
        self.score = self._require_int(
            self.score,
            field_name=HISTORY_KEY_SCORE,
        )
        self.hint_used_count = self._require_int(
            self.hint_used_count,
            field_name=HISTORY_KEY_HINT_USED_COUNT,
        )

        if (
            self.selected_count < 0
            or self.answered_count < 0
            or self.correct_count < 0
            or self.score < 0
            or self.hint_used_count < 0
        ):
            raise ValueError(HISTORY_NEGATIVE_VALUES_ERROR)
        if self.answered_count > self.selected_count:
            raise ValueError(HISTORY_ANSWERED_GT_SELECTED_ERROR)
        if self.correct_count > self.answered_count:
            raise ValueError(HISTORY_CORRECT_GT_ANSWERED_ERROR)
        if self.hint_used_count > self.answered_count:
            raise ValueError(HISTORY_HINT_GT_ANSWERED_ERROR)

    @classmethod
    def create_now(
        cls,
        *,
        selected_count: int,
        answered_count: int,
        correct_count: int,
        score: int,
        hint_used_count: int,
    ) -> "HistoryEntry":
        """현재 시각을 포함한 새 history 엔트리를 만든다."""
        return cls(
            played_at=cls._format_datetime(datetime.now().astimezone()),
            selected_count=selected_count,
            answered_count=answered_count,
            correct_count=correct_count,
            score=score,
            hint_used_count=hint_used_count,
        )

    @classmethod
    def from_dict(cls, data: object) -> "HistoryEntry":
        """저장 payload를 읽어 `HistoryEntry`로 복원한다."""
        if not isinstance(data, dict):
            raise ValueError(HISTORY_ENTRY_DICT_ERROR)

        return cls(
            played_at=data[HISTORY_KEY_PLAYED_AT],
            selected_count=data[HISTORY_KEY_SELECTED_COUNT],
            answered_count=data[HISTORY_KEY_ANSWERED_COUNT],
            correct_count=data[HISTORY_KEY_CORRECT_COUNT],
            score=data[HISTORY_KEY_SCORE],
            hint_used_count=data[HISTORY_KEY_HINT_USED_COUNT],
        )

    def to_dict(self) -> dict[str, object]:
        """JSON 저장 가능한 딕셔너리 형태로 변환한다."""
        return {
            HISTORY_KEY_PLAYED_AT: self.played_at,
            HISTORY_KEY_SELECTED_COUNT: self.selected_count,
            HISTORY_KEY_ANSWERED_COUNT: self.answered_count,
            HISTORY_KEY_CORRECT_COUNT: self.correct_count,
            HISTORY_KEY_SCORE: self.score,
            HISTORY_KEY_HINT_USED_COUNT: self.hint_used_count,
        }

    @staticmethod
    def _require_int(value: object, *, field_name: str) -> int:
        """bool/float/문자열 숫자를 배제한 진짜 int만 허용한다."""
        if type(value) is not int:
            raise ValueError(f"{field_name}는 정수여야 합니다.")
        return value

    @staticmethod
    def _require_non_empty_string(value: object, *, field_name: str) -> str:
        """표시용 문자열 필드가 비어 있지 않은지 확인한다."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name}는 비어 있지 않은 문자열이어야 합니다.")
        return value.strip()

    @classmethod
    def _normalize_played_at(cls, value: object, *, field_name: str) -> str:
        """예전 ISO 문자열은 읽기 쉬운 형식으로 바꾸고, 그 외 문자열은 유지한다."""
        played_at = cls._require_non_empty_string(value, field_name=field_name)
        try:
            parsed = datetime.fromisoformat(played_at)
        except ValueError:
            return played_at
        return cls._format_datetime(parsed)

    @staticmethod
    def _format_datetime(value: datetime) -> str:
        """플레이 시각을 콘솔과 저장 파일에서 읽기 쉬운 형식으로 만든다."""
        return value.strftime(PLAYED_AT_FORMAT)
