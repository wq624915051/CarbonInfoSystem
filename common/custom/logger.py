import sys
import logging
import datetime
from colorama import Fore, Style

class Log:
    def __init__(self, level="info") -> None:
        self.logger = self.get_logger(level)

    def debug(self, msg):
        self.logger.debug(Fore.WHITE + f"{self.get_now()}\t[DEBUG]: {str(msg)}" + Style.RESET_ALL)
    
    def info(self, msg):
        self.logger.info(Fore.GREEN + f"{self.get_now()}\t[INFO]: {str(msg)}" + Style.RESET_ALL)
    
    def warning(self, msg):
        self.logger.warning(Fore.YELLOW + f"{self.get_now()}\t[WARNING]: {str(msg)}" + "\033[m")
    
    def error(self, msg):
        self.logger.error(Fore.RED + f"{self.get_now()}\t[ERROR]: {str(msg)}" + Style.RESET_ALL)
    
    def critical(self, msg):
        self.logger.critical(Fore.RED + f"{self.get_now()}\t[CRITICAL]: {str(msg)}" + Style.RESET_ALL)

    def get_now(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_logger(self, level="info"):
        if level == "debug":
            level = logging.DEBUG
        elif level == "info":
            level = logging.INFO
        elif level == "warning":
            level = logging.WARNING
        elif level == "error":
            level = logging.ERROR
        elif level == "critical":
            level = logging.CRITICAL
        else:
            level = logging.INFO
        # 获取对象
        logger = logging.getLogger()
        logger.setLevel(level)

        if not logger.handlers:
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(level)
            logger.addHandler(ch)
        return logger

my_logger = Log()

if __name__ == '__main__':
    loggg = Log(level="warning")
    loggg.debug("你")
    loggg.info("好")
    loggg.warning("世")
    loggg.error("界")
    loggg.critical("！")