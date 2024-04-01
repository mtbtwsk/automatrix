# matrixgenerator.main.py
import pandas as pd
import sys,os
import tkinter as tk
from gui.mainwindow import mainwindow
#Suppress warnings about editing pandas copy vs view
pd.options.mode.chained_assignment = None  # default='warn'

root = tk.Tk()

def main():
    window = mainwindow(root)
    window.run()

if __name__ == "__main__":
    main()