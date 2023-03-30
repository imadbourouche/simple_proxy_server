import logging

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    green = "\x1b[0;32m"
    red = "\x1b[31;20m"
    blue = "\x1b[0;34m"
    yellow="\x1b[0;33m"
    reset = "\x1b[0m"

    format= "%(asctime)s - %(message)s"
    time="%(asctime)s"
    message="%(message)s"
    request_format = green + f"REQUEST: {time}\n" + reset + grey+ f"--------- LOGS ----------\n{message}-------------------------" + reset
    error_format= red + f"ERROR {time}: " + reset + grey + message + reset
    black_list_format = yellow + f"BLACK_LIST {time}: "+ reset + grey + message + reset
    
    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: request_format,
        logging.ERROR: error_format,
        logging.WARNING: black_list_format,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)