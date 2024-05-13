from flask import Flask,request,render_template,make_response
import pandas as pd, numpy as np
import os
from io import BytesIO
import data,excel
from clss import clssreader
import json
import openpyxl

app = Flask(__name__)
app.config['SECRET_KEY'] =os.urandom(24)


@app.route('/',methods=['POST','GET'])
def automatrix():
    if request.method=='GET':
        return render_template('index.html')
    
    if request.method=='POST':

        #Retrieve data from form submission
        files = request.files.getlist('files')
        views = {'default'       : ['Course Schedule',(request.form.get('course_schedule') == 'true')],
                'by_instructor'  : ['Instructor Schedule', (request.form.get('instructor_schedule') == 'true')],
                'by_day'         : ['Daily Schedule', (request.form.get('daily_schedule') == 'true')],
                'graphical'      : ['Graphical Schedule', (request.form.get('graphical_schedule') == 'true')]
                }
        tas_in_instructor = (request.form.get('tas_in_instructor') == 'true')
        section_in_course = (request.form.get('section_in_course') == 'true')
        xlists_in_course = (request.form.get('xlists_in_course') == 'true')
        caps_in_enrollment = (request.form.get('caps_in_enrollment') == 'true')
        separate_title_topic = (request.form.get('separate_title_topic') == 'true')
        exclude_discussions = (request.form.get('exclude_discussions') == 'true')
        exclude_labs = (request.form.get('exclude_labs') == 'true')
        name_format = request.form.get('name_format')
        kept_columns = json.loads(request.form.get('columns'))

        #Hand the files to the reader, which combines the CSVs into a
        reader = clssreader()
        reader.combine_csv(files)

        #Hand the combined CSV to the handler, which does more cleanup and
        #applies user settings before sending to the excel writer
        handler = data.data_handler(reader.df)
        handler.delete_singletons()
        handler.move_TAs()
        handler.data.loc[handler.data['Instructor'].isna(), 'Teaching Assistant'] = np.nan
        handler.data['Instructor'].fillna(handler.data['Teaching Assistant'], inplace=True)    
        handler.cleanup()
        handler.extract_names('Instructor')
        handler.extract_names('Teaching Assistant')

        #Get a list of instructor names to use for Instructor View
        instructornames = handler.instructor_names(name_format, handler.data['Instructor'].tolist())

        #Dataframe to export
        data_to_write = handler.data.copy()
        handler.sort_terms(data_to_write)

        data_to_write['surname'] = data_to_write['Instructor']
        data_to_write = handler.rename(data_to_write,'last','surname')

        #Rename instructors, try renaming TAs unless TAs are not being kept
        data_to_write = handler.rename(data_to_write,name_format, 'Instructor')
        try:
            data_to_write = handler.rename(data_to_write,name_format, 'Teaching Assistant')
        except KeyError:
            pass

        #Apply checkbox settings
        #Separate titles?
        if not separate_title_topic: 
            data_to_write['Title'] = data_to_write.apply(lambda row: 
                                                                row['Topic'] if pd.notna(row['Topic']) 
                                                                else row['Title'], axis=1)
            data_to_write.drop(['Topic'],axis=1, inplace=True)
        
        #Combine section # with course #s?
        if section_in_course:
            data_to_write['Sec.'] = data_to_write['Sec.'].astype(int).astype(str)
            data_to_write['Course'] = data_to_write['Course'].astype(str) + '-' + data_to_write['Sec.'].fillna('').astype(str)

        #Combine crosslists with course #s?
        if xlists_in_course:
            data_to_write['Crosslisted'].astype(str).dropna()
            data_to_write['Course'] = data_to_write['Course'].astype(str) + ' (' + data_to_write['Crosslisted'].fillna('').astype(str)+')'
            data_to_write['Course'] = data_to_write['Course'].astype(str).apply(remove_trailing_parentheses).str.strip()

        #Combine TAs with instructors?
        if tas_in_instructor:
            data_to_write['Instructor'] = data_to_write['Instructor']+' ('+data_to_write['Teaching Assistant']+')'
            data_to_write['Instructor'] = data_to_write['Instructor'].apply(remove_trailing_parentheses).str.strip()
            try:
                data_to_write.drop(['Teaching Assistant'],axis=1,inplace=True)
            except:
                pass

        #Combine enrollment with course cap?
        if caps_in_enrollment:
            data_to_write['Enrollment'] = data_to_write['Enrollment'].astype(str).str.replace('.0','')+'/'+data_to_write['Cap'].astype(str).str.replace('.0','')
            try:
                data_to_write.drop(['Cap'],axis=1,inplace=True)
            except:
                pass

        #Exclude discussion sections?
        if exclude_discussions:
            data_to_write = data_to_write[~data_to_write['Section Type'].isin(['Discussion'])]
    
        #Exclude lab sections?
        if exclude_labs:
            data_to_write = data_to_write[~data_to_write['Section Type'].isin(['Laboratory'])]

        #'Suppressed data' is a df that's kept alongside self.handler.data but whose contents
        #are not made visible to the user, as they can't be put in the output.
        #'Term' is a suppressed column because all the output sheets are sorted by Term.
        #'Meetings' is suppressed because it contains structured info about meetings,
        #not just strings like 'MW3pm-3:20pm'. 'surname' is used only for the graphical schedule
        data_to_write['Meetings'] = handler.get_meetings(data_to_write)
        suppressed_data = data_to_write[['Term','Meetings','surname']]

        #Drop columns not specified by user and reorder according to user prefs
        data_to_write = data_to_write.reindex(columns=kept_columns)

        #Hand off to writer
        writer = excel.xlwriter(data_to_write,
                                views,
                                instructornames,
                                suppressed_data)
        workbook = writer.run()

        #Create a BytesIO stream for serving the file back to the
        #end user
        excel_data = BytesIO()
        workbook.save(excel_data)
        excel_data.seek(0)

        #Manually building the response because I couldn't get
        #send_file() to work *shrug emoji*
        response = make_response(excel_data.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=matrix.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response
    
def remove_trailing_parentheses(s):
    return s[:-3] if s.endswith(' ()') else s