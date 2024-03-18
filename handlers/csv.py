import pandas as pd
from tkinter import filedialog

class clssreader:
    def __init__(self):
        self.read_flag = False
        self.files = []
        self.df = pd.DataFrame()

    def select_files(self):
        self.files = filedialog.askopenfilenames(
        title="Select CSV files",
        filetypes=(("CSV files", "*.csv"), ("all files", "*.*"))
        )
        self.read_flag = True

    def combine_csv(self):
        # Initialize an empty list to store DataFrames
        data_frames = []
        if self.files == []:
            ValueError('No files selected')
        for file_path in self.files:
            # Skip the first two rows and read the data
            data = pd.read_csv(file_path, skiprows=2)
            #Append to data_frames
            data_frames.append(data)
        output = pd.concat(data_frames, ignore_index=True)
        self.df = output
    
class CSVwriter:
    def __init__(self,initial_df=None):
        if initial_df is None:
            self.data = pd.DataFrame()
        else:
            self.data = initial_df
    def write_file(self):
        file_path = filedialog.asksaveasfilename(initialfile='matrix.csv',defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        self.data.to_csv(file_path, index=False)