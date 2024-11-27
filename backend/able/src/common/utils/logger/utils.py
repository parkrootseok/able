import logging

class CustomFormatter(logging.Formatter):
    CYAN = "\033[36m"
    RESET = "\033[0m"

    def format(self, record):
        record.msg = f"{self.CYAN}{record.msg}{self.RESET}"
        return super().format(record)


def get_logger(name: str, level: int = logging.INFO, log_to_file: bool = False, log_file: str = "app.log") -> logging.Logger:

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if not logger.hasHandlers():
        logger.setLevel(level)
        logger.propagate = False

        # Console handler
        stream_handler = logging.StreamHandler()
        formatter = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # Optional file handler
        if log_to_file:
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

    return logger
