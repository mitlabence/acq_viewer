from matplotlib.pyplot import figure, show
import numpy
import os
import h5py
import numpy as np
from tkinter import Tk  # use tkinter to open files
from tkinter.filedialog import askopenfilename, askdirectory

def open_file(title: str = "Select file") -> str:
    """
    Opens a tkinter dialog to select a file. Returns the path of the file.
    :param title: The message to display in the open directory dialog.
    :return: the absolute path of the directory selected.
    """
    root = Tk()
    # dialog should open on top. Only works for Windows?
    root.attributes("-topmost", True)
    root.withdraw()  # keep root window from appearing
    return os.path.normpath(askopenfilename(title=title))

class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None
        self.ctl_pressed = False

    def zoom_factory(self, ax, base_scale=2.):
        def onKeyPressed(event):
            if event.key == "control":
                self.ctl_pressed = True
        def onKeyReleased(event):
            if event.key == "control":
                self.ctl_pressed = False
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location
            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])
            if self.ctl_pressed:
                ax.set_ylim([ydata - new_height * (1-rely),
                            ydata + new_height * (rely)])            
            else:
                ax.set_xlim([xdata - new_width * (1-relx),
                            xdata + new_width * (relx)])
            ax.figure.canvas.draw()

        fig = ax.get_figure()  # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)
        fig.canvas.mpl_connect("key_press_event", onKeyPressed)
        fig.canvas.mpl_connect("key_release_event", onKeyReleased)
        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax:
                return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.press is None:
                return
            if event.inaxes != ax:
                return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)

            ax.figure.canvas.draw()

        fig = ax.get_figure()  # get the figure of interest

        # attach the call back
        fig.canvas.mpl_connect('button_press_event', onPress)
        fig.canvas.mpl_connect('button_release_event', onRelease)
        fig.canvas.mpl_connect('motion_notify_event', onMotion)

        # return the function
        return onMotion


# convert .acq file with bioread CLI command acq2hdf5
fpath_eeg = open_file("Select EEG .hdf5 file to plot!")
assert os.path.exists(fpath_eeg)

with h5py.File(fpath_eeg, "r") as hf:
    # check beforehand if this is the dataset structure
    eeg_data = hf["channels"]["channel_0"][()]
    eeg_sr = hf.attrs["samples_per_second"]
eeg_data = np.max(eeg_data) - eeg_data  # mirror to have large positive spikes

ts_eeg = np.arange(len(eeg_data))/eeg_sr

fig = figure()


ax = fig.add_subplot(111, xlim=(  # plot 5 minutes = 360 s
    ts_eeg[0], ts_eeg[360*2000]), ylim=(np.min(eeg_data), np.max(eeg_data)), autoscale_on=False)


ax.plot(ts_eeg, eeg_data, linewidth=0.5)
scale = 1.1
zp = ZoomPan()
figZoom = zp.zoom_factory(ax, base_scale=scale)
figPan = zp.pan_factory(ax)
show()
