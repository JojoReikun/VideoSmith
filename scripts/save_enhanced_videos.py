import os
from pathlib import Path
import cv2

def save_new_videos(output_folder, videolist, enhancements, crop, crop_start, crop_end, gamma, gamma_value, callback=None):
    """
    this function reads in video by video. For each video frames within the crop range are read in one-by-one,
    enhancements are applied and then the video is saved to the selected output location.
    The progress is returned via callback.
    :param output_folder: selected path for saving the enhanced videos
    :param videolist: list of filepaths to all selected videos
    :param enhancements: dictionary of {'enhancement': value}, where value defines eg. gamma_value etc. depending on type of enhancement.
    :param crop: bool. If True video within crop_start to frame_count-crop_end will be stored. If False entire video.
    :param crop_start:
    :param crop_end:
    :param callback:
    :return: Info message that saving of videos was successful
    """

    # make output folder if it doesn't exist yet
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    filename_add = "_enh"

    for i, video in enumerate(videolist):
        # create a video capture object
        cap = cv2.VideoCapture(video)

        # Check if camera opened successfully
        if (cap.isOpened() == False):
            print("Error opening video stream or file")

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count/frame_rate
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # get the videoname:
        #print("video: ", video)
        filename = str(video).rsplit("/", 1)[1]
        filename = filename.rsplit(".", 1)[0]
        #print("filename: ", filename)
        videoname = filename + filename_add
        print("videoname: ", videoname)

        # create a video write object
        output_name = os.path.join(output_folder, videoname) + ".avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_name, fourcc, frame_rate, (frame_width, frame_height))

        # set output video length:
        if crop == True:
            framerange = [crop_start, crop_end]
            cap.set(1, crop_start)
        else:   # all frames
            framerange = [0, frame_count]

        # read in frame by frame and apply enhancements, then save video
        counter = 0
        while(cap.isOpened()):
            counter += 1
            ret, frame = cap.read()
            if ret == True:

                if gamma == True:
                    gamma_frame = adjust_gamma(frame, gamma_value)
                    enh_frame = gamma_frame
                else:
                    enh_frame = frame

                # write frame to video:
                if crop == True:
                    if counter > (frame_count-crop_end):
                        break   # stop writing to video once desired crop-off end reached
                    else:
                        out.write(enh_frame)
                else:
                    out.write(enh_frame)

            else:
                break

            #print("Counter: ", counter)

        # track progress for files:
        if callback is not None:
            callback.emit(int(100 * (i / len(videolist))))

        cap.release()
        out.release()

    return "all enhanced videos saved successfully to {}".format(output_folder)


def adjust_gamma(image, gamma_value):
    import numpy as np
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    gamma_value = gamma_value/10  # slider is from 0 to 20, because minimum increment is 1

    invGamma = 1.0 / gamma_value
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)