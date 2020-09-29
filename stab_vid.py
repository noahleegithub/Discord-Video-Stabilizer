# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 23:57:54 2020

@author: Noah Lee, lee.no@northeastern.edu
"""

import subprocess
from ffprobe import FFProbe
from exceptions import VideoStabilisingException
import os

def is_number(s):
    """ Returns True if string is a number. 
        
        Args:
            s (str): The input string.
 
        Returns:
            True if s is a number, False otherwise.
    """
    return s.replace('.', '', 1).isdigit()


class StabVid(object):

    def __init__(self,
                 ffmpeg_full_path="ffmpeg",
                 video_scale_factor="1.15",
                 video_zoom_factor="-15",
                 max_video_length_seconds=120):
        self.max_video_length_seconds = max_video_length_seconds
        self.min_video_length_seconds = 1
        self.ffmpeg_full_path = ffmpeg_full_path
        self.video_scale_factor = video_scale_factor
        self.video_zoom_factor = video_zoom_factor

    def __call__(self, input_path, output_path):
        return self.stab_file(input_path, output_path)

    def stab_file(self, input_path, output_path):
        ''' Stabilizes and compresses a video.

        Parameters
        ----------
        input_path : string
            The path to get the video from.
        output_path : string
            Where the final video goes.

        Raises
        ------
        VideoStabilisingException
            If an error is encountered while stabilizing the video.

        Returns
        -------
        None.
        '''
        zoomed_file_name = os.path.abspath(os.path.join("videos", "zoomed.mp4"))
        stabbed_file_name = os.path.abspath(os.path.join("videos", "stabilized.mp4"))
        
        metadata = FFProbe(input_path)
        if len(metadata.video) > 1:
            raise VideoStabilisingException("Video may not contain multiple video streams.")
        if len(metadata.video) < 1:
            raise VideoStabilisingException("No video streams found in file")

        could_check_dur_initially = self.check_vid_duration(input_path)

        try:
            # zoom by the size of the zoom in the stabilization, the total output file is bigger,
            # but no resolution is lost to the crop
            subprocess.check_output(
                [self.ffmpeg_full_path,
                 "-y",
                 "-i", input_path,
                 "-vf", "scale=trunc((iw*" + self.video_scale_factor + ")/2)*2:trunc(ow/a/2)*2",
                 "-pix_fmt", "yuv420p",
                 zoomed_file_name],
                shell=False,
                stderr=subprocess.STDOUT)

            if not could_check_dur_initially:
                # sometimes metadata on original vids were broken,
                # so we need to re-check after fixing it during the first ffmpeg-pass
                self.check_vid_duration(zoomed_file_name)

            subprocess.check_output(
                [self.ffmpeg_full_path,
                 "-y",
                 "-i", zoomed_file_name,
                 "-vf", "vidstabdetect",
                 "-f", "null",
                 "-"],
                shell=True,
                stderr=subprocess.STDOUT)

            subprocess.check_output(
                [self.ffmpeg_full_path,
                 "-y",
                 "-i", zoomed_file_name,
                 "-vf", "vidstabtransform=smoothing=20:crop=black:zoom=" + self.video_zoom_factor
                 + ":optzoom=0:interpol=linear,unsharp=5:5:0.8:3:3:0.4",
                 "-threads", "1",
                 stabbed_file_name],
                shell=True,
                stderr=subprocess.STDOUT)
            
            subprocess.check_output(
                [self.ffmpeg_full_path,
                 "-y",
                 "-i", stabbed_file_name,
                 "-vcodec", "libx265",
                 "-threads", "1"
                 "-crf", "28",
                 output_path],
                shell=True,
                stderr=subprocess.STDOUT)
            
        except subprocess.CalledProcessError as cpe:
            print("cpe.returncode", cpe.returncode)
            print("cpe.cmd", cpe.cmd)
            print("cpe.output", cpe.output)

            raise VideoStabilisingException("ffmpeg could't compute file")

    def check_vid_duration(self, path):
        ''' Checks whether the video has a duration - if it does, check the
            length.

        Parameters
        ----------
        path : string
            Path to the video.

        Raises
        ------
        VideoStabilisingException
            If the length of the video is greater than max or less than min.

        Returns
        -------
        bool
            True if the video has a valid duration, False if the video cannot
            be processed for its duration yet.

        '''
        metadata = FFProbe(path)
        if hasattr(metadata.video[0], "duration") \
            and is_number(metadata.video[0].duration):
            if float(metadata.video[0].duration) > self.max_video_length_seconds:
                raise VideoStabilisingException("Video too long. Video duration: " 
                                                + metadata.video[0].duration 
                                                + ", Maximum duration: " 
                                                + str(self.max_video_length_seconds) 
                                                + ". ")
            elif float(metadata.video[0].duration) < self.min_video_length_seconds:
                raise VideoStabilisingException("Video too short. Video duration: " 
                                                + metadata.video[0].duration
                                                + ", Minimum duration: " 
                                                + str(self.min_video_length_seconds)
                                                + ". ")
            else:
                return True
        return False
