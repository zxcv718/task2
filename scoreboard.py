from __future__ import annotations

from datetime import datetime

from console_io import OutputFn
from game_constants import RECENT_HISTORY_LIMIT


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
    return max(best_score, total_score)


def show_scores(
    output_fn: OutputFn,
    *,
    best_score: int,
    history: list[dict[str, object]],
) -> None:
    output_fn("")
    output_fn(f"최고 점수: {best_score}")
    output_fn(f"총 플레이 횟수: {len(history)}")

    if not history:
        output_fn("아직 저장된 플레이 기록이 없습니다.")
        return

    output_fn("최근 5개 기록:")
    for entry in reversed(history[-RECENT_HISTORY_LIMIT:]):
        output_fn(
            " | ".join(
                [
                    f"플레이 시각: {entry['played_at']}",
                    f"선택 문제 수: {entry['selected_count']}",
                    f"푼 문제 수: {entry['answered_count']}",
                    f"맞힌 문제 수: {entry['correct_count']}",
                    f"점수: {entry['score']}",
                    f"힌트 사용 수: {entry['hint_used_count']}",
                ]
            )
        )
