import logging

logger = None

def register_logger(obj):
    global logger
    logger = obj
