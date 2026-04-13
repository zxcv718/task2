DEFAULT_STATE_PATH = "state.json"

STATE_VERSION = 1
BASE_POINTS = 10
HINT_POINTS = 7
RECENT_HISTORY_LIMIT = 5

STATE_KEY_VERSION = "version"
STATE_KEY_NEXT_QUIZ_ID = "next_quiz_id"
STATE_KEY_BEST_SCORE = "best_score"
STATE_KEY_QUIZZES = "quizzes"
STATE_KEY_HISTORY = "history"

HISTORY_KEY_PLAYED_AT = "played_at"
HISTORY_KEY_SELECTED_COUNT = "selected_count"
HISTORY_KEY_ANSWERED_COUNT = "answered_count"
HISTORY_KEY_CORRECT_COUNT = "correct_count"
HISTORY_KEY_SCORE = "score"
HISTORY_KEY_HINT_USED_COUNT = "hint_used_count"
LEGACY_HISTORY_KEY_QUESTION_COUNT = "question_count"

APP_TITLE = "나만의 퀴즈 게임"
APP_STATE_NOTICE = "진행 상황은 state.json에 저장됩니다."
MENU_PROMPT = "메뉴 번호를 선택하세요: "
MENU_DIVIDER = "=" * 40
SECTION_DIVIDER = "-" * 40
MENU_OPTIONS = (
    "1. 퀴즈 풀기",
    "2. 퀴즈 추가",
    "3. 퀴즈 목록",
    "4. 퀴즈 삭제",
    "5. 점수 확인",
    "6. 종료",
)

NO_REGISTERED_QUIZZES_MESSAGE = "현재 등록된 퀴즈가 없습니다."
QUIZ_INTERRUPTED_RECORDED_MESSAGE = "퀴즈 진행이 중단되어 현재까지의 결과를 기록했습니다."
QUIZ_FINISHED_MESSAGE = "퀴즈가 끝났습니다."
SAVE_AND_EXIT_MESSAGE = "진행 상황을 저장하고 종료합니다."
EXIT_MESSAGE = "프로그램을 종료합니다."

SUMMARY_SELECTED_COUNT_LABEL = "선택한 문제 수"
SUMMARY_ANSWERED_COUNT_LABEL = "푼 문제 수"
SUMMARY_CORRECT_COUNT_LABEL = "맞힌 문제 수"
SUMMARY_SCORE_LABEL = "점수"
SUMMARY_BEST_SCORE_LABEL = "최고 점수"

INPUT_INTERRUPTED_MESSAGE = "입력이 중단되었습니다. 저장 후 안전하게 종료합니다."
EMPTY_INPUT_MESSAGE = "빈 입력은 허용되지 않습니다. 다시 입력해주세요."
NUMBERS_ONLY_MESSAGE = "숫자만 입력해주세요."
RANGE_MESSAGE_TEMPLATE = "{minimum}부터 {maximum} 사이의 숫자를 입력해주세요."

ADD_QUIZ_TITLE = "새 퀴즈 추가"
QUESTION_PROMPT = "문제: "
CHOICE_PROMPTS = (
    "선택지 1: ",
    "선택지 2: ",
    "선택지 3: ",
    "선택지 4: ",
)
ANSWER_NUMBER_PROMPT = "정답 번호를 입력하세요 (1-4): "
HINT_PROMPT = "힌트: "
QUIZ_ADDED_MESSAGE_TEMPLATE = "{quiz_id}번 퀴즈가 추가되었습니다."
NO_QUIZZES_TO_LIST_MESSAGE = "표시할 퀴즈가 없습니다."
QUIZ_LIST_TITLE = "저장된 퀴즈 목록"
QUIZ_ID_LABEL = "ID"
QUESTION_LABEL = "문제"
ANSWER_LABEL = "정답 번호"
HINT_LABEL = "힌트"
NO_QUIZZES_TO_DELETE_MESSAGE = "삭제할 퀴즈가 없습니다."
DELETE_QUIZ_TITLE = "삭제할 퀴즈 ID를 선택하세요."
DELETE_QUIZ_PROMPT = "삭제할 퀴즈 ID: "
QUIZ_ID_NOT_FOUND_MESSAGE = "해당 ID의 퀴즈가 없습니다. 다시 입력하세요."
QUIZ_DELETED_MESSAGE_TEMPLATE = "{quiz_id}번 퀴즈를 삭제했습니다."

