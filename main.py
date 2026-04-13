"""프로그램 실행 진입점을 제공하는 모듈.

이 파일은 최대한 단순하게 유지해서, 실제 게임 로직은 `QuizGame` 쪽에
모여 있고 실행 시작만 여기서 담당한다는 점이 바로 드러나도록 한다.
"""

from quiz_game import QuizGame


def main() -> None:
    """퀴즈 게임 객체를 만들고 메인 루프를 시작한다."""
    game = QuizGame()
    game.run()


if __name__ == "__main__":
    main()
