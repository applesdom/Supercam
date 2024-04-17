import logging

LOG_FILE  = './supercam.log'
LOG_LEVEL = logging.DEBUG

def set_up_logging():
    formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', style='%')
    print_handler = logging.StreamHandler()
    print_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Apply to root logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)  
    logger.addHandler(print_handler)
    logger.addHandler(file_handler)
