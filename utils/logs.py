import colorlog

def config_logger():

    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s%(green)s - %(name)s - %(reset)s%(light_white)s%(message)s %(reset)s%(white)s(%(filename)s:%(lineno)d)%(reset)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "blue",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red,bg_bold_white",
        }
    ))

    logger = colorlog.getLogger()
    logger.setLevel(colorlog.INFO)
    logger.addHandler(console_handler)