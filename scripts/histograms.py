import cv2
import matplotlib.pyplot as plt


def convert_to_grayscale(videolist, preview_frame, selected_video):
    cap = cv2.VideoCapture(videolist[selected_video])

    # Check if camera opened successfully
    if (cap.isOpened() == False):
        print("Error opening video stream or file")

    cap.set(cv2.CAP_PROP_POS_FRAMES, preview_frame)
    # Capture specified preview frame
    _, frame = cap.read()

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # When everything done, release the video capture object
    cap.release()
    return gray_frame


def calculate_histogram(videolist, preview_frame, selected_video):
    # first convert frame to grayscale:
    gray_frame = convert_to_grayscale(videolist, preview_frame, selected_video)

    hist_original = cv2.calcHist(gray_frame,[0],None,[256],[0,256])

    plt.plot(hist_original)
    fig = plt.gcf()
    fig.set_size_inches(4, 4.5)
    fig.savefig("origHist.png", dpi=100)
    plt.show()
    plt.close()

    plot_hist_orig = cv2.imread("origHist.png")

    histogram_calculated = True
    return histogram_calculated, gray_frame, plot_hist_orig


def equalize_histogram(histogram_calculated, gray_frame, use_threshold, threshold_text):
    info = "histogram equalized"
    plot_hist_equ = None
    gray_frame_equalized = None
    default_clip_limit = 40

    if histogram_calculated != True:
        info = "histogram needs to be calculated first!"

    elif use_threshold != True:
        gray_frame_equalized = cv2.equalizeHist(gray_frame)
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
            gray_frame_equalized = cv2.equalizeHist(gray_frame)
            clahe = cv2.createCLAHE(clipLimit=default_clip_limit)
            gray_img_clahe = clahe.apply(gray_frame_equalized)

            gray_frame_equalized = gray_img_clahe
        else:
            gray_frame_equalized = gray_frame_equalized

    histogram_calculated = False

    return info, gray_frame_equalized, histogram_calculated, plot_hist_equ