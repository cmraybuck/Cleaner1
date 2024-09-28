FILE first_file ./csvs/DocA.csv SSN *Specifies file and ID column
FILE second_file ./csvs/DocB.csv SSN

OUTPUT-FILE= ./output.csv *Specifies name of output file

DEL-ROW second_file 0,1,2,3,4,5,6,7,8 *Deletes rows 1-9 from DocB
ADD-COL first_file 4,5,6 *Adds columns E, F, and G from DocA
ADD-COL second_file 1,2,3 *Adds columns B, C, and D from DocB

-----------------------------------------------------------------------------------------

FILE first_file ./csvs/DocA.csv SSN
FILE second_file ./csvs/DocB.csv SSN

OUTPUT-FILE= ./output.csv

DEL-ROW second_file 0,1,2,3,4,5,6,7,8
ADD-COL second_file Employee Name,Account Balance AS Balance, Age, Job Title, Department, Employment Status *Adds columns of specified names from DocB, renamed Account Balance to Balance.
ADD-COL first_file Date of Birth, Compensation, Hours Worked 


* "x AS y" renames column x to y. If no change is specified, the column name will remain the same.