#=======================================================================================================================================
# Import libraries and dataframe 
#=======================================================================================================================================

# Import libraries
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt 
import seaborn as sns

# Import dataframe
os.chdir('C:/Users/Guillermo/Desktop/ESTUDIOS/Data Science Bootcamp/Projects/Web scraping/Project')
df = pd.read_csv('jobs.csv')

# Summary statistics and first exploration
df.shape 
df.columns
df.head()


#=======================================================================================================================================
# Data cleaning  
#=======================================================================================================================================

# Drop columns we are not interested in
col = df[['Unnamed: 0', 'description', 'job_type', 'job_function']]
df.drop(col, axis = 1, inplace = True)

# Eliminate extra charachters in company names
df['company'] = df['company'].apply(lambda x: x.split('\n')[0])


# Clean employees and salaries columns from extra symbols (/hr, K, $...) 
for r in range(len(df)):
    a = list(map(lambda x: x.replace('[', '').replace("'", '').replace(']', '').strip(), df.iloc[r,5].split(',')))
    b = list(map(lambda x: x.replace('[', '').replace("'", '').replace(']', '').replace('/hr', '').replace('$', '').replace('K', '').strip(), df.iloc[r,6].split(', ')))
    df['employees'][r] = a
    df['salaries'][r] = b


# Extend dataframe creating one observation per each item in salaries and employees. When Glassdoor publishes a vacancy, 
# it includes references to other vacancies offer by the firm. This are contained as a list in the employees variable
# while the corresponding salaries are stored as lists in the salaries variable.
column_names = ['job', 'company', 'location', 'industry', 'size', 'employees', 'salaries']
df1 = pd.DataFrame(columns = column_names)

for i in range(df.shape[0]):
    j = df.iloc[i,0]
    c = df.iloc[i,1]
    l = df.iloc[i,2]
    ind = df.iloc[i,3]
    s = df.iloc[i,4]
    for i2 in range(len(df['salaries'][i])):
        e = df.iloc[i,5][i2]
        sal = df.iloc[i,6][i2]
        dic = {'job':[j], 'company':[c], 'location':[l], 'industry':[ind], 'size':[s], 'employees':[e], 'salaries':[sal]}
        temp = pd.DataFrame(dic)
        df1 = pd.concat([df1, temp], axis = 0)

df = df1.copy()

# Make every entry in the salaries variable to be express in thousands of dollars per year
def calculate_salary(x):
    try:
        if ('-' in x):
            x = x.split('-')                     
            x = ((float(x[0])+float(x[1]))/2)    # For salaries in which a range was provided (example: 13-14 USD/hr) we take the average point.       
            if x < 2000: x = x*40*52.14          # We convert average salaries per hour to salaries per year (40 hours/week, 52.14 weeks per year).
        else:
            x = float(x.replace(',',''))         # Remove comas that signal thousands of dollars.
            if x < 2000: x = x*40*52.14          # Once again, convert salaries per hour to salaries per year.         
    except:
        pass                                     # We avoid missing values so the loop doesn´t break.
    return(x)

df['salaries'] = list(map(calculate_salary, df['salaries']))

# Eliminate extra charachers ('Employees') from the size column
for i in range(df.shape[0]):
    try:
        df['size'].iloc[i] = df['size'].iloc[i].split(' Employees')[0]
    except:
        pass                                     # We avoid missing values so the loop doesn´t break.

# Simplified the location so that we get data on the State in which the firm is located.
df['location'] = list(map(lambda x: x.split(', ')[-1], df['location']))

# Simplify the longest label names for the industry variable. This will be useful in the exploratory data visualization part.
for i in range(df.shape[0]):
    if df['industry'].iloc[i] == 'Information Technology':
        df['industry'].iloc[i] = 'IT'
    elif df['industry'].iloc[i] == 'Transportation & Logistics':
        df['industry'].iloc[i] = 'Transportation' 
    elif df['industry'].iloc[i] == 'Oil, Gas, Energy & Utilities':
        df['industry'].iloc[i] = 'Energy'
    elif df['industry'].iloc[i] == 'Arts, Entertainment & Recreation':
        df['industry'].iloc[i] = 'Entertainment'
    elif df['industry'].iloc[i] == 'Construction, Repair & Maintenance':
        df['industry'].iloc[i] = 'Construction'   

# Eliminate duplicates. When Glassdoor publishes a vacancy, it includes references to other vacancies offer by the firm. 
# This data was scrapped as it helped increase the sample size. However, this means that if you scrape two or more 
# different vacancies from a company, each of them is going to make reference to the other, hence duplicating in the data.
df = df.drop_duplicates(keep = 'first').copy()

#=======================================================================================================================================
# Missing values  
#=======================================================================================================================================

