'''
PACKAGES
'''

from __future__ import print_function
#from ortools.sat.python import cp_model
import os
import pandas as pd
import pyomo
import numpy
from numpy import genfromtxt
from pandas import ExcelWriter
from pandas import ExcelFile
from datetime import timedelta
from pandas.tseries import offsets
import cplex

# change working directory
os.chdir("C:/Users/Jacob Lindell/Desktop/All/Work/Luke/Compiled_Final")

'''
READ IN DATA
'''

Data = pd.read_excel('Data.xlsx')

#rename columns to get rid of spaces
Data.columns = ['Tail_Number', 'Owning_Base', 'Model', 'Scheduled_Start_Date', 
                'Depot_Length', 'Actual_Start', 'Forecasted_Finish']


'''
REPLACE SCHEDULED START AND DEPOT LENGTH WITH ACTUAL START AND NEW DEPOT LENGTH
'''
Data['Actual_Start'] = Data['Actual_Start'].fillna(0) # Makes all NAs 0
Data['Forecasted_Finish'] = Data['Forecasted_Finish'].fillna(0)
a = 0

for i in range(len(Data)):
    if Data.iloc[i,5] == 0:
        a = a
    else:
        Data.iloc[i,3] = Data.iloc[i,5] # replaces scheduled start with actual start
        Data.iloc[i,4] = (Data.iloc[i,6] - Data.iloc[i,5]).days # finds days between actual start and actual finish, then converts to integer
        
Data = Data.drop(['Actual_Start', 'Forecasted_Finish'], axis=1) # gets rid of actual start and finish columns

'''
GET NECESSARY PARAMETERS FROM DATA and create new columns
'''

# max_planes
max_planes = Data['Tail_Number'].max()
# max_bases
max_bases = Data.Owning_Base.nunique()
# max_months
Data['year'] = pd.DatetimeIndex(Data['Scheduled_Start_Date']).year
Data['month'] = pd.DatetimeIndex(Data['Scheduled_Start_Date']).month
Data['day'] = pd.DatetimeIndex(Data['Scheduled_Start_Date']).day
max_year = Data['year'].max() # finds the last year
max_month = Data.iloc[len(Data)-1]['month'] # assume last row is always highest
min_year = Data['year'].min()
min_month = Data.iloc[0]['month'] # assume first row is always lowest
max_months = ((max_year-min_year)*12) + max_month + 12 # started data at beginning of 1998
# max_slackplanes
max_slackplanes = 10 # not found from data, just guessed
# Adds depot_length to start_date
Data['Depot_End_Date'] = 0
for i in range(len(Data)):
    Data.iloc[i,8] = Data.iloc[i,3] + timedelta(days = Data.iloc[0,4].item())

# Depot_Length_months    
Data['Depot_Length_months'] = (Data['Depot_Length']/30).round(0) # create depot_length in months


'''
CREATE DEPOT DATA
'''
#Depot_Data = numpy.zeros(shape=(max_planes,max_months))

start_date = Data.iloc[0,3] - offsets.YearBegin() # start at beginning of year
start_year = start_date.year
start_month = start_date.month

# convert length and end from float to int for addition
Data['Depot_Length_months'] = Data['Depot_Length_months'].astype(numpy.int64) 

# Month_start is month + year - 1 (python indeces start at 0)
Data['SSD_Month_start'] = (Data['year'] - start_year)*12 + (Data['month'] - start_month)
Data['SSD_Month_start'] = Data['SSD_Month_start'].astype(numpy.int64)
Data['SSD_Month_end'] = Data['SSD_Month_start'] + Data['Depot_Length_months'] # month start + depot length (varies)

# Create Depot_Data (new value for every month in depot)
Depot_Data = Data[['Tail_Number', 'SSD_Month_start', 'SSD_Month_end']]
Dep = numpy.zeros(shape=(max_planes+1,max_months))

for i in range(len(Depot_Data)): # loop through data
    for j in range(Depot_Data.iloc[i,1],Depot_Data.iloc[i,2]): # loop through 8-18
        Dep[Depot_Data.iloc[i,0],j] = 1 # month = 1

# get rid of rows with only 0s
# if sum of row = 0, delete row
Depot_Data.sum(axis=1)

# write data
Depot_Data = pd.DataFrame(data=Dep)
Depot_Data = Depot_Data.drop(Depot_Data.index[0])

# get rid of rows with only 0s
# if sum of row = 0, delete row
Depot_Data.sum(axis=1)

Depot_Data.to_csv('Data\Depot_Data.csv', index=False)


