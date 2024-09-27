import h5py
import os
from tkinter import Tk  # use tkinter to open files
from tkinter.filedialog import askopenfilename, askdirectory
import subprocess

def open_dir(title: str = "Select data directory", ending_slash: bool = False) -> str:
    """
    Opens a tkinter dialog to select a folder. Returns the path of the folder.
    :param title: The message to display in the open directory dialog.
    :return: the absolute path of the directory selected.
    """
    root = Tk()
    # dialog should open on top. Only works for Windows?
    root.attributes("-topmost", True)
    root.withdraw()  # keep root window from appearing
    folder_path = askdirectory(title=title)
    if ending_slash:
        folder_path += "/"
    return os.path.normpath(folder_path)


fold = open_dir("Select directory of .acq files")
output_fold = open_dir("Select folder to export .hdf5 files")
assert os.path.exists(fold)
assert os.path.exists(output_fold)
assert fold != "."  # quit on pressing cancel (most likely reason for "." folder)

for root, folders, files in os.walk(fold):
    for file in files:
        file_name, file_ext = os.path.splitext(file)
        if file_ext == ".acq":
            fpath_full_acq = os.path.join(root, file) 
            fpath_full_hdf5 = os.path.join(output_fold, file_name + ".hdf5")
            if not os.path.exists(fpath_full_hdf5):
                print(f"Converting {fpath_full_acq}...")
                subprocess.run(["acq2hdf5", fpath_full_acq, fpath_full_hdf5])
                print(f"Saved to {fpath_full_hdf5}")
            else:
                print(f"Skipping already converted {fpath_full_acq}")