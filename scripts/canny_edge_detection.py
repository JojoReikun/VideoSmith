import cv2
import numpy as np

def canny_edge_detector(current_image):
    # blurring
    blurred = cv2.GaussianBlur(current_image, (5, 5), 0)
    # canny
    sigma = 0.33
    v = np.median(current_image)
    lower = int(max(0, (1.0-sigma) * v))
    upper = int(min(255, (1.0+sigma) * v))
    auto = cv2.Canny(blurred, lower, upper)
    edge_image = auto

    return edge_image