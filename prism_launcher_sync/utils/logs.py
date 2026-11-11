import colorlog


def config_logger():
    colorlog.basicConfig(
        level=colorlog.INFO,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "blue",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red,bg_bold_white",
        },
        format=("%(log_color)s[%(asctime)s.%(msecs)03d]"
                " [%(levelname)s]"
                " %(green)s[%(name)s]"
                " %(light_white)s%(message)s %(white)s"
                " (%(filename)s:%(lineno)d)%(reset)s"),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