'''
CREATE INITIAL POSS
'''

Init_Poss = Data[['Tail_Number', 'Owning_Base']]
## Owning base will show how it converts
Owning_Base = {'D': 0, 'W': 1, 'T': 2, 'L': 3}
#Assign these different key-value pair from above dictiionary to your table
Init_Poss['Owning_Base'] = [Owning_Base[item] for item in Init_Poss['Owning_Base']]


# Sort values, and then remove duplicate tail numbers
df = Init_Poss.sort_values('Tail_Number', ascending=True)
df = df.drop_duplicates(subset='Tail_Number', keep='first')

# Change it to be binary

a = numpy.zeros(shape=(max_planes+1, max_bases))

for i in range(0,len(df['Tail_Number'])):
    a[df.iloc[i][0]][df.iloc[i][1]] = 1

# get rid of rows with only 0s
# if sum of row = 0, delete row    
Initial_Poss = pd.DataFrame(data=a)
Initial_Poss = Initial_Poss.iloc[1:]

Initial_Poss.to_csv('Data\Initial_Poss.csv', index=False)


'''
DEPOT DATA FLIP
'''
## Flips the depot data in order to use it to replace the given statement
a = numpy.zeros(shape=(max_planes+1,max_months+1))


for i in range(Depot_Data.shape[0]):
    for j in range(Depot_Data.shape[1]):
        if Depot_Data.iloc[i,j] == 1:
            a[i,j] = 0
        else:
            a[i,j] = 1

Depot_Data_Flip = pd.DataFrame(data=a)

Depot_Data_Flip.to_csv('Data\Depot_Data_Flip.csv', index=False)


'''
MIN OWNED, MIN REQUIRED
'''

# Min owned
a = Initial_Poss.sum(axis=0, skipna=True)
Min_Owned = pd.DataFrame(data=a)

Min_Owned.to_csv('Data\Min_Owned.csv', index=False)

# Min req
Min_Req = pd.read_csv('Data/Min_Req.csv')


'''
A IS B
'''

## If a=b, 0, otherwise 1

a = numpy.zeros(shape=(max_bases,max_bases))

for i in range(max_bases):
    for j in range(max_bases):
        if i == j:
            a[i,j] = 0
        else:
            a[i,j] = 1
            
AisB = pd.DataFrame(data=a)

AisB.to_csv('Data\AisB.csv', index=False)


'''
CREATE PYOMO MODEL
'''

from pyomo.environ import *
#import pyomo.environ
from pyomo.opt import SolverStatus, TerminationCondition
from pyomo.opt import SolverFactory
#from pyomo.util.infeasible import log_infeasible_constraints
#from pyomo.core.base.expr import identify_variables
import time
start = time.time()

model = ConcreteModel('Min Swaps')


N = range(0,max_planes)
A = range(0, max_bases)
B = range(0, max_bases)
C = range(0, max_bases)
T = range(0, max_months)
M = range(0, max_slackplanes)

# VARIABLES
model.y = Var(N, A, B, T, within = Binary)
model.s = Var(M, B, T, within = Binary)

'''
Objective and constraints
'''

# OBJECTIVE
model.obj = Objective(expr = sum(model.y[n,a,b,t] * AisB.iloc[a,b] for n in N for a in A for b in B for t in T) + sum(100 * model.s[m,b,t]
                      for m in M for b in B for t in T), sense = minimize)
# y (plane n goes from base a to base b during month t) * AisB (does a = b) + Big M method for slack vars (dont use slack)

# CONSTRAINTS
    # All aircraft are assigned
def all_assigned_rule(model, n, t):
    return (sum(model.y[n,a,b,t] for a in A for b in B) == 1)
model.all_assigned = Constraint(N, T, rule = all_assigned_rule)

    # Min planes required
        ## Added the Depot_Data_Flip which should take care of the given statement from the formulation
def min_req_rule(model, b, t):
        return ((sum(model.y[n,a,b,t] * Depot_Data_Flip.iloc[n,t] for n in N for a in A) + sum(model.s[m,b,t] for m in M)) >= Min_Req.iloc[b,1])
model.min_req = Constraint(B, T, rule = min_req_rule)

    # Planes owned by base = owned planes
def planes_owned_rule(model, b, t):
    return (sum(model.y[n,a,b,t] for n in N for a in A) >= Min_Owned.iloc[b,0])
model.planes_owned = Constraint(B, T, rule = planes_owned_rule)

    # Planes start at init poss
