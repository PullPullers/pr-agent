# 샘플 코드입니다.

class Logger:
    # TODO: 정상적인 할 일 생성
    # TODO: 제목이 없는 경우 예외 발생
    # todo: 제목이 1글자인 경우 허용
    # TODO - 제목이 너무 긴 경우 에러 처리
    """
    간단한 로거 클래스입니다. 메시지를 지정된 파일에 기록합니다.
    """
    def __init__(self, log_file_path: str):
        """
        Logger 인스턴스를 초기화합니다.

        :param log_file_path: 로그 메시지를 저장할 파일 경로입니다.
        """
        self.log_file_path = log_file_path

    def log_message(self, message: str, level: str = "INFO"):
        """
        TODO : Add a uniqudde index to the table
        지정된 메시지를 로그 파일에 기록합니다.

        :param message: 기록할 메시지 내용입니다.
        :param level: 로그 레벨 (예: INFO, WARNING, ERROR)입니다.
        """
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                log_entry = f"[{level}] {message}\n"
                f.write(log_entry)
            # 콘솔에도 간단히 출력 (선택 사항)
            print(f"로그 기록됨 ({self.log_file_path}): [{level}] {message}")
        except IOError as e:
            # todo test
            # todo todo
            print(f"로그 파일 쓰기 오류: {e}")

# TODO:
# 1. Logger 클래스는 파일 경로, 쓰기, 포매팅 기능을 수행함.
#    - SRP 관점에서 책임 분리 검토 필요.
# 2. OCP를 통해 포매팅/저장소 확장 가능성 고려.
#    - Strategy Pattern 또는 DI 활용.
# 3. 사용 예시 작성 및 예외 처리 테스트.

def unused_function():
    temp = 42
    # TODO
    pass

def empty_handler():
    # TODO 테스트
    pass