import tkinter as tk
from handlers.csv import clssreader, CSVwriter
from gui.mainwindow import mainwindow
# Default columns to retain
default_columns = ['Term','Meetings', 'Course','Section #','Course Title','Section Type','Teaching Assistant', 
                    'Meeting Pattern','Instructor','Room','Maximum Enrollment','Combined']
# Selectable output views
views = ['Course schedule','Instructor schedule','Daily schedule']

def main():
    root = tk.Tk()
    reader = clssreader()
    writer = CSVwriter()

    window = mainwindow(root,reader,writer)
    window.defaultcolumns = default_columns
    window.views = views
    window.run()

if __name__ == "__main__":
    main()