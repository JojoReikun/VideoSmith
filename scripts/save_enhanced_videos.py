import os
from pathlib import Path
import cv2

def save_new_videos(output_folder, videolist, enhancements, crop):
    # need output location
    # need video list
    # need new filenames
    # need to apply all settings to selected videos
    # settings are applied frame-wise, then video is saved

    filename_add = "_enh"

    for video in videolist:
        if crop == True:
            # framerange = start to end
            continue
        else:
            # framerange = all frames
                # for frame in framerange apply all enhancements
            continue
    return