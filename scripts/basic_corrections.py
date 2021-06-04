import cv2
import numpy as np

def change_gamma(videolist, preview_frame, selected_video, gamma_value):
    cap = cv2.VideoCapture(videolist[selected_video - 1])

    # Check if camera opened successfully
    if (cap.isOpened() == False):
        print("Error opening video stream or file")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # print('Frame count:', frame_count)

    cap.set(cv2.CAP_PROP_POS_FRAMES, preview_frame)
    # Capture specified preview frame
    _, frame = cap.read()

    original = frame

    # When everything done, release the video capture object
    cap.release()

    # adjust gamma:
    if gamma_value == 10:
        image_gamma = original
        return

    else:
        image_gamma = adjust_gamma(original, gamma_value)

    return image_gamma


def adjust_gamma(image, gamma_value):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    gamma_value = gamma_value/10  # slider is from 0 to 20, because minimum increment is 1

    invGamma = 1.0 / gamma_value
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)
