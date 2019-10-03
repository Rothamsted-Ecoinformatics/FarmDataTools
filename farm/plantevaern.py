import csv
import xml.etree.ElementTree as et
import re

rawdata = open("data.xml", "r")
csvfile = open("data.csv","w",newline="")
dwriter = csv.writer(csvfile,delimiter=",")
linedata = []
for line in rawdata:
    line = line.strip()
    if re.search(r'value="[a-zA-Z\s\.\-\,\/\(\)]+"',line): 
        value = re.search(r'value="([a-zA-Z\s\.\-\,\/\(\)]+)"',line)
        if (value):
            linedata.append(value.group(1))
    elif re.search(r'value="?[0-9]*,?[0-9]*"?',line) and line.rfind("ProblemID") <=0:
        value = re.search(r'value="?([0-9]*,?[0-9]*)"?',line)
        if (value):
            linedata.append(value.group(1))
    elif line.rfind("</TR>")>-1:
        dwriter.writerow(linedata)
        linedata = []
    
    
    
    #if line.rfind("FORM") <=0 and line.rfind("ProblemID") <=0: # remove form elements as a distraction and may not be well formed 
        # don't know why but this keeps failing to parse the whole doc, so perhaps try just manual parse - everything is in value so should be possible line by line
        #line = line.strip()
        #cleanline = re.sub(r"<TD.+?>","<TD>",line) #clean up malformed TD elements
        #cleanline = re.sub(r"<A.+?>","",cleanline).replace("</A>","").replace("><INPUT","")
        #cleanline = re.sub(r"on[fF]ocus=\".+?\"","",cleanline)
        #cleanline = re.sub(r"on[bB]lur=\".+?\"","",cleanline)
        #cleanline = re.sub(r"on[cC]hange=\".*?\"","",cleanline)
        #cleanline = re.sub(r"onMouseOut=\".*?\"","",cleanline)
        #cleanline = re.sub(r"onMouseOver=\".*?\"","",cleanline)
        #cleanline = re.sub(r"STYLE=\".*?\"","",cleanline)
        #cleanline = re.sub(r"value=([0-9]+)",r'value="\1"',cleanline) # tidies up unquoted values
        #cleanline = cleanline.replace("readonly","").replace("&nbsp;","").replace("<TD></TD>","").replace("\" >","\">").replace("\t","").replace("class=\"disabledinput\"","").replace("  "," ")
        #cleanline.strip()
        #print(cleanline)
        #print(cleanline.rfind(r"[a-zA-Z]"))
    #    if re.search(r"[a-zA-Z]",cleanline):
    #        cleandata.write(cleanline+"\n")
#cleandata.close 

#tree = et.parse('cleandata.xml')
#root = tree.getroot()
#print(root)
#records = []



#for form in root.findall('TABLE/TR/FORM'):
#    row = []
#    for cell in form.findall('TD/INPUT'):
#        row.append(cell.attrib['value'])
#    print(row)
