import cv2
import matplotlib.pyplot as plt


def calculate_histogram(current_image):
    # first convert frame to grayscale:
    hist_original = cv2.calcHist(current_image,[0],None,[256],[0,256])

    plt.plot(hist_original)
    fig = plt.gcf()
    fig.set_size_inches(4, 4.5)
    fig.savefig("origHist.png", dpi=100)
    plt.show()
    plt.close()

    plot_hist_orig = cv2.imread("origHist.png")

    histogram_calculated = True
    return histogram_calculated, plot_hist_orig


def equalize_histogram(histogram_calculated, current_image, use_threshold, threshold_text):
    info = "histogram equalized"
    plot_hist_equ = None
    gray_frame_equalized = None
    default_clip_limit = 40

    if histogram_calculated != True:
        info = "histogram needs to be calculated first!"

    elif use_threshold != True:
        gray_frame_equalized = cv2.equalizeHist(current_image)
        hist_equalized = cv2.calcHist(gray_frame_equalized,[0],None,[256],[0,256])

        plt.plot(hist_equalized, "r-")
        fig = plt.gcf()
        fig.set_size_inches(4, 4.5)
        fig.savefig("equHist.png", dpi=100)
        plt.show()
        plt.close()

        plot_hist_equ = cv2.imread("equHist.png")

    elif use_threshold == True:
        if threshold_text == "CLAHE":
            gray_frame_equalized = cv2.equalizeHist(current_image)
            clahe = cv2.createCLAHE(clipLimit=default_clip_limit)
            gray_img_clahe = clahe.apply(gray_frame_equalized)

            gray_frame_equalized = gray_img_clahe
        else:
            gray_frame_equalized = gray_frame_equalized

    histogram_calculated = False

    return info, gray_frame_equalized, histogram_calculated, plot_hist_equ