import pandas as pandas
import json
import datetime
from service import FarmService

myFarm = FarmService().myFarm()

xl = pandas.ExcelFile("Electronic-farm-diary-2020-RO-test-xlsx.xlsx")
print(xl.sheet_names)
df = xl.parse('Sheet1',index_col=None,header=0)

for index, row in df.iterrows():
    #print(row[0])
    if row['Prop_No'] == 'Commercial' and "Drill" in row['Application'] and row['loaded'] == "N" and isinstance(row['field_id'],int):
        print(row['Application'])
        # need to create the planting and then create a seeding attached to it