# Assing missing values to empty cells
df = df.replace(r'^\s*$', np.nan, regex=True)

# Count number of rows with missing values
df.shape[0] - df.dropna().shape[0]      # 523 rows with missing values

# Number of missing values in the dataframe by column
df.isnull().sum()   

# Missing values are quite concentrated in the industry column. In order not to lose the rest of the information
# in those observations, we keep them and set nan in industry to be 'unknown'. 

for i in range(df.shape[0]):
    if pd.isnull(df['industry'].iloc[i]):
        df['industry'].iloc[i] = 'unknown'

# Drop missing values in rows for which most of the information is missing.
df = df.dropna()

#=======================================================================================================================================
# Exploration dataframe: key statistics and categorical variables  
#=======================================================================================================================================

# Key statistics
df.shape 
df.describe()

# Explore categorical variables

# Check the number of different options we have in each of our categorical variables
df_unique = df.nunique().to_frame().reset_index()
print(df_unique)
	# There are 15 different industries represented in the dataframe. Also an additional category 'unknown'.
	# There are 6 different ranges of sizes a firm can fall into. Also an additional category 'unknown'.
	# There are 3 different locations represented in the dataframe (NY, NJ and PA).

# Different industries, sizes and locations that are represented in the dataframe.
df['size'].unique()
df['industry'].unique()
df['location'].unique()

#=======================================================================================================================================
# Exploratory data visualization with seaborn  
#=======================================================================================================================================

# 1. Number of vacancies per industry
x = df.groupby('industry').count().reset_index().sort_values(ascending = False, by = 'employees')
sns.barplot(x = 'industry', y = 'employees', data = x, color = 'b')
# Set title for the graph
plt.title('Number of vacancies per industry', loc = 'center')
# Set x-axis label
plt.xlabel('Industries')
# Set y-axis label
plt.ylabel('Vacancies')
# Set industry labels vertical
plt.xticks(rotation = 90)


# 2. Relationship between salaries and industry
x = df.copy().sort_values(by = 'salaries', ascending = False)
sns.boxplot(x = 'industry', y = 'salaries', data = x)
# Set graph title
plt.title('Average salary per industry', loc = 'center')
# y-axis label
plt.ylabel('Salaries')
# x-axis label
plt.xlabel('Industries')
# Set industry labels vertical
plt.xticks(rotation = 90)


# 3. Number of vacancies per State
x = df.groupby('location')['employees'].count().reset_index().sort_values(ascending = False, by = 'employees')
sns.barplot(x = 'location', y = 'employees', data = x)
# Set graph title
plt.title('Number of vacancies per State', loc = 'center')
# y-axis label
plt.ylabel('Vacancies')
# x-axis label
plt.xlabel('States')
# Set industry labels vertical
plt.xticks(rotation = 90)


# 4. Salaries per State. 
sns.boxplot(x = 'location', y = 'salaries', data = df)
# Set graph title
plt.title('Average salaries per State', loc = 'center')
# y-axis label
plt.ylabel('Salaries')
# x-axis label
plt.xlabel('States')
# Set industry labels vertical
plt.xticks(rotation = 90)
#New Jersey has higher average salary than New York. We will break down this by industry.


# 5. Compare average salaries per industries across the States of New York and New Jersey. 
# Prepare dataframe with the relevant data
sal_ny = df[df['location'] == 'NY'].groupby('industry').mean().reset_index()
sal_nj = df[df['location'] == 'NJ'].groupby('industry').mean().reset_index()
x = sal_ny.merge(sal_nj, on = 'industry', how = 'outer')
# Reorder it following the values of the first value:
ordered_df = x.sort_values(ascending = False, by = 'salaries_x')
my_range = range(1, len(x.index) + 1)
# The vertical plot is made using the hline function
plt.hlines(y = my_range, xmin = ordered_df['salaries_y'], xmax = ordered_df['salaries_x'], color = 'grey', alpha = 0.4)
plt.scatter(ordered_df['salaries_x'], my_range, color = 'blue', alpha = 0.8 , label = 'NY')
plt.scatter(ordered_df['salaries_y'], my_range, color = 'orange', alpha = 1, label = 'NJ')
plt.legend()
# Add titles and axis names
plt.yticks(my_range, ordered_df['industry'])
plt.title("Average salaries across industries and States", loc='center')
plt.xlabel('Average salaries')
plt.ylabel('Industries')


# 6. Average salaries per firm in the business service industry
x = df[df['industry'] == 'Business Services']
# Average salaries per firm and State in the Business Service industry
x = x.groupby(['location', 'company'])['salaries'].mean().reset_index()
sns.barplot(x = 'salaries', y = 'company', hue = 'location', data = x, hue_order=["NY", "NJ"], palette=["C0", "C1"])
plt.title('Average salaries per firm in the business service industry', loc = 'center')
# y-axis label
plt.ylabel('Companies')
# x-axis label
plt.xlabel('Average salary')


