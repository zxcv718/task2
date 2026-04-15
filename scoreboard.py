"""최고 점수와 플레이 히스토리 화면 출력을 담당하는 모듈.

이 파일은 "점수판을 어떻게 보여 줄 것인가"에만 집중한다. history 기록을
만드는 책임은 상위 게임 로직과 `HistoryEntry` 모델이 맡고, 이 모듈은
이미 만들어진 데이터를 콘솔에서 읽기 좋게 출력하는 역할만 담당한다.
"""

from __future__ import annotations

from collections.abc import Sequence

from console_io import OutputFn
from game_constants import (
    ANSWERED_COUNT_LABEL,
    CORRECT_COUNT_LABEL,
    HINT_USED_COUNT_LABEL,
    NO_PLAY_HISTORY_MESSAGE,
    PLAY_COUNT_LABEL,
    PLAYED_AT_LABEL,
    RECENT_HISTORY_LIMIT,
    RECENT_HISTORY_TITLE,
    SCORE_LABEL,
    SELECTED_COUNT_LABEL,
    SUMMARY_BEST_SCORE_LABEL,
)
from history_entry import HistoryEntry


def show_scores(
    output_fn: OutputFn,
    *,
    best_score: int,
    history: Sequence[HistoryEntry],
) -> None:
    """최고 점수와 최근 플레이 기록을 화면에 출력한다.

    이 함수는 저장된 기록 전체를 보여 주기보다, 최근 기록 일부만 추려서
    콘솔 화면에서 한눈에 읽기 좋게 정리하는 역할을 한다.
    """
    output_fn("")
    output_fn(f"{SUMMARY_BEST_SCORE_LABEL}: {best_score}")
    output_fn(f"{PLAY_COUNT_LABEL}: {len(history)}")

    if not history:
        output_fn(NO_PLAY_HISTORY_MESSAGE)
        return

    output_fn(RECENT_HISTORY_TITLE)
    # 최근 기록이 아래쪽에 쌓이므로, 화면에는 뒤에서부터 역순으로 보여 준다.
    recent_history = list(history)[-RECENT_HISTORY_LIMIT:]
    for entry in reversed(recent_history):
        # 한 줄 요약 형식으로 보여 주어 콘솔 환경에서도 정보 밀도를 유지한다.
        output_fn(
            " | ".join(
                [
                    f"{PLAYED_AT_LABEL}: {entry.played_at}",
                    f"{SELECTED_COUNT_LABEL}: {entry.selected_count}",
                    f"{ANSWERED_COUNT_LABEL}: {entry.answered_count}",
                    f"{CORRECT_COUNT_LABEL}: {entry.correct_count}",
                    f"{SCORE_LABEL}: {entry.score}",
                    f"{HINT_USED_COUNT_LABEL}: {entry.hint_used_count}",
                ]
            )
        )
