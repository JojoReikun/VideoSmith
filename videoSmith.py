import sys
import datetime
import traceback
import cgitb
import time
import os
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore

from qt_gui.videoEnhancer import Ui_MainWindow  # importing main window of the GUI
from scripts import handle_video_preview, histograms, basic_corrections

"""
Locations of required executables and how to use them:
"""

# LAB
# C:\Users\JojoS\Miniconda3\pkgs\qt-5.9.7-vc14h73c81de_0\Library\bin\designer.exe
# pyuic5 to convert UI to executable python code is located at:
# C:\Users\JojoS\Miniconda3\Scripts\pyuic5.exe
# to convert the UI into the required .py file run:
# -x = input     -o = output
# pyuic5.exe -x "D:\Jojo\PhD\VideoEnhancerPython\qt_gui\videoEnhancer.ui" -o "D:\Jojo\PhD\VideoEnhancerPython\qt_gui\videoEnhancer.py"


class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
        No data
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    progress
        `int` indicating % progress
    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)


class Worker(QtCore.QRunnable):
    '''
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class videoSmith_mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(videoSmith_mainWindow, self).__init__()
        self.ui = Ui_MainWindow()

        self.ui.setupUi(self)

        # start thread pool
        self.threadpool = QtCore.QThreadPool()

        ###
        # variables
        ###
        self.videolist = []
        self.selected_video = 0
        self.number_of_videos = 0
        self.progress = 0
        self.updateProgress(self.progress)
        self.selected_preview = 0
        self.preview_frame = 0
        self.frame_count = 100

        # set output location
        self.output_location = os.path.join(str(Path.cwd()), "output")
        self.update_output_location()
        self.ui.left_pushButton_OutputFolder.pressed.connect(self.set_output_location)

        self.output_location_folder = Path(self.output_location).joinpath("videoSmith_output")

        # video list
        self.ui.left_pushButton_loadVideos.pressed.connect(self.load_videos)
        self.ui.left_pushButton_clearVideoList.pressed.connect(self.clear_video_list)

        # live preview
        self.ui.mid_pushButton_startPreview.pressed.connect(self.start_video_preview)
        self.ui.mid_horizontalSlider_frame.valueChanged.connect(self.update_video_preview)
        self.ui.mid_pushButton_updatePreview.setDisabled(True)
        self.ui.mid_pushButton_updatePreview.pressed.connect(self.update_video_preview_hist)

        """
        Enhancement Setup
        """
        # histogram stuff
        self.ui.right_pushButton_calcHist.pressed.connect(self.calculate_histogram)
        self.ui.right_pushButton_equalizeHist.pressed.connect(self.equalize_histogram)
        self.grayframe = None
        self.grayframe_equalized = None
        self.histogram_calculated = False
        self.histogram_equalized = False
        self.ui.right_comboBox_chooseThreshold.setDisabled(True)
        self.use_threshold = False
        self.ui.right_checkBox_useThreshold.toggled.connect(self.update_use_threshold)
        self.threshold_text = " "

        # add threshold items to combobox
        self.ui.right_comboBox_chooseThreshold.addItem("None")
        self.ui.right_comboBox_chooseThreshold.addItem("CLAHE")
        self.ui.right_comboBox_chooseThreshold.currentIndexChanged.connect(self.calculate_histogram)

        # basic corrections
        self.gamma_value = 1
        self.ui.right_horizontalSlider_gamma.valueChanged.connect(self.adjust_gamma)


    """
    Setup and Video Previews
    """

    def updateProgress(self, progress):
        self.progress = progress
        self.ui.right_progressBar.setValue(int(self.progress))

    def log_info(self, info):
        now = datetime.datetime.now()
        self.ui.right_listWidget_info.addItem(now.strftime("%H:%M:%S") + " [INFO] " + info)
        self.ui.right_listWidget_info.sortItems(QtCore.Qt.DescendingOrder)

    def set_output_location(self):
        new_location = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose output location",
                                                                  str(Path.cwd()))
        if new_location:
            self.output_location = new_location

        self.update_output_location()

    def update_output_location(self):
        self.ui.left_lineEdit_outputFolder.setText(self.output_location)

    def add_videos_to_list(self, video_filename):
        self.ui.left_listWidget_videoList.addItem(video_filename)
        self.ui.left_listWidget_videoList.sortItems(QtCore.Qt.DescendingOrder)

    def load_videos(self):
        worker = Worker(self.load_videos_threaded)
        self.threadpool.start(worker)

    def load_videos_threaded(self, progress_callback):
        ### imports
        import tkinter as tk
        import tkinter.filedialog as fd

        root = tk.Tk()
        selected_files = fd.askopenfilenames(parent=root, title="select videos for enhancement with similar issues")

        root.destroy()

        print(selected_files, len(selected_files))

        if len(selected_files) > 0:
            self.log_info(str(len(selected_files)) + " videos selected!")
            self.number_of_videos = len(selected_files)
            self.videolist = selected_files

            # write list of videos to listWidget
            for i, video in enumerate(self.videolist):
                if i < 10:
                    item = "(0" + str(i) + ")" + "  " + video
                    self.add_videos_to_list(item)
                    self.ui.left_comboBox_selectPreview.addItem(item)
                else:
                    item = "(" + str(i) + ")" + "  " + video
                    self.add_videos_to_list(item)
                    self.ui.left_comboBox_selectPreview.addItem(item)

            self.ui.left_listWidget_videoList.sortItems(QtCore.Qt.AscendingOrder)
            self.ui.lcdNumber.display(self.number_of_videos)

    def start_video_preview(self):
        worker = Worker(self.start_video_preview_threaded)
        self.threadpool.start(worker)

    def start_video_preview_threaded(self, progress_callback):
        self.grayframe = None
        self.grayframe_equalized = None
        self.histogram_calculated = False
        self.histogram_equalized = False
        self.gamma_value = 10
        self.ui.right_horizontalSlider_gamma.setValue(10)

        if self.number_of_videos > 0:
            # set initial video preview:
            preview_image, frame_count = handle_video_preview.set_default_preview(self.videolist, self.preview_frame, self.selected_video)

            # update frame count and adjust length of slider:
            self.frame_count = frame_count
            self.ui.mid_horizontalSlider_frame.setMaximum(self.frame_count)
            self.log_info("video " + str(self.selected_video) + " with " + str(self.frame_count) + " frames selected for preview, slider size adjusted")

            preview_image = QtGui.QImage(preview_image.data, preview_image.shape[1], preview_image.shape[0],
                                      QtGui.QImage.Format_RGB888).rgbSwapped()
            # scale image to preview window:
            preview_image_scaled = preview_image.scaled(self.ui.mid_label_livePreview.width(),
                                                     self.ui.mid_label_livePreview.height(),
                                                     QtCore.Qt.KeepAspectRatio)
            self.ui.mid_label_livePreview.setPixmap(QtGui.QPixmap.fromImage(preview_image_scaled))

            # enable change of videos through combo box
            self.ui.left_comboBox_selectPreview.currentIndexChanged.connect(self.update_video_preview_index)
        else:
            self.log_info("Select videos first to start the live preview")

    # update video preview when different frame selected
    def update_video_preview(self, value):
        self.selected_video = self.ui.left_comboBox_selectPreview.currentIndex()
        worker = Worker(self.update_video_preview_threaded, value=value)
        self.threadpool.start(worker)

    def update_video_preview_threaded(self, value, progress_callback):
        self.preview_frame = value
        self.ui.right_horizontalSlider_gamma.setValue(10)   # reset gamma slider
        print("value threaded: ", self.preview_frame)
        preview_image, frame_count = handle_video_preview.set_default_preview(self.videolist, self.preview_frame, self.selected_video)

        self.log_info("frame " + str(self.preview_frame) + " selected for preview")

        preview_image = QtGui.QImage(preview_image.data, preview_image.shape[1], preview_image.shape[0],
                                     QtGui.QImage.Format_RGB888).rgbSwapped()
        # scale image to preview window:
        preview_image_scaled = preview_image.scaled(self.ui.mid_label_livePreview.width(),
                                                    self.ui.mid_label_livePreview.height(),
                                                    QtCore.Qt.KeepAspectRatio)
        self.ui.mid_label_livePreview.setPixmap(QtGui.QPixmap.fromImage(preview_image_scaled))

    # update video preview when different video selected
    def update_video_preview_index(self, value):
        index = self.ui.left_comboBox_selectPreview.currentIndex()
        # reset histogram because chosen video was changed
        self.histogram_calculated = False

        worker = Worker(self.update_video_preview_index_threaded, value=value, index=index)
        self.threadpool.start(worker)

    def update_video_preview_index_threaded(self, value, index, progress_callback):
        self.preview_frame = value
        self.selected_video = index
        preview_image, frame_count = handle_video_preview.set_default_preview(self.videolist, self.preview_frame, self.selected_video)

        self.frame_count = frame_count
        self.ui.mid_horizontalSlider_frame.setMaximum(self.frame_count)

        self.log_info("video " + str(self.selected_video) + " with " + str(self.frame_count) + " frames selected for preview, slider size adjusted")

        preview_image = QtGui.QImage(preview_image.data, preview_image.shape[1], preview_image.shape[0],
                                     QtGui.QImage.Format_RGB888).rgbSwapped()
        # scale image to preview window:
        preview_image_scaled = preview_image.scaled(self.ui.mid_label_livePreview.width(),
                                                    self.ui.mid_label_livePreview.height(),
                                                    QtCore.Qt.KeepAspectRatio)
        self.ui.mid_label_livePreview.setPixmap(QtGui.QPixmap.fromImage(preview_image_scaled))

        # reset histogram stuff
        self.ui.mid_label_histOrig.setText("original histogram")
        self.ui.mid_label_equHist.setText("equalized histogram")
        self.histogram_calculated = False
        self.histogram_equalized = False
        self.grayframe = None
        self.grayframe_equalized = None
        self.ui.mid_pushButton_updatePreview.setDisabled(True)

    def update_video_preview_hist(self):
        # TODO: write new video preview with hist applied to preview frame before display
        worker = Worker(self.update_video_preview_hist_threaded)
        self.threadpool.start(worker)

    def update_video_preview_hist_threaded(self, progress_callback):
        if self.grayframe is None and self.grayframe_equalized is None:
            image = self.preview_frame

        else:
            image = self.grayframe_equalized

        image = QtGui.QImage(image.data, image.shape[1], image.shape[0], QtGui.QImage.Format_Grayscale8)
        # scale image to preview window:
        image_scaled = image.scaled(self.ui.mid_label_livePreview.width(),
                                                      self.ui.mid_label_livePreview.height(),
                                                      QtCore.Qt.KeepAspectRatio)

        # add equalized frame to preview window:
        self.ui.mid_label_livePreview.clear()
        self.ui.mid_label_livePreview.setPixmap(QtGui.QPixmap.fromImage(image_scaled))

    def clear_video_list(self):
        self.ui.left_listWidget_videoList.clear()
        self.number_of_videos = 0
        self.videolist = []
        self.ui.lcdNumber.display(self.number_of_videos)
        self.ui.mid_label_livePreview.setText("video preview disabled")

        # reset histogram stuff
        self.ui.mid_label_histOrig.setText("original histogram")
        self.ui.mid_label_equHist.setText("equalized histogram")
        self.histogram_calculated = False
        self.histogram_equalized = False
        self.grayframe = None
        self.grayframe_equalized = None
        self.ui.mid_pushButton_updatePreview.setDisabled(True)

    """
    Video Enhancements
    """
    # histogram stuff
    def calculate_histogram(self):
        worker = Worker(self.calculate_histogram_threaded)
        self.threadpool.start(worker)

    def calculate_histogram_threaded(self, progress_callback):
        histogram_calculated, grayframe, plot_hist_orig = histograms.calculate_histogram(self.videolist, self.preview_frame, self.selected_video)
        self.histogram_calculated = histogram_calculated
        self.grayframe = grayframe
        self.log_info("histogram calculated for " + self.ui.left_comboBox_selectPreview.currentText())

        # add histogram plot to label:
        plot_hist_orig = QtGui.QImage(plot_hist_orig.data, plot_hist_orig.shape[1], plot_hist_orig.shape[0],
                                     QtGui.QImage.Format_RGB888).rgbSwapped()
        # scale image to preview window:
        plot_hist_orig_scaled = plot_hist_orig.scaled(self.ui.mid_label_histOrig.width(),
                                                    self.ui.mid_label_histOrig.height(),
                                                    QtCore.Qt.KeepAspectRatio)
        self.ui.mid_label_histOrig.setPixmap(QtGui.QPixmap.fromImage(plot_hist_orig_scaled))

    def equalize_histogram(self):
        worker = Worker(self.equalize_histogram_threaded)
        self.threadpool.start(worker)

    def equalize_histogram_threaded(self, progress_callback):
        use_threshold = self.use_threshold
        self.threshold_text = self.ui.right_comboBox_chooseThreshold.currentText()
        info, grayframe_equalized, histogram_calculated, plot_hist_equ = histograms.equalize_histogram(self.histogram_calculated, self.grayframe, use_threshold, self.threshold_text)
        self.log_info(info)
        self.histogram_calculated = histogram_calculated
        self.grayframe_equalized = grayframe_equalized

        plot_hist_equ = QtGui.QImage(plot_hist_equ.data, plot_hist_equ.shape[1], plot_hist_equ.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        # scale image to preview window:
        plot_hist_equ_scaled = plot_hist_equ.scaled(self.ui.mid_label_equHist.width(),
                                                    self.ui.mid_label_equHist.height(),
                                                    QtCore.Qt.KeepAspectRatio)
        # add histogram plot to label:
        self.ui.mid_label_equHist.setPixmap(QtGui.QPixmap.fromImage(plot_hist_equ_scaled))


        self.histogram_equalized = True
        self.ui.mid_pushButton_updatePreview.setEnabled(True)

    def update_use_threshold(self):
        worker = Worker(self.update_use_threshold_threaded)
        self.threadpool.start(worker)

    def update_use_threshold_threaded(self, progress_callback):
        if self.ui.right_checkBox_useThreshold.isChecked():
            self.use_threshold = True
            self.ui.right_comboBox_chooseThreshold.setEnabled(True)
            self.ui.mid_label_histOrig.setText("original histogram")
            self.ui.mid_label_equHist.setText("equalized histogram")
            self.log_info("Calculate histogram and equalize again, then update preview")
        else:
            self.use_threshold = False
            self.ui.right_comboBox_chooseThreshold.setDisabled(True)
            self.grayframe = None
            self.grayframe_equalized = None
            self.histogram_calculated = False
            self.histogram_equalized = False
            self.ui.right_comboBox_chooseThreshold.setCurrentIndex(0)
            self.ui.mid_label_histOrig.setText("original histogram")
            self.ui.mid_label_equHist.setText("equalized histogram")

    # gamma
    def adjust_gamma(self, value):
        worker = Worker(self.adjust_gamma_threaded, value=value)
        self.threadpool.start(worker)

    def adjust_gamma_threaded(self, value, progress_callback):
        self.gamma_value = value
        preview_image = basic_corrections.change_gamma(self.videolist, self.preview_frame, self.selected_video, self.gamma_value)

        preview_image = QtGui.QImage(preview_image.data, preview_image.shape[1], preview_image.shape[0],
                                     QtGui.QImage.Format_RGB888).rgbSwapped()
        # scale image to preview window:
        preview_image_scaled = preview_image.scaled(self.ui.mid_label_livePreview.width(),
                                                    self.ui.mid_label_livePreview.height(),
                                                    QtCore.Qt.KeepAspectRatio)
        self.ui.mid_label_livePreview.setPixmap(QtGui.QPixmap.fromImage(preview_image_scaled))



if __name__ == "__main__":
    # (for debugging only, to report errors to the console)
    #cgitb.enable(format='text')
    app = QtWidgets.QApplication([])

    application = videoSmith_mainWindow()

    application.show()

    sys.exit(app.exec())