# 7. Proportion of vacancies per industry and State 
# Number of total vacancies in New York
num_ny = df[df['location'] == 'NY']
num_ny = num_ny['employees'].count()
# Number of total vacancies in New Jersey
num_nj = df[df['location'] == 'NJ']
num_nj = num_nj['employees'].count()
# Calculate proportion of number of vacancies per industry in NY and NJ
x = df[df['location'] != 'PA']
x = x.groupby(['industry', 'location'])['employees'].count().reset_index()
for i in range(x.shape[0]):
    if x.iloc[i,1] == 'NY':
        x.iloc[i,2] = round((x.iloc[i,2]/num_ny)*100,2)
    else:
        x.iloc[i,2] = round((x.iloc[i,2]/num_nj)*100,2)
# Create dataframe with the proportion of vacancies per state (each state in one different column).
prop_vac_ny = x[x['location'] == 'NY']
prop_vac_nj = x[x['location'] == 'NJ']
x = prop_vac_ny.merge(prop_vac_nj, on = 'industry', how = 'outer')
# Reorder it following the values of the first value:
ordered_df = x.sort_values(ascending = False, by = 'employees_x')
my_range = range(1, len(x.index) + 1)
# The vertical plot is made using the hline function
plt.hlines(y = my_range, xmin = ordered_df['employees_y'], xmax = ordered_df['employees_x'], color = 'grey', alpha = 0.4)
plt.scatter(ordered_df['employees_x'], my_range, color = 'blue', alpha = 0.8 , label = 'NY')
plt.scatter(ordered_df['employees_y'], my_range, color = 'orange', alpha = 1, label = 'NJ')
plt.legend()
# Add titles and axis names
plt.yticks(my_range, ordered_df['industry'])
plt.title('Proportion of vacancies per industry and State', loc = 'center')
plt.xlabel('Industries')
plt.ylabel('Proportion of vacancies')


# 8. Relationship between salaries and size of the firm 
sns.boxplot(x = 'size', y = 'salaries', data = df, order = ['1 to 50', '51 to 200', '201 to 500', '501 to 1000', '1001 to 5000', '10000+', 'Unknown'])
# Set graph title
plt.title('Salaries per number of employees in the firm', loc = 'center')
# y-axis label
plt.ylabel('Salaries')
# x-axis label
plt.xlabel('Number of employees')
# Set industry labels vertical
plt.xticks(rotation = 90)


# 9. Vacancies per salary level and size of the firm 
avg_salarie = df['salaries'].mean()
x = df.groupby('industry')['salaries'].mean().reset_index()
x['Pay'] = pd.Series()
for i in range(x.shape[0]):
    if x.iloc[i,1] > avg_salarie:
        x.iloc[i,2] = 'High_pay'
    else:
        x.iloc[i,2] = 'Low_pay'
y = df.groupby(['industry', 'size']).count().reset_index()
x = y.merge(x, how = 'outer', on = 'industry')
sns.barplot(x = 'size', y = 'company', hue = 'Pay', data = x, order = ['1 to 50', '51 to 200', '201 to 500', '501 to 1000', '1001 to 5000', '10000+', 'Unknown'])
plt.title('Number of vacancies per salary level and number of employees in the firm', loc = 'center')
# y-axis label
plt.ylabel('Vacancies')
# x-axis label
plt.xlabel('Number of employees')
# Set industry labels vertical
plt.xticks(rotation = 90)


# 10. Low pay jobs average salaries per size of the firm
avg_salarie = df['salaries'].mean()
#x = df.groupby('industry')['salaries'].mean().reset_index()
x = df[['industry', 'salaries', 'size']].copy()
x['Pay'] = pd.Series()
for i in range(x.shape[0]):
    if x.iloc[i,1] > avg_salarie:
        x.iloc[i,3] = 'High_pay'
    else:
        x.iloc[i,3] = 'Low_pay'
x = x[x['Pay'] == 'Low_pay']
x = x.groupby('size')['salaries'].mean().reset_index()
sns.barplot(x = 'salaries', y = 'size', data = x, color = 'blue', alpha = 0.8, order = ['10000+','1001 to 5000','501 to 1000','201 to 500','51 to 200','1 to 50','Unknown'])
plt.title('Low pay jobs average salaries per size of the firm', loc = 'center')
# y-axis label
plt.ylabel('Number of employees')
# x-axis label
plt.xlabel('Average salary')
# Set industry labels vertical
plt.xticks(rotation = 90)