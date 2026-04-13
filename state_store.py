from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from console_io import OutputFn
from default_data import build_default_state
from game_constants import STATE_VERSION
from quiz import Quiz


@dataclass(slots=True)
class GameState:
    quizzes: list[Quiz]
    best_score: int
    history: list[dict[str, object]]
    next_quiz_id: int


class StateStore:
    def __init__(self, state_path: str | Path, output_fn: OutputFn) -> None:
        self.state_path = Path(state_path)
        self.output_fn = output_fn

    def load_state(self) -> GameState:
        if not self.state_path.exists():
            self.output_fn("state.json 파일이 없어 기본 퀴즈로 새로 생성합니다.")
            state = self._parse_state(build_default_state())
            self.save_state(state)
            return state

        try:
            with self.state_path.open("r", encoding="utf-8") as file:
                raw_state = json.load(file)
            return self._parse_state(raw_state)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            self.output_fn(
                f"state.json을 불러오지 못했습니다 ({error}). 기본 데이터로 복구합니다."
            )
            state = self._parse_state(build_default_state())
            self.save_state(state)
            return state

    def save_state(self, state: GameState) -> bool:
        data = {
            "version": STATE_VERSION,
            "next_quiz_id": state.next_quiz_id,
            "best_score": state.best_score,
            "quizzes": [quiz.to_dict() for quiz in state.quizzes],
            "history": list(state.history),
        }

        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with self.state_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")
        except OSError as error:
            self.output_fn(f"state.json 저장에 실패했습니다: {error}")
            return False

        return True

    def _parse_state(self, data: dict[str, object]) -> GameState:
        if not isinstance(data, dict):
            raise ValueError("state 데이터는 딕셔너리여야 합니다.")

        version = int(data["version"])
        if version != STATE_VERSION:
            raise ValueError(f"지원하지 않는 state 버전입니다: {version}")

        quizzes_raw = data["quizzes"]
        best_score = int(data["best_score"])
        history_raw = data["history"]
        next_quiz_id = int(data["next_quiz_id"])

        if best_score < 0:
            raise ValueError("best_score는 음수일 수 없습니다.")
        if next_quiz_id < 1:
            raise ValueError("next_quiz_id는 1 이상이어야 합니다.")
        if not isinstance(quizzes_raw, list):
            raise ValueError("quizzes는 리스트여야 합니다.")
        if not isinstance(history_raw, list):
            raise ValueError("history는 리스트여야 합니다.")

        quizzes = [Quiz.from_dict(item) for item in quizzes_raw]
        history = [self._validate_history_entry(item) for item in history_raw]
        highest_quiz_id = max((quiz.quiz_id for quiz in quizzes), default=0)

        return GameState(
            quizzes=quizzes,
            best_score=best_score,
            history=history,
            next_quiz_id=max(next_quiz_id, highest_quiz_id + 1),
        )

    def _validate_history_entry(self, entry: dict[str, object]) -> dict[str, object]:
        if not isinstance(entry, dict):
            raise ValueError("각 history 항목은 딕셔너리여야 합니다.")

        played_at = str(entry["played_at"])
        selected_count = int(entry.get("selected_count", entry.get("question_count", 0)))
        answered_count = int(entry.get("answered_count", entry.get("question_count", 0)))
        correct_count = int(entry["correct_count"])
        score = int(entry["score"])
        hint_used_count = int(entry["hint_used_count"])

        if (
            selected_count < 0
            or answered_count < 0
            or correct_count < 0
            or score < 0
            or hint_used_count < 0
        ):
            raise ValueError("history 값은 음수일 수 없습니다.")
        if answered_count > selected_count:
            raise ValueError("answered_count는 selected_count보다 클 수 없습니다.")
        if correct_count > answered_count:
            raise ValueError("correct_count는 answered_count보다 클 수 없습니다.")
        if hint_used_count > answered_count:
            raise ValueError("hint_used_count는 answered_count보다 클 수 없습니다.")

        return {
            "played_at": played_at,
            "selected_count": selected_count,
            "answered_count": answered_count,
            "correct_count": correct_count,
            "score": score,
            "hint_used_count": hint_used_count,
        }
