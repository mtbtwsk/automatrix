import tkinter as tk
from .dnd import dndListbox
from ..handlers import data
import os

class mainwindow:
    def __init__(self,root,csv_reader,csv_writer):
        self.reader = csv_reader
        self.writer = csv_writer    #For now this is CSV but in the future will be xlsx
        self.menu = root
        self.defaultcolumns = []    
        self.views = ['Course schedule','Instructor schedule','Daily schedule']
        self.menu.title("Matrix Organizer")
        self.selected_filenames = tk.StringVar()
        self.selected_filenames.set('Selected input files will appear here.')

        #Three frames: top, left, and right
        self.top_frame = tk.Frame(root,pady=5,padx=5)
        self.top_frame.grid(row=0,columnspan=3,sticky='ew')
        self.left_frame = tk.LabelFrame(root,height='600px',pady=5,padx=5,text='Matrix Settings',
                                        borderwidth=1,highlightthickness=5)
        self.left_frame.grid(row=1,column=0,sticky='ns')        
        self.right_frame = tk.LabelFrame(root,height='600px',pady=5,padx=20,text='Export Settings',borderwidth=1,highlightthickness=5)
        self.right_frame.grid(row=1,column=1,sticky='ns')


        #The top frame contains read/write tools
        ##Button to read in files
        self.read_button = tk.Button(self.top_frame, text='Select files...', command=lambda : self.read())
        self.read_button.pack(side='left')

        ##Filenames displayed in a string
        self.selected_files_display = tk.Label(self.top_frame, textvariable=self.selected_filenames)
        self.selected_files_display.pack(side='left')

        ##Button to write to disk
        self.write_button = tk.Button(self.top_frame,text="Export...", command=lambda : self.save())
        self.write_button.pack(side='right')


        #The left frame contains the column-selection widgets
        ## Labels for column listboxes
        self.kept_items_label = tk.Label(self.left_frame, text="Fields to keep in course matrix")
        self.kept_items_label.grid(row=0,column=0)
        self.discarded_items_label = tk.Label(self.left_frame, text="")
        self.discarded_items_label.grid(row=0,column=3)

        ## Listboxes
        self.kept_scroll = tk.Scrollbar(self.left_frame, orient="vertical")
        self.kept_items = dndListbox(self.left_frame, selectmode="single",yscrollcommand=self.kept_scroll.set)

        self.kept_scroll.config(command=self.kept_items.yview)
        self.kept_items.grid(row=1, column=0, rowspan=2, pady=5, sticky='nsew')
        self.kept_scroll.grid(row=1, column=1, rowspan=2, pady=5, sticky='ns')
        self.discarded_scroll = tk.Scrollbar(self.left_frame, orient="vertical")
        self.discarded_items = dndListbox(self.left_frame, selectmode="single",
                                          yscrollcommand=self.discarded_scroll.set)
        self.discarded_scroll.config(command=self.discarded_items.yview)
        self.discarded_items.grid(row=1,column=3,rowspan=2, pady=5, sticky='nsew')
        self.discarded_scroll.grid(row=1, column=4, rowspan=2, pady=5, sticky='ns')

        ## Buttons to move items between listboxes
        self.keep_button = tk.Button(self.left_frame, text="<")
        self.keep_button.grid(row=2,column=2)
        self.discard_button = tk.Button(self.left_frame, text=">")
        self.discard_button.grid(row=1,column=2)


        #Right frame contains export settings
        ##Label for view options
        self.views_label = tk.Label(self.right_frame, text="Select matrix styles to export:")
        self.views_label.pack(anchor='w')

        ##Checkboxes for view options
        view_checkbox_list = []
        view_checkbox_var_list = []
        for view in self.views:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(self.right_frame,text=view, variable=var)
            var.set=(True)
            view_checkbox_list.append(checkbox)
            view_checkbox_var_list.append(var)
        for chk in view_checkbox_list:
            chk.pack(anchor='w')

        ##Label for name settings
        name_options_label = tk.Label(self.right_frame,text='Name output format:')
        name_options_label.pack(anchor='w')

        ##Radio buttons for name settings
        name_options = ['Last', 'Last, First', 'First Last']
        self.name_variable = tk.StringVar(value='Last')
        for option in name_options:
            rad = tk.Radiobutton(self.right_frame,text=option,value=option,variable=self.name_variable,command=lambda : self.handler.rename(self.name_variable.get()))
            rad.pack(anchor='w')

        ##Label for other settings (checkbox)
        other_settings_label = tk.Label(self.right_frame,text='Other settings:')

        ##Radio buttons for name settings
        self.split_TAs_flag = tk.BooleanVar()
        self.split_TAs_flag.set(True)
        split_TAs_checkbox = tk.Checkbutton(self.right_frame,text='Put TAs in separate column (recommended)',
                                            variable=self.split_TAs_flag,onvalue=True,offvalue=False)
        other_settings_label.pack(anchor='w')
        split_TAs_checkbox.pack(anchor='w')

        #Populate fields with initialized values
        self.populate()

    def run(self):
        self.menu.mainloop()

    def read(self):
        #Read in files with reader, combine them into a df
        self.reader.select_files()
        self.reader.combine_csv()

        #Pass df from reader to handler
        self.handler = data.data_handler(self.reader.df)
        self.handler.files = self.reader.files
        self.handler.data = self.reader.df

        ##Delete singleton rows (These are typically class or instructor names)
        self.handler.delete_singletons()

        ##Split TAs from Instructor column, move to Teaching Assistant column
        self.handler.move_TAs()
        
        ##Do a bunch of cleaning
        self.handler.cleanup()

        self.handler.get_meetings()

        #Populate fields with read-in values
        self.populate()

    def save(self):
        ##Sort courses by term
        self.handler.sort_terms()

        ##Drop columns selected by user, hand off to writer, and save file
        self.handler.drop_columns(self.kept_items.get(0, tk.END))
        self.writer.data = self.handler.data
        self.writer.write_file()

    def populate(self):
        try:
            filenames = [os.path.basename(file_path) for file_path in self.reader.files]
            self.column_names = self.handler.data.columns.tolist()
            if self.reader.files == []:
                pass
            else:
                self.selected_filenames.set(", ".join(filenames))
            self.kept_items.delete(0,'end')
            self.discarded_items.delete(0,'end')
            for value in self.column_names:
                self.kept_items.insert(tk.END, value) if value in self.defaultcolumns else self.discarded_items.insert(tk.END, value)
        except AttributeError:
            pass

    def filter_by_selection(self,df):
        selected = list(self.kept_items.get(0,tk.END))
        output = df[selected]
        return output