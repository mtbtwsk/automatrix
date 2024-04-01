# AutoMatrix
version 0.1.0

<img width="600" alt="Screen Shot 2024-03-29 at 8 53 44 PM" src="https://github.com/mtbtwsk/automatrix/assets/165427058/d95bc59a-1078-4386-9353-d5b300fc14fe">

**AutoMatrix** is a utility that automates the generation of **course matrices** from [CLSS](https://www.courseleaf.com/software/clss/) export CSVs. In addition to generating a matrix of course offerings, AutoMatrix can generate by-instructor, by-day, and graphical schedules of course offerings.

## Installation

(Mac only for now.) Download the AutoMatrix.app.zip file from [Releases](https://github.com/mtbtwsk/automatrix/releases/tag/v0.1.0), unzip, and move it to your Applications folder. Before you run it the first time, you may need to go to System Preferences > Security and manually allow it to be run.

## How to use AutoMatrix 

After your courses have been entered in CLSS:

1. Navigate to the CLSS page for the term and department for which you want course information.
2. Click `export` in the top right corner. 
3. In the resulting menu, **click `Check all`**, export the full .csv file, and save it to your computer.
4. Repeat Step 2 for all the terms you want to appear in your matrix.
5. Launch AutoMatrix and read in the .csv files you downloaded from CLSS.
6. Configure your preferences.
7. Click `Save As...` to save the .xlsx file.

## Features

### Matrix Settings panel

The left listbox contains the columns you want to keep in the final output document. It's preloaded with default choices. Move columns in or out of the left column using the arrow buttons, and reorder items in the left list by dragging and dropping.

### Export Settings panel

AutoMatrix generates four types of schedules:

+ **Course Schedule**: A simple by-quarter schedule of classes, alphabetically by course number.
+ **Instructor Schedule**: For each quarter, a sub-schedule for every primary instructor.
+ **Daily Schedule**: For each quarter, a sub-schedule for every day of the week.
+ **Graphical Schedule**: A graphical representation of course offerings for each quarter.

For space reasons, the Graphical Schedule displays the Course, Instructor, and meeting times only.

### More Settings panel

This panel offers some customization options for the output document.

+ **Include TAs in Instructor Column**. If checked, TAs will be shown in the following format under Instructor: `Primary Instructor (Teaching Assistant, ...)`.
+ **Include Xlists in Course Column**. If checked, crosslisted courses will be listed in the following format under Course: `MY_DEPT 101-1 (XLIST 101-1)`.
+ **Show Course Cap w/ Enrollment**. If checked, the Enrollment column will display the number enrolled against the course cap, e.g. `15/20`.
+ **Separate Columns for Title and Topic**. By default, course titles are rewritten with special topics. If you want to keep them separate, check this box.
+ **Exclude Discussion/Laboratory Sections**. These boxes allow you to exclude sections that are listed as labs or discussion sections.

## Note: Column Names

For legibility, AutoMatrix renames some of the most commonly used columns from their default names in CLSS. Refer to the following table:

| CLSS terminology   | AutoMatrix terminology |
|--------------------|------------------------|
| Maximum Enrollment | Cap                    |
| Section #          | Sec.                   |
| Combined           | Crosslisted            |
| Meeting Pattern    | Schedule               |
| Course Title       | Title                  |








