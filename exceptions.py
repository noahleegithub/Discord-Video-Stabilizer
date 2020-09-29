# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 22:09:05 2020

@author: Noah Lee, lee.no@northeastern.edu
"""

class StabbotException(Exception):
    ''' Raised when an error occurs during Stabbot's operation.
    '''
    def __init__(self, msg):
        super().__init__(msg)

class VideoDownloadingException(StabbotException):
    ''' Raised when an error occurs downloading a video.
    '''
    def __init__(self, msg):
        super().__init__("Error when downloading video: " + msg)

class VideoStabilisingException(StabbotException):
    ''' Raised when an error occurs stabilizing a video
    '''
    def __init__(self, msg):
        super().__init__("Error when stabilizing video: " + msg)
