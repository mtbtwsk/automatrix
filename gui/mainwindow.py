# matrixgenerator.gui.mainwindow.py
import tkinter as tk
from .dnd import dndListbox
from .handlers.data import data_handler
import pandas as pd, numpy as np
import os

class mainwindow:
    '''
    The main interface of the program: a single window
    containing several frames in which the user can
    enter their specifications for the output document.
    '''

    def __init__(self,root,csv_reader,writer):
        self.menu = root
        self.menu.title('AutoMatrix')

        self.reader = csv_reader
        self.writer = writer    #For now this is CSV but in the future will be xlsx

        '''
        The mainwindow tracks the columns read in from the CLSS
        .csv files (self.columns), as well as various user-configurable
        settings (all set to False by default; name format defaults 
        to 'Lastname'.
        '''
        self.columns = []
        self.settings = {
            'filenames'          : tk.StringVar(value='Selected input files \
                                                      will appear here.'),

            'kept_columns'       : [],

            'views'              : {'default'       : ['Course Schedule',tk.BooleanVar(value=True)],
                                   'by_instructor'  : ['Instructor Schedule', tk.BooleanVar(value=True)],
                                   'by_day'         : ['Daily Schedule', tk.BooleanVar(value=True)],
                                   'graphical'      : ['Graphical Schedule', tk.BooleanVar(value=True)] },

            'name'               : tk.StringVar(value='Firstname Lastname'),

            'checkboxes'         : {'mergeTAs'           : ['Include TAs in Instructor Column',
                                                            lambda : self.toggle_mergeTAs(),
                                                            tk.BooleanVar(value=False)],
                                    'combine_crosslisted': ['Include Xlists in Course Column',
                                                            lambda : self.toggle_combine_crosslisted(),
                                                            tk.BooleanVar(value=False)],
                                    'separatetitles'     : ['Separate Columns for Title and Topic',
                                                            lambda : self.toggle_separatetitles(),
                                                            tk.BooleanVar(value=False)],
                                    'excludediscussion'  : ['Exclude Discussion Sections',
                                                            lambda : None,
                                                            tk.BooleanVar(value=False)],
                                    'excludelaboratory'  : ['Exclude Laboratory Sections',
                                                            lambda : None,
                                                            tk.BooleanVar(value=False)]
                                    }
        }
        
        self.flags = {
            'has_read_file'         : False
        }

        #Placing three frames: Top, left, and right
        self.top_frame = tk.Frame(root,
                                  pady = 5,
                                  padx = 5
                                  )
        self.top_frame.grid(row = 0,
                            columnspan = 3,
                            sticky = 'ew'
                            )
        self.left_frame = tk.LabelFrame(root,
                                        height = '600px',
                                        pady = 5,
                                        padx = 5,
                                        text = 'Matrix Settings',
                                        borderwidth = 1,
                                        highlightthickness = 5
                                        )
        self.left_frame.grid(row = 1,
                             rowspan=2,
                             column = 0,
                             sticky = 'ns'
                             )
        self.left_frame.grid_rowconfigure(1,weight=1)
        self.left_frame.grid_rowconfigure(2,weight=1)

        self.right_frame = tk.LabelFrame(root,
                                         height = '600px',
                                         pady = 5,
                                         padx=20,
                                         text='Export Settings',
                                         borderwidth=1,
                                         highlightthickness=5
                                         )
        self.right_frame.grid(row = 1,
                              column = 1,
                              sticky = 'nsew'
                              
                              )

        self.advanced_settings = tk.LabelFrame(self.menu,
                                               text='More Settings',
                                               pady = 5,
                                               padx=20,
                                               borderwidth=1,
                                               highlightthickness=5
                                               ) 
        
        self.advanced_settings.grid(row = 2,
                                    column = 1,
                                    sticky = 'nsew')
    

        #The top frame contains read/write tools
        ##Button to read in files
        self.read_button = tk.Button(self.top_frame,
                                     text='Select files...', 
                                     command=lambda : self.read()
                                     )
        self.read_button.pack(side='left')

        ##Filenames displayed in a string
        self.selected_files_display = tk.Label(
            self.top_frame,
            textvariable=self.settings['filenames']
            )
        self.selected_files_display.pack(side='left')

        ##Button to write to disk
        self.write_button = tk.Button(self.top_frame,
                                      text="Export...", 
                                      command=lambda : self.write()
                                      )
        self.write_button.pack(side='right')


        #The left frame contains the column-selection widgets
        ## Labels for column listboxes
        self.kept_items_label = tk.Label(self.left_frame,
                                         text="Fields to keep in course matrix"
                                         )
        self.kept_items_label.grid(row=0,
                                   column=0,
                                   sticky='n'
                                   )
        self.discarded_items_label = tk.Label(self.left_frame,
                                              text = ''
                                              )
        self.discarded_items_label.grid(row=0,
                                        column=3
                                        )

        ## Listboxes and scrollbars
        self.kept_scroll = tk.Scrollbar(self.left_frame, 
                                        orient="vertical",
                                        )              
        self.kept_items = dndListbox(self.left_frame, 
                                     selectmode="single",
                                     yscrollcommand=self.kept_scroll.set,
                                     borderwidth=0, highlightthickness=0
                                     )
        self.kept_scroll.config(command=self.kept_items.yview)
        self.kept_items.grid(row=1, 
                             column=0, 
                             rowspan=2, 
                             pady=5, 
                             sticky='nsew'
                             )
        self.kept_scroll.grid(row=1, 
                              column=1, 
                              rowspan=2, 
                              pady=5, 
                              sticky='nsew'
                              )
        
        self.discarded_scroll = tk.Scrollbar(self.left_frame, 
                                             orient="vertical"
                                             )
        self.discarded_items = tk.Listbox(self.left_frame, 
                                          selectmode="single",
                                          yscrollcommand=self.discarded_scroll.set,
                                        borderwidth=0, highlightthickness=0,
                                          )
        self.discarded_scroll.config(command=self.discarded_items.yview)
        self.discarded_items.grid(row=1,
                                  column=3,
                                  rowspan=2, 
                                  pady=5, 
                                  sticky='nsew'
                                  )
        self.discarded_scroll.grid(row=1, 
                                   column=4, 
                                   rowspan=2, 
                                   pady=5, 
                                   sticky='nsew'
                                   )

        ## Buttons to move items between listboxes
        self.keep_button = tk.Button(self.left_frame, text="<",
                                     command=lambda : self.move_item(
                                         self.discarded_items,self.kept_items))
        self.keep_button.grid(row=1,column=2,sticky='s')
        self.discard_button = tk.Button(self.left_frame, text=">",
                                        command=lambda : self.move_item(
                                            self.kept_items,self.discarded_items))
        self.discard_button.grid(row=2,column=2,sticky='n')

        #Right frame contains settings
        ##Label for view options
        self.views_label = tk.Label(self.right_frame, 
                                    text="Select matrix styles to export:",
                                    width=30,
                                    anchor='w'
                                    )
        self.views_label.pack(anchor='w')

        ##Checkboxes for view options
        for entry in self.settings['views']:
            checkbox = tk.Checkbutton(self.right_frame,
                                      text=self.settings['views'][entry][0], 
                                      variable=self.settings['views'][entry][1]
                                      )
            checkbox.pack(anchor='w')

        ##Label for name settings
        name_options_label = tk.Label(self.right_frame,
                                      text='Name format:'
                                      )
        name_options_label.pack(anchor='w')

        ##Radio buttons for name settings
        name_options = ['Firstname Lastname', 'Lastname', 'Lastname, Firstname']
        for option in name_options:
            rad = tk.Radiobutton(self.right_frame,text=option,value=option,variable=self.settings['name'])
            rad.pack(anchor='w')


        ##Advanced settings frame
        self.advanced_settings_button_text = tk.StringVar(value='Show Advanced Settings')
        self.advanced_settings_button = tk.Button(self.right_frame,
                                                  textvariable=self.advanced_settings_button_text,
                                                  command=lambda : self.toggle_advanced_settings())
        #self.advanced_settings_button.pack(anchor='w')
        ##Checkbox 
        for _, entry in self.settings['checkboxes'].items():
            checkbox = tk.Checkbutton(self.advanced_settings,
                                    wraplength=f'{self.views_label.winfo_reqwidth()-40}',
                                    text=entry[0],
                                    command=entry[1],
                                    variable=entry[2],
                                    onvalue=True, offvalue=False)
            checkbox.pack(anchor='w')

        #Populate fields with initialized values
        self.populate()


    def move_item(self,source,destination):
        # get selected item index
        selected = source.curselection()
        # get the text of the selected item
        selected_text = source.get(selected)
        # delete the selected item from listbox1
        source.delete(selected)
        # add the selected item to listbox2
        destination.insert(selected, selected_text)
        self.settings['kept_columns'] = self.kept_items.get(0,tk.END)


    def populate(self):
    # Function to populate menus with appropriate items.
        self.kept_items.delete(0,tk.END)
        self.discarded_items.delete(0,tk.END)
        filenames_list = [os.path.basename(filepath) for filepath in self.reader.filepaths]
        self.settings['filenames'].set(", ".join(filenames_list))
        
        # Create a list of the columns that are not in 'kept_columns'
        other_columns = [col for col in self.columns if col not in self.settings['kept_columns']]

        # Concatenate the 'kept_columns' with the sorted 'other_columns'
        self.columns = self.settings['kept_columns'] + other_columns

        #Then we add items to their listboxes:
        for value in self.columns:
            (self.kept_items.insert(tk.END, value) 
            if value in self.settings['kept_columns'] 
            else self.discarded_items.insert(tk.END, value))

    def read(self):
        #Function for reading in files.

        #Read in files with reader, combine them into a df
        self.reader.select_files()
        self.reader.combine_csv()

        #Pass df from reader to handler
        self.handler = data_handler(self.reader.df)
        self.handler.filepaths = self.reader.filepaths
        self.handler.data = self.reader.df


        #Data preparation
        self.handler.delete_singletons()
        self.handler.move_TAs()

        #If a section has TAs but no instructor, treat TAs as primary instructor
        self.handler.data.loc[self.handler.data['Instructor'].isna(), 'Teaching Assistant'] = np.nan
        self.handler.data['Instructor'].fillna(self.handler.data['Teaching Assistant'], inplace=True)

        self.handler.cleanup()
        self.handler.extract_names('Instructor')
        self.handler.extract_names('Teaching Assistant')
        self.handler.get_meetings()

        self.columns = self.handler.data.columns.tolist()

        #Since the Topic column gets combined with Title by default, we remove Topic
        #before generating the list of columns. Otherwise it would show up as a possible
        #column without being able to appear in the output.
        if not self.flags['has_read_file']: self.columns.remove('Topic')

        self.populate()

        #Flag to indicate that a file has been read in
        self.flags['has_read_file'] = True


    def run(self):
        self.menu.mainloop()


    def toggle_combine_crosslisted(self):
    # Remove and add the Crosslisted column when check button is toggled
        if self.flags['has_read_file']:
            if self.settings['checkboxes']['combine_crosslisted'][2].get():
                self.columns.remove('Crosslisted')
                try:
                    self.settings['kept_columns'].remove('Crosslisted')
                except ValueError:
                    pass
            else:
                self.columns.insert(0,'Crosslisted')
            self.populate()
        else: pass

    def toggle_mergeTAs(self):
    # Remove and add the TA column when check button is toggled
        if self.flags['has_read_file']:
            if self.settings['checkboxes']['mergeTAs'][2].get():
                self.columns.remove('Teaching Assistant')
                try:
                    self.settings['kept_columns'].remove('Teaching Assistant')
                except ValueError:
                    pass
            else:
                self.columns.insert(0,'Teaching Assistant')
            self.populate()
        else: pass


    def toggle_separatetitles(self):
    # Remove and add the Topic column when check button is toggled
        if self.flags['has_read_file']:
            if self.settings['checkboxes']['separatetitles'][2].get():
                self.columns.insert(0,'Topic')
            else:
                self.columns.remove('Topic')
                try:
                    self.settings['kept_columns'].remove('Topic')
                except ValueError:
                    pass
            self.populate()
        else: pass

    def write(self):
    #Raise an error if the user didn't select any outputs
        if all(not value[1].get() for value in self.settings['views'].values()):
            raise ValueError('No output views selected.')

    #Get a list of instructor names to use for Instructor View
        instructornames = self.handler.instructor_names(self.settings['name'].get(), self.handler.data['Instructor'].tolist())

    #Sort rows by Term
        self.handler.sort_terms()

    #Rename instructors, try renaming TAs unless TAs are not being kept
        self.handler.rename(self.settings['name'].get(), 'Instructor')
        try:
            self.handler.rename(self.settings['name'].get(), 'Teaching Assistant')
        except KeyError:
            pass

        self.settings['kept_columns'] = self.kept_items.get(0,tk.END)
        self.settings['kept_columns'] = list(self.settings['kept_columns'])

    #Apply checkbox settings
        #Separate titles?
        if not self.settings['checkboxes']['separatetitles'][2].get():
            self.handler.data['Title'] = self.handler.data.apply(lambda row: 
                                                                 row['Topic'] if pd.notna(row['Topic']) 
                                                                 else row['Title'], axis=1)
            self.handler.data.drop(['Topic'],axis=1, inplace=True)
        
        #Exclude discussion sections?
        if self.settings['checkboxes']['excludediscussion'][2].get():
            self.handler.data = self.handler.data[~self.handler.data['Section Type'].isin(['Discussion'])]

        #Exclude lab sections?
        if self.settings['checkboxes']['excludelaboratory'][2].get():
            self.handler.data = self.handler.data[~self.handler.data['Section Type'].isin(['Laboratory'])]

        #Combine crosslists with course #s?
        if self.settings['checkboxes']['combine_crosslisted'][2].get():
            self.handler.data['Crosslisted'].astype(str).dropna()
            self.handler.data['Course'] = self.handler.data['Course'].astype(str) + ' (' + self.handler.data['Crosslisted'].fillna('').astype(str)+')'
            self.handler.data['Course'] = self.handler.data['Course'].astype(str).apply(remove_trailing_parentheses).str.strip()
    
        #Combine TAs with instructors?
        if self.settings['checkboxes']['mergeTAs'][2].get():
            self.handler.data['Instructor'] = self.handler.data['Instructor']+' ('+self.handler.data['Teaching Assistant']+')'
            self.handler.data['Instructor'] = self.handler.data['Instructor'].apply(remove_trailing_parentheses).str.strip()
            try:
                self.handler.data.drop(['Teaching Assistant'],axis=1,inplace=True)
            except:
                pass
    #'Suppressed data' is a df that's kept alongside self.handler.data but whose contents
    #are not made visible to the user, as they can't be put in the output.
    #'Term' is a suppressed column because all the output sheets are dfs by Term.
    #'Meetings' is suppressed because it contains structured info about meetings,
    #not just strings like 'MW3pm-3:20pm'
        self.suppressed_data = self.handler.data[['Term','Meetings']]

    #Drop columns not specified by user and reorder according to user pref
        self.handler.data = self.handler.data.reindex(columns=self.settings['kept_columns'])

    #Hand off to writer
        self.writer.data = self.handler.data
        self.writer.compile_excel(self.writer.data, self.settings['views'],instructornames, self.suppressed_data)
        self.writer.write_excel()

def remove_trailing_parentheses(s):
    return s[:-3] if s.endswith(' ()') else s