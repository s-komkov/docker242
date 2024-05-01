"""
setup_logging
~~~~~~~~~~~~~~~~~~~~~

Настройки логгирования и вывода сообщений приложения.

Описание констант:

   >>> LOGGING_TYPE - Тип логирования. console - вывод сообщений в stdout; file - запись сообщений в файл
   >>> LOGGING_LEVEL - Уровень логирования CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG, NOTSET.
       Собщения ниже указанного уровня выводиться не будут. 
   >>> LOG_PATH - Путь к файлу логов
   >>> LOG_FILE - Название лог-файла 
   
Формат "%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s - %(message)s" выводит сообщения
в следующем виде:

2023-12-20 09:01:47,437 - [{Уровень}] - ({Имя файла}).{Имя функции python} - {Сообщение}
   
"""


import logging

LOGGING_TYPE = "console"
LOGGING_LEVEL = logging.INFO
LOG_PATH = "."
LOG_FILE = "app"


logFormatter = logging.Formatter("%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(LOGGING_LEVEL)

if LOGGING_TYPE == "console":
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
elif LOGGING_TYPE == "file":
    fileHandler = logging.FileHandler(f"{LOG_PATH}/{LOG_FILE}.log")
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)


