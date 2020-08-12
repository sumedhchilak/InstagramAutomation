import functools
import logging
import configparser
import time

def config_init(config_path):
    """
        Method initializes configuration
        Parameter is the Path the .ini configuration file
    """
    path = config_path.split('.')
    assert(path[len(path)-1] == 'ini') # Makes sure the file has the correct configuration
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

def get_log_object(logger_path):
    """
        Makes a logging object and returns it

    """
    logger = logging.getLogger('InstaBotLogger')
    logger.setLevel(logging.DEBUG)
    fileHand = logging.FileHandler(logger_path) # The log file handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') #The Log format
    fileHand.setFormatter(formatter)
    logger.addHandler(fileHand)
    return logger

def exception(func):
    """
        The exception logging decorator

    """
    #Function to wrap
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            #Exception
            message = "Exception in method {}".format(func.__name__)
            logger = get_log_object('bot.log')
            logger.exception(message)

def sleep_method(func):
    """
        Method that sleeps for 2 sec before calling methods
    
    """
    def wrapper(*args, **kwargs):
        PAUSE = 1
        time.sleep(PAUSE)
        func(*args, **kwargs)
        time.sleep(PAUSE)
    return wrapper