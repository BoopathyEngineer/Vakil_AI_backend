import logging

def logger_setup(filename):
    logger = logging.getLogger(filename)
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler('hyperflx.log')

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger