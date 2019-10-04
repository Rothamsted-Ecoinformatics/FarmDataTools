import csv
import re

rawdata = open("plantevaern.txt","r") # read in the data file
csvfile = open("data2.csv","a+",newline="") # open output file in append mode
dwriter = csv.writer(csvfile,delimiter=",") # CSV writer

#============================================================================================
# EDIT THESE FILTER PARAMS
# Herbicide, max does, adjuvant, growth stage, drough stress, min temp, max temp - they don't do anything, just extra data for the table
filterParams = ["DFF","0.24","Not relevant","0-2 leaves","None","8","14"]
#============================================================================================

linedata = [] # array for row data
process = False
for line in rawdata:
    if line.find('ID="sbar"')>-1: # data table starts after this 
        process = True
    elif line.find('name="frmConditions"')>1: # data table has finished 
        process = False
    
    if process:
        if line.rfind("</TR>")>-1 and len(linedata) > 0: # use </tr> to flag end of the row 
            for fp in filterParams:
                linedata.append(fp)
            dwriter.writerow(linedata) # write line to CSV
            linedata = [] # reset for next line
        elif line.find("ProblemID") <=0: # ignore inputs with this name 
            match = re.search(r'value="?([a-zA-Z\s\.\-\,\/\(\)]+|[0-9]*,?[0-9]*)"?',line) # if there is a value extract it using regex
            if match: # there is a value so process it
                value = match.group(1)
                value = re.sub(r'([0-9]*),([0-9]*)',r'\1.\2',value) # UKify decimals (regex here to avoid subs in plant names)
                linedata.append(value)    