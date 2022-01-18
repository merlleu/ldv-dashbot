# import logging
# logging.basicConfig(level=logging.DEBUG)


import getpass
import src
bot = src.Bot(input('Email > '), getpass.getpass("Password > "))
print(f"Connected as {bot.user}")