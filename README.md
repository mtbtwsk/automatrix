# AutoMatrix 0.1.0

**AutoMatrix** is a utility for Northwestern staff that automates the generation of **course matrices**: the spreadsheets that we use to track course offerings and schedules within units.

In addition to generating a matrix of course offerings, AutoMatrix can generate by-instructor schedules, by-day schedules, and a graphical representation of course offerings.

## How to use AutoMatrix 

After your courses have been entered in CLSS:

1. Navigate to the CLSS page for the term and department for which you want course information.
2. Click `export` in the top right corner. 
3. In the resulting menu, click `Check all`, export the full .csv file, and save it to your computer.
4. Repeat Step 2 for all the terms you want to appear in your matrix.
5. Launch AutoMatrix and load in the .csv files you downloaded from CLSS.
6. Configure your preferences.
7. Click `Save As...` to save the .xlsx file.

## Features

This section describes the features in each part of the program.

### Matrix Settings panel

The left listbox contains the columns you want to keep in the final output document(s). It's preloaded with a default configuration. Move columns in or out of the left column using the arrow buttons. 

Reorder items in the left list by dragging and dropping.

## Column Titles

For legibility, AutoMatrix renames some of the most commonly used columns from their default names in CLSS. Refer to the following table:

| CLSS terminology   | AutoMatrix terminology |
|--------------------|------------------------|
| Maximum Enrollment | Cap                    |
| Section #          | Sec.                   |
| Combined           | Crosslisted            |
| Meeting Pattern    | Schedule               |
| Course Title       | Title                  |