QUESTION_COUNT_PROMPT_TEMPLATE = "몇 문제를 풀까요? (1-{quiz_count}): "
QUIZ_START_MESSAGE_TEMPLATE = "총 {selected_count}문제를 시작합니다."
QUESTION_PROGRESS_TEMPLATE = "문제 {question_index}/{selected_count}"
CORRECT_ANSWER_MESSAGE_TEMPLATE = "정답입니다! +{points}점"
WRONG_ANSWER_MESSAGE_TEMPLATE = "오답입니다. 정답은 {answer}번, {correct_text}입니다."
ANSWER_INPUT_PROMPT = "정답 입력 (1-4, 힌트는 h): "
HINT_COMMAND = "h"
HINT_ALREADY_USED_MESSAGE = "이 문제에서는 이미 힌트를 사용했습니다."
HINT_MESSAGE_TEMPLATE = "힌트: {hint}"
ANSWER_OR_HINT_ONLY_MESSAGE = "1, 2, 3, 4 또는 h만 입력해주세요."
ANSWER_RANGE_OR_HINT_MESSAGE = "1부터 4까지의 숫자 또는 h를 입력해주세요."

PLAY_COUNT_LABEL = "총 플레이 횟수"
NO_PLAY_HISTORY_MESSAGE = "아직 저장된 플레이 기록이 없습니다."
RECENT_HISTORY_TITLE = "최근 5개 기록:"
PLAYED_AT_LABEL = "플레이 시각"
SELECTED_COUNT_LABEL = "선택 문제 수"
ANSWERED_COUNT_LABEL = "푼 문제 수"
CORRECT_COUNT_LABEL = "맞힌 문제 수"
SCORE_LABEL = "점수"
HINT_USED_COUNT_LABEL = "힌트 사용 수"

STATE_FILE_MISSING_MESSAGE = "state.json 파일이 없어 기본 퀴즈로 새로 생성합니다."
STATE_FILE_RECOVERY_MESSAGE_TEMPLATE = "state.json을 불러오지 못했습니다 ({error}). 기본 데이터로 복구합니다."
STATE_SAVE_FAILED_MESSAGE_TEMPLATE = "state.json 저장에 실패했습니다: {error}"

STATE_DATA_DICT_ERROR = "state 데이터는 딕셔너리여야 합니다."
UNSUPPORTED_STATE_VERSION_ERROR_TEMPLATE = "지원하지 않는 state 버전입니다: {version}"
BEST_SCORE_NEGATIVE_ERROR = "best_score는 음수일 수 없습니다."
NEXT_QUIZ_ID_MIN_ERROR = "next_quiz_id는 1 이상이어야 합니다."
QUIZZES_LIST_ERROR = "quizzes는 리스트여야 합니다."
HISTORY_LIST_ERROR = "history는 리스트여야 합니다."
HISTORY_ENTRY_DICT_ERROR = "각 history 항목은 딕셔너리여야 합니다."
HISTORY_NEGATIVE_VALUES_ERROR = "history 값은 음수일 수 없습니다."
HISTORY_ANSWERED_GT_SELECTED_ERROR = "answered_count는 selected_count보다 클 수 없습니다."
HISTORY_CORRECT_GT_ANSWERED_ERROR = "correct_count는 answered_count보다 클 수 없습니다."
HISTORY_HINT_GT_ANSWERED_ERROR = "hint_used_count는 answered_count보다 클 수 없습니다."
