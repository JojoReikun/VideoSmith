import cv2
import numpy as np

def change_gamma(preview_image, gamma_value):
    # adjust gamma:
    if gamma_value == 10:
        image_gamma = preview_image
        return
    elif gamma_value == 0:
        gamma_value == 1
        image_gamma = adjust_gamma(preview_image, gamma_value)
    else:
        image_gamma = adjust_gamma(preview_image, gamma_value)

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
