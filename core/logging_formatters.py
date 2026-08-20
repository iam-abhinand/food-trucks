import logging


class JSONFormatter(logging.Formatter):
    def format(self, record):
        return super().format(record)
