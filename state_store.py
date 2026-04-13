from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from console_io import OutputFn
from default_data import build_default_state
from game_constants import (
    BEST_SCORE_NEGATIVE_ERROR,
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
    HISTORY_LIST_ERROR,
    HISTORY_NEGATIVE_VALUES_ERROR,
    LEGACY_HISTORY_KEY_QUESTION_COUNT,
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
            self.output_fn(STATE_FILE_MISSING_MESSAGE)
            state = self._parse_state(build_default_state())
            self.save_state(state)
            return state

        try:
            with self.state_path.open("r", encoding="utf-8") as file:
                raw_state = json.load(file)
            return self._parse_state(raw_state)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            self.output_fn(STATE_FILE_RECOVERY_MESSAGE_TEMPLATE.format(error=error))
            state = self._parse_state(build_default_state())
            self.save_state(state)
            return state

    def save_state(self, state: GameState) -> bool:
        data = {
            STATE_KEY_VERSION: STATE_VERSION,
            STATE_KEY_NEXT_QUIZ_ID: state.next_quiz_id,
            STATE_KEY_BEST_SCORE: state.best_score,
            STATE_KEY_QUIZZES: [quiz.to_dict() for quiz in state.quizzes],
            STATE_KEY_HISTORY: list(state.history),
        }

        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with self.state_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")
        except OSError as error:
            self.output_fn(STATE_SAVE_FAILED_MESSAGE_TEMPLATE.format(error=error))
            return False

        return True

    def _parse_state(self, data: dict[str, object]) -> GameState:
        if not isinstance(data, dict):
            raise ValueError(STATE_DATA_DICT_ERROR)

        version = int(data[STATE_KEY_VERSION])
        if version != STATE_VERSION:
            raise ValueError(UNSUPPORTED_STATE_VERSION_ERROR_TEMPLATE.format(version=version))

        quizzes_raw = data[STATE_KEY_QUIZZES]
        best_score = int(data[STATE_KEY_BEST_SCORE])
        history_raw = data[STATE_KEY_HISTORY]
        next_quiz_id = int(data[STATE_KEY_NEXT_QUIZ_ID])

        if best_score < 0:
            raise ValueError(BEST_SCORE_NEGATIVE_ERROR)
        if next_quiz_id < 1:
            raise ValueError(NEXT_QUIZ_ID_MIN_ERROR)
        if not isinstance(quizzes_raw, list):
            raise ValueError(QUIZZES_LIST_ERROR)
        if not isinstance(history_raw, list):
            raise ValueError(HISTORY_LIST_ERROR)

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
            raise ValueError(HISTORY_ENTRY_DICT_ERROR)

        played_at = str(entry[HISTORY_KEY_PLAYED_AT])
        selected_count = int(
            entry.get(HISTORY_KEY_SELECTED_COUNT, entry.get(LEGACY_HISTORY_KEY_QUESTION_COUNT, 0))
        )
        answered_count = int(
            entry.get(HISTORY_KEY_ANSWERED_COUNT, entry.get(LEGACY_HISTORY_KEY_QUESTION_COUNT, 0))
        )
        correct_count = int(entry[HISTORY_KEY_CORRECT_COUNT])
        score = int(entry[HISTORY_KEY_SCORE])
        hint_used_count = int(entry[HISTORY_KEY_HINT_USED_COUNT])

        if (
            selected_count < 0
            or answered_count < 0
            or correct_count < 0
            or score < 0
            or hint_used_count < 0
        ):
            raise ValueError(HISTORY_NEGATIVE_VALUES_ERROR)
        if answered_count > selected_count:
            raise ValueError(HISTORY_ANSWERED_GT_SELECTED_ERROR)
        if correct_count > answered_count:
            raise ValueError(HISTORY_CORRECT_GT_ANSWERED_ERROR)
        if hint_used_count > answered_count:
            raise ValueError(HISTORY_HINT_GT_ANSWERED_ERROR)

        return {
            HISTORY_KEY_PLAYED_AT: played_at,
            HISTORY_KEY_SELECTED_COUNT: selected_count,
            HISTORY_KEY_ANSWERED_COUNT: answered_count,
            HISTORY_KEY_CORRECT_COUNT: correct_count,
            HISTORY_KEY_SCORE: score,
            HISTORY_KEY_HINT_USED_COUNT: hint_used_count,
        }
