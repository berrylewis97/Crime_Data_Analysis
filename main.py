import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import folium
import os


#importing data
raw_data = pd.read_csv(r"C:\Users\USER\Crime_Data_from_2020_to_Present.csv")

data = raw_data.copy()

#Renaming all columns(on the copy)
data.columns = ['File_Number','Report_Date','Occ_Date','Occ_Time','Area_Code','Area_Name',
                'Sub_Area_Code','Crime_degree','Crime_Code','Crime_Desc','Mocodes','Vict_Age',
                'Vict_Sex','Vict_Descent','Place_code','Place_Desc','Weapon_code','Weapon_Desc',
                'Status','Status_Desc','crime_1','crime_2','crime_3','crime_4','Location',
                'Cross_Street','LAT','LON'
               ]

#settings
pd.set_option("display.max_columns",30)
pd.set_option("display.max_rows",200)


# Fixing date columns dtypes
data['Report_Date'] = pd.to_datetime(data["Report_Date"])
data['Occ_Date'] = pd.to_datetime(data["Occ_Date"])


# Fixing Time column 
data['Occ_Time'] = data['Occ_Time'].astype('str').str.zfill(4)
data['Occ_Time'] = data['Occ_Time'].str[:2] +":"+ data['Occ_Time'].str[2:]
data['Occ_Time'] = pd.to_datetime(data["Occ_Time"],format = "%H:%M").dt.time
#adding an hour column
data["Occ_Hour"] = data["Occ_Time"].astype('str').str[:2]

#fixing age column
data = data[data['Vict_Age'].between(0,100)]
data['Vict_Age'] = np.where(data['Vict_Age'] == 0,round(data['Vict_Age'].mean()),data['Vict_Age'])
data['Vict_Age'].value_counts()

#removing unknown genders
data = data[data['Vict_Sex'].isin(['M','F'])]

#fixing race column
data = data[data['Vict_Descent'] != '-']
data.dropna(subset = 'Vict_Descent',inplace = True)
data

#Converting catagorical columns into category dtype

# before 164.7+ MB

for column in data.columns:
    if data[column].nunique() <25:
        data[column] = data[column].astype('category')
    else:
        data[column] = data[column]
        
# after 123.5+ MB



#Makind File_Number More readable
data = data.sort_values(by = 'Report_Date').reset_index(drop = True)
data['File_Number'] = [i.zfill(6) for i in np.arange(0,603684).astype('str')]


#Orgenazing The Data into Tables
Fact = data[['File_Number','Report_Date','Occ_Date','Occ_Time','Area_Code','Sub_Area_Code','Crime_degree','Crime_Code','Status','LAT','LON']]


#Orgenazing The Data into Tables
Dim_Area = data[['Area_Code','Area_Name']].sort_values(by = 'Area_Code').drop_duplicates().reset_index(drop = True)

Dim_Sub_Area = data[['Sub_Area_Code','Area_Name']].sort_values(by = 'Sub_Area_Code').reset_index(drop = True).drop_duplicates()

Dim_Crime = data[['Crime_Code','Crime_Desc']].drop_duplicates().sort_values(by = 'Crime_Code').reset_index(drop = True)

Dim_Sub_Crime = data[['File_Number','Crime_Code','crime_2','crime_3','crime_4']]

Dim_Status = data[['Status','Status_Desc']].drop_duplicates().sort_values(by = 'Status').reset_index(drop = True)

Dim_Weapon = data[['File_Number','Weapon_code','Weapon_Desc']].dropna(how = 'any').reset_index(drop = True)

#information about the Place (Place Description)
Dim_Place = data[['Place_code','Place_Desc']]
Dim_Place = Dim_Place.dropna(how = 'any').drop_duplicates()
Dim_Place['Place_code'] = Dim_Place['Place_code'].astype('int16')
Dim_Place = Dim_Place.sort_values(by = 'Place_code').reset_index(drop = True)

#information about the victim (age, sex, Descent)
Dim_Victim = data.copy()[['File_Number','Vict_Age','Vict_Sex','Vict_Descent']]
#replacing negative values with mean

#לחזור
Dim_Victim['Vict_Age'] = np.where(Dim_Victim['Vict_Age']<1,Dim_Victim['Vict_Age'].mean(),Dim_Victim['Vict_Age'])
Dim_Victim['Vict_Age'].fillna(Dim_Victim['Vict_Age'].mean)
Dim_Victim['Vict_Age']  = Dim_Victim['Vict_Age'].round()
Dim_Victim['Vict_Sex'] = np.where(Dim_Victim['Vict_Sex'].isin(['H', '-']),Dim_Victim['Vict_Sex'].mode(),Dim_Victim['Vict_Sex'])
Dim_Victim['Vict_Sex'] = np.where(Dim_Victim['Vict_Sex'].isnull(),'X',Dim_Victim['Vict_Sex'])



#information about the geographical place 
Dim_Address = data[['Location','Area_Name']].drop_duplicates().sort_values(by = 'Area_Name').reset_index(drop = True)

Dim_Coordinates = data[['File_Number','LAT','LON']]

Dim_LON = pd.DataFrame({"LON_ID":np.arange(10,len(Dim_Coordinates['LON'].unique())+10),"LON":Dim_Coordinates['LON'].unique()})
Dim_LAT = pd.DataFrame({"LAT_ID":np.arange(10,len(Dim_Coordinates['LAT'].unique())+10),"LAT":Dim_Coordinates['LAT'].unique()})

#Replacing LAT and LON Values with the New codes
Fact = Fact.merge(Dim_LON,on = 'LON').merge(Dim_LAT,on = 'LAT').sort_values(by = 'File_Number').reset_index(drop = True).drop(['LAT','LON'],axis = 1)

#Creating a date table
Dim_Date = pd.DataFrame({"Report_Date":pd.date_range(start=Fact['Report_Date'].min(),end=Fact['Report_Date'].max())})

Dim_Date['year'] = Dim_Date['Report_Date'].dt.year
Dim_Date['Quarter'] = Dim_Date['Report_Date'].dt.quarter
Dim_Date['month'] = Dim_Date['Report_Date'].dt.month
Dim_Date['Day'] = Dim_Date['Report_Date'].dt.day

 
Dim_Date['Week_Day'] =Dim_Date['Report_Date'].dt.dayofweek + 2
#sunday = 1, Saturday = 7
Dim_Date['Week_Day'] = np.where(Dim_Date['Week_Day'] == 8 ,1,Dim_Date['Week_Day'])

Dim_Date['Day_Name'] = Dim_Date['Report_Date'].dt.day_name()