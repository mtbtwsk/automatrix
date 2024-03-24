import pandas as pd
from tkinter import filedialog
import openpyxl as xl
from openpyxl.styles import Alignment,Font,PatternFill
from openpyxl import Workbook

class xlwriter:
    def __init__(self):
        self.dataframes = {}
        self.wb = Workbook()
    
    def write_excel(self):
        filepath = filedialog.asksaveasfilename(initialfile='matrix.xlsx',defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        self.wb.save(filepath)

    def compile_excel(self, df, views, names, suppressed_data):
        self.data = df
        complete_data = self.data.join(suppressed_data)
        first = True

        #Create a two dictionaries for getting abbreviations from days or vice versa
        days_dict = {'Monday': 'M', 'Tuesday': 'T', 
                      'Wednesday': 'W', 'Thursday': 'Th', 'Friday':'F'}

        for key, view in views.items():

            #Check if we're on the first sheet. If not, append
            #a new sheet and write to that
            if view[1].get() and first:
                self.ws = self.wb.active
                self.ws.title = view[0]

            elif view[1].get():
                self.ws = self.wb.create_sheet()
                self.ws.title = view[0]
            first = False

            #Write 'Course Schedule' sheet
            if key == 'default' and view[1].get():
                for term in suppressed_data['Term'].unique():

                    #Add the Term row
                    self.ws.append([term])

                    #Format the Term row
                    for col in range(1, len(self.data.columns.tolist())+1):
                        self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='808080')
                        self.ws.cell(self.ws.max_row, column=col).font = Font(size=20,bold=True)
                    self.ws.row_dimensions[self.ws.max_row].height = 30


                    
                    mask = complete_data['Term'] == term
                    new_df = self.data[mask].copy()
                    #new_df.drop(['Term'], axis=1,inplace=True)


                    #Add the columns row
                    self.ws.append(new_df.columns.tolist())

                    #Format the columns row
                    self.ws.row_dimensions[self.ws.max_row].height = 15
                    for col in range(1, len(self.data.columns.tolist())+1):
                        self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='A9A9A9')
                        self.ws.cell(self.ws.max_row, column=col).font = Font(italic=True)

                    count = 0
                    for _, row in new_df.iterrows():
                        self.ws.append(row.tolist())
                        for col in range(1, len(self.data.columns.tolist())+1):
                            if count % 2 == 0:
                                self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='E8E8E8')
                            else:
                                self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='D3D3D3')
                            self.ws.row_dimensions[self.ws.max_row].height = 30
                        count += 1
                    self.ws.append([])

                self.auto_resize(self.ws)
                self.merge_headers(self.ws,complete_data['Term'].unique(),len(self.data.columns.tolist()))

            #Write the 'By Instructor' sheet
            if key == 'by_instructor' and view[1].get():
                for term in suppressed_data['Term'].unique():

                    #Add the term row
                    self.ws.append([term])

                    #Format the Term row
                    for col in range(1, len(self.data.columns.tolist())+1):
                        self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='808080')
                        self.ws.cell(self.ws.max_row, column=col).font = Font(size=20,bold=True)
                    self.ws.row_dimensions[self.ws.max_row].height = 30

                    for name in names:
                        mask = (complete_data['Term'] == term) & (complete_data['Instructor'] == name)
                        new_df = self.data[mask].copy()
                        new_df.drop(['Instructor'], axis=1,inplace=True)

                        if not new_df.empty:
                            self.ws.append([name])

                            #Format the name row
                            for col in range(1, len(self.data.columns.tolist())+1):
                                self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='A9A9A9')
                                self.ws.cell(self.ws.max_row, column=col).font = Font(bold=True)
                            
                            #Format the dataframe to add under Instructor Name

                            #Add the columns row
                            self.ws.append(new_df.columns.tolist())

                            #Format the columns row
                            for col in range(1, len(self.data.columns.tolist())+1):
                                self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='A9A9A9')
                                self.ws.cell(self.ws.max_row, column=col).font = Font(italic=True)

                            count = 0
                            for _, row in new_df.iterrows():
                                self.ws.append(row.tolist())
                                for col in range(1, len(self.data.columns.tolist())+1):
                                    if count % 2 == 0:
                                        self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='E8E8E8')
                                    else:
                                        self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='D3D3D3')
                                self.ws.row_dimensions[self.ws.max_row].height = 30
                                count += 1
                    self.ws.append([])
                    self.ws.append([])


                self.auto_resize(self.ws)
                self.merge_headers(self.ws,complete_data['Term'].unique(),len(self.data.columns.tolist()))
                self.merge_headers(self.ws,complete_data['Instructor'].unique(),len(self.data.columns.tolist()))

            #Write the 'By Day' sheet
            if key == 'by_day' and view[1].get():
                for term in complete_data['Term'].unique():

                    #Add the term row
                    self.ws.append([term])

                    #Format the Term row
                    self.ws.cell(self.ws.max_row, column=1).fill = PatternFill('solid', fgColor='808080')
                    self.ws.cell(self.ws.max_row, column=1).font = Font(size=20,bold=True)
                    self.ws.row_dimensions[self.ws.max_row].height = 30
                    for day in list(days_dict.keys()):
                        #Add the day row
                        self.ws.append([day])
                        #Format the day row
                        for col in range(1, len(self.data.columns.tolist())):
                            self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='A9A9A9')
                            self.ws.cell(self.ws.max_row, column=col).font = Font(bold=True)
                        mask = (complete_data['Term'] == term) & (complete_data['Meetings'].apply(lambda x: days_dict[day] in x))                        
                        new_df = (pd.concat([df, complete_data['Meetings']],axis=1))[mask]
                        new_df['start'] = new_df['Meetings'].apply((lambda d: (lambda x: x[d]['start']))(days_dict[day]))                        
                        new_df.sort_values(by='start', inplace=True)
                        new_df.drop(axis=1,columns=['Meetings','start'],inplace=True)
                        #Add the columns row
                        self.ws.append(new_df.columns.tolist())
                        #Format the columns row
                        for col in range(1, len(self.data.columns.tolist())+1):
                            self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='A9A9A9')
                            self.ws.cell(self.ws.max_row, column=col).font = Font(italic=True)

                        count = 0
                        for _, row in new_df.iterrows():
                            self.ws.append(row.tolist())
                            for col in range(1, len(self.data.columns.tolist())+1):
                                if count % 2 == 0:
                                    self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='E8E8E8')
                                else:
                                    self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='D3D3D3')
                            self.ws.row_dimensions[self.ws.max_row].height = 30
                            count += 1
                    self.ws.append([])
                    self.ws.append([])
                    self.auto_resize(self.ws)
                    self.merge_headers(self.ws,complete_data['Term'].unique(),len(self.data.columns.tolist()))
                    self.merge_headers(self.ws,list(days_dict.keys()),len(self.data.columns.tolist()))

    def write_course_schedule():
        for term in suppressed_data['Term'].unique():

            #Add the Term row
            self.ws.append([term])

            #Format the Term row
            for col in range(1, len(self.data.columns.tolist())+1):
                self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='808080')
                self.ws.cell(self.ws.max_row, column=col).font = Font(size=20,bold=True)
            self.ws.row_dimensions[self.ws.max_row].height = 30


            
            mask = complete_data['Term'] == term
            new_df = self.data[mask].copy()
            #new_df.drop(['Term'], axis=1,inplace=True)


            #Add the columns row
            self.ws.append(new_df.columns.tolist())

            #Format the columns row
            self.ws.row_dimensions[self.ws.max_row].height = 15
            for col in range(1, len(self.data.columns.tolist())+1):
                self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='A9A9A9')
                self.ws.cell(self.ws.max_row, column=col).font = Font(italic=True)

            count = 0
            for _, row in new_df.iterrows():
                self.ws.append(row.tolist())
                for col in range(1, len(self.data.columns.tolist())+1):
                    if count % 2 == 0:
                        self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='E8E8E8')
                    else:
                        self.ws.cell(self.ws.max_row, column=col).fill = PatternFill('solid', fgColor='D3D3D3')
                    self.ws.row_dimensions[self.ws.max_row].height = 30
                count += 1
            self.ws.append([])

        self.auto_resize(self.ws)
        self.merge_headers(self.ws,complete_data['Term'].unique(),len(self.data.columns.tolist()))


    def auto_resize(self,ws):
        for row in ws:
            for cell in row:
                cell.alignment = Alignment(wrap_text=True,
                                        horizontal='left', 
                                        vertical='center'
                                        )
        for column in ws.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length)/2 + 5
            try:
                ws.column_dimensions[column[0].column_letter].width = adjusted_width
            except AttributeError:
                pass

    def merge_headers(self,ws,column_values,end_col):
        for row in ws:
            if any(cell.value in column_values for cell in row):
                ws.merge_cells(start_column=1,
                               end_column=end_col,
                               start_row=row[1].row, end_row=row[1].row
                               )