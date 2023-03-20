from loguru import logger

# format = "[{time:DD.MM.YY HH:mm:ss}] [{module}.{function}:{line}] [{level}]: {message}"
format = "[{time:DD.MM.YY HH:mm:ss}] [{level}]: {message}"
logger_config = {
    "handlers": [{
        "sink": "debug.log",
        "format": format,
        "enqueue": True,
        "rotation": "5 MB",
        "compression": "zip",
        "level": "DEBUG",
    }]
}
logger.remove()
logger.configure(**logger_config)