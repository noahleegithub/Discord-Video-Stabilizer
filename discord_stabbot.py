# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 14:23:54 2020

@author: Noah Lee, lee.no@northeastern.edu
"""
import os
from dotenv import load_dotenv
from bot import Stabbot

def main():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    bot = Stabbot(command_prefix="stab!", 
                  description="A discord bot for stabilizing videos.", 
                  token=TOKEN)
    bot.run()

if __name__ == "__main__":
    main()