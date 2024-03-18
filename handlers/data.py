import pandas as pd
import re

'''
The data_handler class manages all updates to the data that transform it from the
CLSS-provided csv into a more legible doc. 
''' 

class data_handler:
     #self.data is the df to be manipulated
    def __init__(self, initial_df=None):
        self.files = []
        if initial_df is None:
            self.data = pd.DataFrame()
        else:
            self.data = initial_df
        self.data.dropna()
        self.instructor = self.data['Instructor']
        self.ta = self.data['Teaching Assistant']

    def sort_terms(self):
        if self.data.empty:
            raise ValueError('No data accessible')  # Raise the ValueError instead of just creating it
        # Extract year and term
        self.data['year'] = self.data['Term'].str.extract(r'(\d{4})')
        self.data['term'] = self.data['Term'].str.extract(r'(\w+)')
        # Define custom order for terms
        term_order = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}
        # Create a new column with custom order values
        self.data['term_order'] = self.data['term'].map(term_order)
        # Sort by year and then by custom order
        self.data.sort_values(by=['year', 'term_order'], ascending=[True, True], inplace=True)
        # Drop the new column
        self.data.drop(columns=['term_order'], inplace=True)
    
    def drop_columns(self,list):
        to_drop = [col for col in self.data.columns if col not in list]
        self.data = self.data.drop(columns=to_drop)
        self.data = self.data.reindex(columns=list)

    #Delete rows containing only one item
    def delete_singletons(self):
        singletons = self.data.apply(lambda row: row.nunique() <= 1, axis=1)
        self.data = self.data[~singletons]

    def cleanup(self):
        # Remove canceled sections (these start with X)
        self.data['Section #'] = self.data['Section #'].astype(str)
        self.data = self.data[~self.data['Section #'].str.startswith('X')]
        # Remove independent studies and research sections
        self.data = self.data[~self.data['Section Type'].isin(['Independent Study', 'Research'])]
        # Remove unnecessary info from Course Title and Instructor/TA fields
        self.data['Course Title'] = self.data['Course Title'].str.replace(r' \(Prior.*', '', regex=True)
        self.data['Instructor'] = self.data['Instructor'].str.replace(r' \([^)]*\)', '', regex=True)
        self.data['Instructor'] = self.data['Instructor'].str.replace(r' \[[^\]]*\]', '', regex=True)
        self.data['Teaching Assistant'] = self.data['Teaching Assistant'].str.replace(r' \([^)]*\)', '', regex=True)
        self.data['Teaching Assistant'] = self.data['Teaching Assistant'].str.replace(r' \[[^\]]*\]', '', regex=True)
        # Update course titles with special topics and drop the "Topic" column
        self.data['Course Title'] = self.data.apply(lambda row: row['Topic'] if pd.notna(row['Topic']) else row['Course Title'], axis=1)
        self.data.drop(['Topic'],axis=1, inplace=True)
        self.data['Combined'] = self.data['Combined'].str.replace('See ','').replace('Also ','')
        self.data['Combined'] = self.data['Combined'].str.replace('Also ','')
    
    
    def move_TAs(self):
        work = self.data['Instructor'].str.split(';')
        work = work.dropna()
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
        # Create a new column "Teaching Assistant" for relevant entries
        self.data.insert(loc=self.data.columns.get_loc('Instructor')+1, column='Teaching Assistant', value=teaching_assistants)

    def rename(self,setting):
        if setting == 'Last, First':
            self.data['Instructor'] = self.instructor
        if setting == 'Last':       
            self.data['Instructor'] = self.instructor.str.split(';  ')
            for row in self.data['Instructor']:
                for instructor in row:
                    instructor = instructor.split(',', 1)[0]
                row = '; '.join([s for s in row])
        if setting == 'First Last':
            self.data['Instructor'] = self.instructor.str.split(';  ')
            new_column = []
            for row in self.data['Instructor']:
                names = []
                for name in row:
                    name_parts = name.split(', ')
                    first_last = ' '.join([name_parts[1], name_parts[0]])
                    names.append(first_last)
                new_column.append('; '.join(names))
            self.data['Instructor'] = new_column

    #This function takes the 'Meeting Pattern' string and breaks it into
    #a dictionary {day: time}, to be used for "by-day" outputs
    def get_meetings(self):
        work = self.data['Meeting Pattern'].str.split('; ')
        list_of_dicts = []
        for lst in work:
            temp_dict = {}
            for item in lst:
                key, value = item.split(' ')
                temp_dict[key] = value
            list_of_dicts.append(temp_dict)
        days = ['M','T','W','Th','F']
        list_of_meetings = []
        for dct in list_of_dicts:
            temp_dict={}
            for key, value in dct.items():
                for day in days:
                    if day == 'T' and re.search(r"T(?!h)",key):
                        temp_dict[day] = value                        
                    elif day in key and not day =='T':
                        temp_dict[day] = value
                    else: 
                        pass
            temp_dict = dict(sorted(temp_dict.items(), key=lambda x: days.index(x[0])))
            list_of_meetings.append(temp_dict)

        self.data['Meetings'] = list_of_meetings
        