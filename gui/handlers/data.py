# matrixgenerator.handlers.data.py

from datetime import datetime
import pandas as pd
import re

'''
The data_handler class manages all updates to the data that transform it from the
CLSS-provided csv into a more legible doc. 
''' 

class data_handler:
     #self.data is the df to be manipulated
    def __init__(self, initial_df=None):
        self.filepaths = []
        self.nameslist = []
        if initial_df is None:
            self.data = pd.DataFrame()
        else:
            self.data = initial_df
        self.data.dropna()

    def sort_terms(self, df):
        if df.empty:
            raise ValueError('No data accessible')
        else:
            df['year'] = df['Term'].astype(str).str.extract(r'(\d{4})')
            df['term'] = df['Term'].astype(str).str.extract(r'^\d{4}\s(\w+)$') 
            # Define custom order for terms
            term_order = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}
            # Create a new column with custom order values
            df['term_order'] = df['term'].map(term_order)
            # Sort by year and then by custom order
            df.sort_values(by=['year', 'term_order'], ascending=[True, True], inplace=True)
            # Drop the new column
            df.drop(columns=['term_order'], inplace=True)
            return df
    
    def keep_columns(self,lst):
        to_drop = [col for col in self.data.columns if col not in lst]
        self.data = self.data.drop(columns=to_drop)

    #Delete rows containing only one item
    def delete_singletons(self):
        singletons = self.data.apply(lambda row: row.nunique() <= 1, axis=1)
        self.data = self.data[~singletons]

    def move_TAs(self):
        work = self.data['Instructor'].str.split('; ')
        # Remove Instructor substrings containing 'No Print'
        work= work.apply(lambda lst: [s for s in lst if "No Print" not in s])
        #Instructors of Record are primary and secondary instructors
        instructors_of_record = work.apply(lambda lst: [s for s in lst if "Instructor" in s])
        instructors_of_record = instructors_of_record.apply(lambda lst: "; ".join(lst))
        #TAs are anyone else (after we remove the 'No Print' entries)
        teaching_assistants = work.apply(lambda lst: [s for s in lst if "Instructor" not in s])
        teaching_assistants = teaching_assistants.apply(lambda lst: "; ".join(lst))
        #Update the original DF with Instructors of Record
        self.data['Instructor'] = instructors_of_record
        # Create and populate a new column "Teaching Assistant" 
        self.data.insert(loc=self.data.columns.get_loc('Instructor')+1, column='Teaching Assistant', value=teaching_assistants)

    def extract_names(self,column_name):
    # Function to break up comma-separated names into lists of lists
        new_column = self.data[column_name].str.replace(
            r' \([^)]*\)', '', regex=True).str.replace(
                r' \[[^\]]*\]', '', regex=True).str.split(
                    '; '
                    )
        
        output = []
        for row in new_column:
            names = []
            for name in row:
                name = name.strip()
                name_parts = name.split(', ')
                names.append(name_parts)
                names.sort(key=lambda x: x[0])
            output.append(names)

        self.data[column_name] = output


    def rename(self, df, setting, column_name):
    # Function to overwrite Instructor and TA values
    # with formatted names (options: 'Last, First',
    # 'Last', and 'First Last')
        newcolumn = []
        for row in df[column_name]:
            newrow = []
            for item in row:
                if setting == 'Lastname, Firstname':
                    newrow.append(', '.join(item))
                if setting == 'Lastname':
                    newrow.append(item[0])
                if setting == 'Firstname Lastname':
                    try:
                        newrow.append(item[1]+' '+item[0])
                    except IndexError:
                        #IndexError should only get raised if there's a mononymous
                        #person in the list (typically 'Staff', though it could
                        #in principle be a particular person). In that case,
                        #return their mononym.
                        newrow.append(item[0])
            
            #If courses happen on an irregular schedule, then the instructor appears
            #multiple times. This is annoying, so we remove duplicates from the list.  
            newrow = remove_duplicates(newrow)

            if setting == 'Lastname, Firstname':
                newrow = '; '.join(newrow)
            else:
                newrow = ', '.join(newrow)
            newcolumn.append(newrow)
        df[column_name] = newcolumn
        return df
    
    def instructor_names(self, setting, split_names):
    #Like `rename`, except it returns a list of whoever is in the Instructor
    #column.
        sorted_list = []
        nameslist = []
        for course in split_names:
            for name in course:
                sorted_list.append(name)
        sorted_list.sort(key=lambda x: x[0])
        for name in sorted_list:
            if setting == 'Lastname, Firstname':
                nameslist.append(', '.join(name))
            if setting == 'Lastname':        
                nameslist.append(name[0])
            if setting == 'Firstname Lastname':
                try:
                    nameslist.append(name[1]+' '+name[0])
                except IndexError:
                    #IndexError should only get raised if there's a mononymous
                    #person in the list (typically 'Staff', though it could
                    #in principle be a particular person). In that case,
                    #return their mononym.
                    nameslist.append(name[0])
            #If courses happen on an irregular schedule, then the instructor appears
            #multiple times. This is annoying, so we remove duplicates from the list.  
        nameslist = remove_duplicates(nameslist)
        return nameslist

    def cleanup(self):
    #Removes unnecessary information that comes in the CLSS-generated .csv files
        self.data = (self.data[~self.data['Sec.'].
                               astype(str).str.startswith('X')])
        self.data = (self.data[~self.data['Schedule'].
                               isin(['Does Not Meet'])])
        self.data = (self.data[~self.data['Section Type'].
                               isin(['Independent Study', 'Research'])])
        self.data['Title'] = (self.data['Title'].str.
                                     replace(r' \(Prior.*', '', regex=True))
        self.data['Crosslisted'] = (self.data['Crosslisted'].str.
                                 replace('See ','').str.replace('Also ',''))


    def get_meetings(self, df):
        work = df['Schedule'].str.split('; ')
        list_of_dicts = []
        for lst in work:
            temp_dict = {}
            for item in lst:
                key, meeting = item.split(' ')
                times = meeting.split('-')
                for i in range(len(times)):
                    if ':' not in times[i]:
                        times[i] = datetime.strptime('01-01-1900 ' + (times[i][:-2] + ":00" + times[i][-2:]), '%m-%d-%Y %I:%M%p')
                    else:
                        times[i] = datetime.strptime('01-01-1900 ' + times[i],'%m-%d-%Y %I:%M%p')
                value = {'start': times[0], 'end':times[1]}
                temp_dict[key] = value
            list_of_dicts.append(temp_dict)
        days = ['M','T','W','Th','F']
        list_of_meetings = []
        for dct in list_of_dicts:
            temp_dict={}
            for key, values in dct.items():
                for day in days:
                    if day == 'T' and re.search(r"T(?!h)",key):
                        temp_dict[day] = values                      
                    elif day in key and not day =='T':
                        temp_dict[day] = values
            temp_dict = dict(sorted(temp_dict.items(), key=lambda x: days.index(x[0])))
            list_of_meetings.append(temp_dict)
        return list_of_meetings

def remove_duplicates(lst):
    return list(dict.fromkeys(lst))