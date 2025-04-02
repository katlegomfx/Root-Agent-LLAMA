import logging
import re
import os

ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


class NoColorFormatter(logging.Formatter):
    """
    Custom logging formatter that strips ANSI escape sequences from the message.
    """

    def format(self, record):
        original = super().format(record)
        return ANSI_ESCAPE.sub('', original)


def setup_logging():
    disable_color = os.environ.get("DISABLE_COLOR_LOGS", "1") == "1"

    handler = logging.StreamHandler()
    if disable_color:
        formatter = NoColorFormatter(
            fmt='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[handler])
