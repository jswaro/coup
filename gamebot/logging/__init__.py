import logging

__base_logger = logging.getLogger()
__base_handler = logging.NullHandler()
__base_formatter = logging.Formatter(fmt='%(name)s: %(message)s - [%(levelname)s] '
                                         '(%(funcName)s) %(filename)s:%(lineno)d')

__base_handler.setFormatter(__base_formatter)
__base_logger.addHandler(__base_handler)
__base_logger.setLevel(logging.DEBUG)


def log_to_stream(stream, level):
    global __base_formatter
    global __base_logger

    handler = logging.StreamHandler(stream)
    handler.setFormatter(__base_formatter)
    handler.setLevel(level)
    __base_logger.addHandler(handler)


def log_to_file(filename, level):
    global __base_formatter
    global __base_logger

    handler = logging.FileHandler(filename)
    handler.setFormatter(__base_formatter)
    handler.setLevel(level)
    __base_logger.addHandler(handler)
