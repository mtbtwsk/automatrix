# matrixgenerator.main.py
import tkinter as tk
import pandas as pd
from gui.handlers.csv import clssreader
from gui.handlers.excel import xlwriter
from gui.mainwindow import mainwindow

#Suppress warnings about editing pandas copy vs view
pd.options.mode.chained_assignment = None  # default='warn'

# Default columns to retain (in the listed order)
default_columns = ['Course','Sec.','Crosslisted','Title',
                   'Schedule','Instructor','Teaching Assistant',
                   'Room','Cap','Section Type']

def main():
    root = tk.Tk()
    reader = clssreader()
    writer = xlwriter()

    window = mainwindow(root,reader,writer)
    window.settings['kept_columns'] = default_columns
    window.run()

if __name__ == "__main__":
    main()