import logging

_logger_object = None

def register_logger(obj):
    global _logger_object
    _logger_object = obj

def get_logger(mod_name):
    if _logger_object == None:
        return logging.logger(mod_name)
    return _logger_object
