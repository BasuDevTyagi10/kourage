import asyncio
import json
import os
import time
import logging
import platform
import datetime
import discord
from colorama import init
from termcolor import colored

machine = platform.node()
init()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


class Logger:
    def __init__(self, app):
        self.app = app

    def info(self, message):
        print(colored(f'[{time.asctime(time.localtime())}] [{machine}] [{self.app}] {message}', 'yellow'))

    def warning(self, message):
        print(colored(f'[{time.asctime(time.localtime())}] [{machine}] [{self.app}] {message}', 'green'))

    def error(self, message):
        print(colored(f'[{time.asctime(time.localtime())}] [{machine}] [{self.app}] {message}', 'red'))

    def color(self, message, color):
        print(colored(f'[{time.asctime(time.localtime())}] [{machine}] [{self.app}] {message}', color))



def simple_embed(title, description):
    embed = discord.Embed(
            title = title,
            description = description,
            colour=0x11806a
            )
    
    return embed



