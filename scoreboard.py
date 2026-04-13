"""최고 점수와 플레이 히스토리 처리에 관한 모듈.

이 파일은 "점수판"과 관련된 책임만 모아 둔 곳이다. 퀴즈를 풀 때 생성되는
history 기록 형식과, 그 기록을 화면에 어떻게 보여 줄지 함께 관리한다.
즉 게임 진행 로직은 점수를 "계산"하고, 이 모듈은 그 결과를 "기록하고
표시하는 방식"을 맡는다.
"""

from __future__ import annotations

from datetime import datetime

from console_io import OutputFn
from game_constants import (
    ANSWERED_COUNT_LABEL,
    CORRECT_COUNT_LABEL,
    HISTORY_KEY_ANSWERED_COUNT,
    HISTORY_KEY_CORRECT_COUNT,
    HISTORY_KEY_HINT_USED_COUNT,
    HISTORY_KEY_PLAYED_AT,
    HISTORY_KEY_SCORE,
    HISTORY_KEY_SELECTED_COUNT,
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


def record_history(
    history: list[dict[str, object]],
    best_score: int,
    *,
    selected_count: int,
    answered_count: int,
    correct_count: int,
    total_score: int,
    hint_used_count: int,
) -> int:
    """현재 플레이 결과를 history에 추가하고 갱신된 최고 점수를 반환한다.

    history는 나중에 점수 화면에서 그대로 읽어 보여 주는 자료이므로, 여기서
    기록 형식을 일관되게 만드는 것이 중요하다.
    """
    # 시각은 로컬 타임존 정보를 포함한 ISO 형식으로 저장해, 나중에 사람이
    # 읽기 쉽고 다른 시스템에서도 해석하기 쉬운 문자열로 남긴다.
    played_at = datetime.now().astimezone().isoformat(timespec="seconds")
    history.append(
        {
            "played_at": played_at,
            "selected_count": selected_count,
            "answered_count": answered_count,
            "correct_count": correct_count,
            "score": total_score,
            "hint_used_count": hint_used_count,
        }
    )
    # 최고 점수는 기존 값과 이번 점수 중 큰 값을 유지한다.
    return max(best_score, total_score)


def show_scores(
    output_fn: OutputFn,
    *,
    best_score: int,
    history: list[dict[str, object]],
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
    for entry in reversed(history[-RECENT_HISTORY_LIMIT:]):
        # 한 줄 요약 형식으로 보여 주어 콘솔 환경에서도 정보 밀도를 유지한다.
        output_fn(
            " | ".join(
                [
                    f"{PLAYED_AT_LABEL}: {entry[HISTORY_KEY_PLAYED_AT]}",
                    f"{SELECTED_COUNT_LABEL}: {entry[HISTORY_KEY_SELECTED_COUNT]}",
                    f"{ANSWERED_COUNT_LABEL}: {entry[HISTORY_KEY_ANSWERED_COUNT]}",
                    f"{CORRECT_COUNT_LABEL}: {entry[HISTORY_KEY_CORRECT_COUNT]}",
                    f"{SCORE_LABEL}: {entry[HISTORY_KEY_SCORE]}",
                    f"{HINT_USED_COUNT_LABEL}: {entry[HISTORY_KEY_HINT_USED_COUNT]}",
                ]
            )
        )
