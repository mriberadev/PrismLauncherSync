import os
import colorlog

def config_logger():
    os.environ["FORCE_COLOR"] = "True"
    colorlog.basicConfig(
        level=colorlog.INFO,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "light_blue",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red,bg_bold_white",
        },
        format=("%(white)s[%(asctime)s]"
                " %(log_color)s[%(levelname)s]"
                " %(green)s[%(module)s:%(lineno)d]"
                " %(light_white)s%(message)s%(reset)s"),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
