# matrixgenerator.gui.handlers.csv.py

import pandas as pd
#from tkinter import filedialog

class clssreader:
    def __init__(self):
        self.filepaths = []
        self.df = pd.DataFrame()

    def combine_csv(self,filepaths):
        # Initialize an empty list to store DataFrames
        data_frames = []
        if filepaths == []:
            ValueError('No files selected')
        for path in filepaths:
            # Skip the first two rows and read the data
            data = pd.read_csv(path, skiprows=2)
            #Append to data_frames
            data_frames.append(data)
        output = pd.concat(data_frames, ignore_index=True)
        output.rename(columns={'Maximum Enrollment': 'Cap', 
                               'Section #': 'Sec.', 
                               'Combined': 'Crosslisted', 
                               'Meeting Pattern': 'Schedule',
                               'Course Title': 'Title',
                               },
                               inplace=True)
        self.df = output