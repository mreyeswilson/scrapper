import logging
import colorlog

log_formatter = colorlog.ColoredFormatter(
    '%(log_color)s[%(asctime)s][%(levelname)s]:%(reset)s %(message)s',
    log_colors={
        "DEBUG": "orange",
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Configurar el logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configurar el manejador (handler) de salida a la consola con el formato colorido
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)