# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 01:34:29 2020

@author: Noah Lee, lee.no@northeastern.edu
"""

from pystreamable import StreamableApi
from dotenv import load_dotenv
import os

class StreamableUpload(object):
    
    def __init__(self):
        load_dotenv()
        USERNAME = os.getenv('STREAMABLE_USERNAME')
        PASSWORD = os.getenv('STREAMABLE_PASSWORD')
        self.streamable = StreamableApi(USERNAME, PASSWORD)
    
    def __call__(self, filepath):
        self.streamable.upload_video(filepath)
        