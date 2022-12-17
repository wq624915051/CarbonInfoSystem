import sys
import logging
import datetime
from colorama import Fore,Style

def get_logger():
    # 获取对象
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
    return logger


class Log:
    #通过静态成员方法来调用
    logger = get_logger()
    # 获取当前时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def debug(msg):
        Log.logger.debug(Fore.WHITE + f"{Log.now}\t[DEBUG]: {str(msg)}" +  Style.RESET_ALL)

    @staticmethod
    def info(msg):
        Log.logger.info(Fore.GREEN + f"{Log.now}\t[INFO]: {str(msg)}" + Style.RESET_ALL)

    @staticmethod
    def warning(msg):
        Log.logger.warning(Fore.YELLOW + f"{Log.now}\t[WARNING]: {str(msg)}" + "\033[m")

    @staticmethod
    def error(msg):
        Log.logger.error(Fore.RED + f"{Log.now}\t[ERROR]: {str(msg)}" + Style.RESET_ALL)

    @staticmethod
    def critical(msg):
        Log.logger.critical(Fore.RED + f"{Log.now}\t[CRITICAL]: {str(msg)}" + Style.RESET_ALL)

if __name__ == '__main__':
    logger = Log()
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")