def init_poss_rule(model, n, b):
    return (sum(model.y[n,a,b,0] for a in A) - Initial_Poss.iloc[n,b] == 0)
model.init_poss = Constraint(N, B, rule = init_poss_rule)


def last_next_rule(model, n, a, t):
    if t < (max_months-1):
        return ((sum(model.y[n,a,b,t+1] for b in B) - sum(model.y[n,c,a,t] for c in C)) == 0)
    else:
        return ((sum(model.y[n,a,b,max_months-1] for b in B) - sum(model.y[n,c,a,max_months-2] for c in C)) == 0)
model.last_next = Constraint(N, A, T, rule = last_next_rule)

'''
Start the optimization.
'''

solver = 'glpk'
opt = SolverFactory(solver)

#results = opt.solve(model, timelimit = 1, symbolic_solver_labels=True)
results = opt.solve(model)
end = time.time()

'''
Print the results.
'''

row = 0
var_ans = numpy.full(((max_planes*max_months),4), numpy.inf)
slack_use = numpy.zeros(shape=(max_bases,max_months))


print('The problem has ' + str(max_planes) + ' planes and ' + str(max_bases) + ' bases over ' + str(max_months) + ' months.')
print('It took ' + str(end - start) + ' seconds to solve.')
 # if statement that will say whether it is feasible or not, and if feasible will give the results. Helps stop running
if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
    print('Problem is feasible')
    print('The solution is: ' + str(results.solver.termination_condition))
    print('The objective value is: ' + str(model.obj()))

    # writes the variables to a csv
    for n in range(max_planes):
        for a in range(max_bases):
            for b in range(max_bases):
                for t in range(max_months):
                    if model.y[n,a,b,t].value == 1:
                        var_ans[row,0] = n
                        var_ans[row,1] = a
                        var_ans[row,2] = b
                        var_ans[row,3] = t
                        row = row+1
    numpy.savetxt("var_ans.csv", var_ans, delimiter = ",")
    
    # writes the slack vars to a csv
    for m in range(max_slackplanes):
        for b in range(max_bases):
            for t in range(max_months):
                if model.s[m,b,t].value == 1:
                    slack_use[b,t] = slack_use[b,t]+1
    numpy.savetxt("slack_use.csv", slack_use, delimiter = ",")    

        
# I want a new csv file that shows only when a plane changes bases
    Ans = pd.DataFrame(data=var_ans)

    Ans.columns = ['Plane', 'Base Past', 'Base Current', 'Month']

    Ans = Ans.sort_values(by=['Plane', 'Month'])

# DATA IS SORTED BY PLANE AND MONTH, SO FOR EACH PLANE THE MONTH GOES FROM 1-600

# So if plane is the same as before, base is the same as before, dont write
    # if plane is same as before and base is different, write plane, base, month
    
# if plane is different, write plane, base, month
    row = 0
    roww = 0
    rand = 1 # filler

    df = numpy.full((3000,4), numpy.inf)

    for i in range(len(Ans)-1):
        if i==0:
            df[0,0] = Ans.iloc[0,0]
            df[0,1] = Ans.iloc[0,1]
            df[0,2] = Ans.iloc[0,2]
            df[0,3] = Ans.iloc[0,3]
            row = row+1
        else:
            if Ans.iloc[i,0] == Ans.iloc[i+1,0]: # this plane and next plane are same
                if Ans.iloc[i,1] == Ans.iloc[i,2]: # this base and next base are same
                    rand = rand+1
                else: # plane is same but base is different
                    df[row,0] = Ans.iloc[i,0]
                    df[row,1] = Ans.iloc[i,1]
                    df[row,2] = Ans.iloc[i,2]
                    df[row,3] = Ans.iloc[i,3]
                
                    row = row+1
            else: # plane is different
                df[row,0] = Ans.iloc[i,0]
                df[row,1] = Ans.iloc[i,1]
                df[row,2] = Ans.iloc[i,2]
                df[row,3] = Ans.iloc[i,3]
            
                row = row+1
            
                df[row,0] = Ans.iloc[i+1,0]
                df[row,1] = Ans.iloc[i+1,1]
                df[row,2] = Ans.iloc[i+1,2]
                df[row,3] = Ans.iloc[i+1,3]
            
                row = row+1
            
    numpy.savetxt("Ans_org.csv", df, delimiter = ",")
    
    
elif (results.solver.termination_condition == TerminationCondition.infeasible):
    print('Problem is infeasible')
    #log_infeasible_constraints(model)
else:
     # Something else is wrong
    print ('IDK what happened, but something went wrong')
    
