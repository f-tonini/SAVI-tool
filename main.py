import arcpy, os, numpy, shutil
import pandas as pd
from numpy import *
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

abspath = sys.argv[0]
dname = os.path.dirname(abspath)
temppath = dname + "\\ztemp12345" 
if not os.path.isdir(temppath):
   os.makedirs(temppath)
arcpy.env.workspace= temppath

# User Specified Variables:
Observation = ("C:/1_EDF\Other Publication Work/AccuSim/Basic data for test/obs")
Simulation = ("C:/1_EDF\Other Publication Work/AccuSim/Basic data for test/sim1")
n_classes = 2

# Convert Simulation to order magnitude bigger for confusion matrix
mod_simulation = (Raster(Simulation)+40)*100

# Combine obs and sim to create confusion matrix
matrix1 = mod_simulation + Raster(Observation)
arcpy.TableToTable_conversion(matrix1, temppath, 'tempOutFile.dbf')

# Create array of data
location = temppath + '\\tempOutFile.dbf'
rows = arcpy.SearchCursor(location,"","","")
currentCOUNT = "COUNT"
newdata = []
for row in rows:
        rowN = [row.getValue(currentCOUNT)]
        newdata.append(rowN)
del row, rows
matrix = []
for i in newdata:
    x=str(i)
    x=x[:-1]
    x=x[1:]
    x=float(x)
    matrix.append(x)
del i, newdata

# matrix created NOW do quantity and allocation disagreement
maxcount = n_classes * n_classes
matrix = array(matrix)
tot = sum(matrix)
pct_array=[]
for i in matrix:
    pct = i/tot
    pct_array.append(pct)
mylist = []
df = pd.DataFrame()
l = 1
n=1
col=1
for i in matrix:
    if l <= maxcount:
        if n < n_classes:
            mylist.append(i)
            n=n+1
            l=l+1
        elif n == n_classes:
            colname = str(col)
            col=col+1
            n=1
            l=l+1
            mylist.append(i)
            row = pd.Series(mylist)
            df[colname] = row.values
            mylist = []

# Begin converting matrix to pontius table
tot = df.values.sum()
df.div(tot)

# Get Comission
comis_minus = []
i = 1
ccount = 0
while i <= n_classes:
    colname = str(i)
    comis1 = df[colname][ccount]
    colsum = df[colname].sum()
    add = (colsum - comis1)/tot
    comis_minus.append(add)
    i = i+1
    ccount = ccount+1    
extra = 0.0
comis_minus.append(extra)
corow = pd.Series(comis_minus)                

# Calculate Omission
omis_minus = []
ccount = 0
i = 1
while i <= n_classes:
    omis1 = df.iloc[ccount, ccount]
    rowsum = df.iloc[ccount].sum()
    add = (rowsum - omis1)/tot
    omis_minus.append(add)
    ccount = ccount+1
    i = i+1
extra = 0.0
omis_minus.append(extra)
omis_minus.append(extra)
omis_row = pd.Series(omis_minus)

# Divide by tot to get pcts in table
i = 1
ccount = 0
while i <= n_classes:
    colname = str(i)
    df[colname] = (df[colname]/tot)
    i = i+1
    ccount = ccount+1    

# Create table with comission and omission + totals
df['Total'] = (df.sum(axis=1))
df.loc['Sum'] = df.sum()
df.loc['Comission'] = corow.values
df['Omission'] = omis_row.values

# Build output table
Pontius_table = pd.DataFrame(columns = ["Class", "Omission", "Agreement", "Comission", "Quantity", "Allocation"])
i = 1
while i <= n_classes:
    row = []
    Cat = "Category " + str(i)
    val = i-1
    Omis = (df.iloc[val][3])*100
    Agree = (df.iloc[val][val])*100
    Comis = (df.iloc[3][val])*100
    Quant = abs(Omis - Comis)
    Alloc = 2*(minimum(Omis, Comis))
    row.append(Cat)
    row.append(Omis)
    row.append(Agree)
    row.append(Comis)
    row.append(Quant)
    row.append(Alloc)
    row1 = pd.Series(row)
    place = str(val)
    Pontius_table.loc[i] = row1.values
    i=i+1

Quant_total = (Pontius_table["Quantity"].sum())/2
Alloc_total = (Pontius_table["Allocation"].sum())/2
totals = []
tot = "Total Disageement"
noval = "- - -"
totals.append(tot)
totals.append(noval)
totals.append(noval)
totals.append(noval)
totals.append(Quant_total)
totals.append(Alloc_total)
totals1 = pd.Series(totals)
x = i+1
Pontius_table.loc[x] = totals1.values

print Pontius_table
mod_simulation.save(os.path.join(temppath,'tmp_modsim'))
arcpy.Delete_management(mod_simulation)
matrix1.save(os.path.join(temppath,'tmp_matrix'))
arcpy.Delete_management(matrix1)

del mod_simulation, matrix1
shutil.rmtree(temppath)
