import cv2


def handle_video_preview(videolist, selected_preview, preview_frame):
    """
    default first video in list is selected for preview unless changed

    :param videolist: passed from the selected list of videos
    :param selected_preview:  passed from selected video in combo box
    :param preview_frame:  passed from slider
    :return:
    """

    if selected_preview != videolist[0]:
        # update preview with new selected video

        preview_image = None


def set_default_preview(videolist, preview_frame, selected_video):
    # load the original image
    #print("in handle_preview: ", videolist)

    cap = cv2.VideoCapture(videolist[selected_video-1])

    # Check if camera opened successfully
    if (cap.isOpened() == False):
        print("Error opening video stream or file")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #print('Frame count:', frame_count)

    cap.set(cv2.CAP_PROP_POS_FRAMES, preview_frame)
    # Capture specified preview frame
    _, frame = cap.read()

    original = frame

    preview_image = original

    # When everything done, release the video capture object
    cap.release()
    # Closes all the frames
    #cv2.destroyAllWindows()

    return preview_image, frame_count

