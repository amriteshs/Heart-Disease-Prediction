import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import json
import task02


def get_data(file):
    usecols=['age','sex','chest_pain','blood_pressure','serum_cholesterol','blood_sugar',
             'electrocardiographic_result','max_heart_rate','exercise_induced',
             'old_peak','slope','major_vessels','thal','target']
    df = pd.read_csv(file,sep=',',header=None ,names=usecols)
    
    df.replace('-', np.nan)
    return df

def scattered_json():
    df = t2.get_data("processed.cleveland.data")
    df = t2.data_cleansing(df)
    scattered_json = [] 
    for col in df:
        if col != 'age' and col != 'sex':
            record = {}

            title = {}
            title['text'] = 'Age (x-axis) and ' + col.replace("_"," ").title()+' (y-axis)'
            record['title'] = title

    
            xAxis = {}
            
            xtitle = {}
            xtitle['text'] = 'Age'
            xAxis['title'] = xtitle

            record['xAxis'] = xAxis


            yAxis = {}
            
            ytitle = {}
            ytitle['text'] = 'Age (x-axis) and ' + col.replace("_"," ").title()+' (y-axis)'
            yAxis['title'] = ytitle

            record['yAxis'] = yAxis

            
            
            series = []

            male_series = {}
            male_series['name']= 'Male'
            male_series['colour']='rgba(119, 152, 191, .5)'            
            male_series['data'] = df.loc[df['sex'] == 1,['age',col]].values.tolist()
            series.append(male_series)

            female_series = {}
            female_series['name']= 'Female'
            female_series['colour']='rgba(223, 83, 83, .5)'
            female_series['data'] = df.loc[df['sex'] == 0,['age',col]].values.tolist()
            series.append(female_series)

            record['series'] = series

            #print(record)
            json_record = json.dumps(record)

            scattered_json.append(json_record)
            

            '''
            plt.scatter(x=male['age'],y=male[col],c='Blue', label='Male')
            plt.scatter(x=female['age'],y=female[col],c='Pink', label='Female')
            #plt.title('Age (x-axis) and ' + col.replace("_"," ").title()+' (y-axis)', fontsize=20)
            plt.xlabel('Age', fontsize=18)
            plt.ylabel(col.replace("_"," ").title(), fontsize=16)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.11), ncol=2)
            plt.show()
            '''
    
        
    return scattered_json

def stacked_json():
    #load data
    df = task02.get_data("processed.cleveland.data")
    
    #data cleansing
    df = task02.data_cleansing(df)

    #binning
    df = binning(df,'age',3)
    age_cat = df['age_bin'].unique()
    age_cat.sort()
    #print(age_cat)
    to_bin = ['blood_pressure','serum_cholesterol','max_heart_rate','old_peak']
    for x in to_bin:
        df = binning(df,x,4)

    # list of columns to stack
    to_stack = ['chest_pain', 'blood_pressure_bin', 'serum_cholesterol_bin', 'blood_sugar',
                'electrocardiographic_result', 'max_heart_rate_bin', 'exercise_induced', 'old_peak_bin', 'slope',
                'major_vessels', 'thal']
    
    #replace values for proper labeling of stack
    df['chest_pain'].replace([1,2,3,4],['typical angin','atypical angin','non-anginal pain','asymptomatic'], inplace=True)
    df['blood_sugar'].replace([0,1],['no','yes'], inplace=True)
    df['electrocardiographic_result'].replace([0,1,2],['normal','having ST-T wave abnormality','showing probable or definite leftventricular hypertrophy by Estes’ criteria'], inplace=True)
    df['thal'].replace(['3.0','6.0','7.0'],['normal','fixed dafect','reversable defect'],inplace=True)

    #prepare json data to be sent for grouped stack bar chart
    scattered_data = [] 
    for col in to_stack:
        record = {}

        chart ={}
        chart['type'] = 'column'
        record['chart'] = chart
        
        title ={}
        title['text'] = col.replace("_bin","").replace("_"," ").title() + " grouped by Age and Gender"
        record['title'] = title
        
        xAxis = {}
        xAxis['categories'] = age_cat.tolist()
        labels = {}
        labels['y'] = 45
        xAxis['labels'] = labels
        record['xAxis'] = xAxis
        
        yAxis = {}
        yAxis['allowDecimals'] = 'false'
        yAxis['min'] = 0
        title = {}
        title['text']= col.replace("_"," ").title()
        yAxis['title'] = title
        record['yAxis'] = yAxis
        
        series = []
        #get cat
        col_cat = df[col].unique()
        #col_cat.sort()      
        for cat in col_cat:
            series_m ={}
            series_m['name'] = str(cat).title()
            
            series_f = {}
            series_f['name'] = str(cat).title()
            
            tot_per_age_m = []
            tot_per_age_f = []
            
            for a_cat in age_cat:
                tot_per_age_m.append(float(df['age'][(df['sex']==1)&(df['age_bin']==a_cat)&(df[col]==cat)].count()))

                tot_per_age_f.append(float(df['age'][(df['sex']==0)&(df['age_bin']==a_cat)&(df[col]==cat)].count()))
                
            series_m['data'] = tot_per_age_m
            series_m['stack'] = 'Male'

            
            series_f['data'] = tot_per_age_f
            series_f['stack'] = 'Female'
            
            series.append(series_m)
            series.append(series_f)
        record['series'] = series
        
        # print("inside this function")
        # print(type(record))
        json_record = json.dumps(record)
        # print(type(json_record))
        scattered_data.append(record)
       
    return scattered_data


def binning(df,col,num_bins,labels=[]):
    '''
    binning for age using histogram analysis and creates a new column with bin labels
    optional labels parameter - if there is a defined definition for the label
    '''
    #print(len(labels))
    hist,bin_edges = np.histogram(df[col],num_bins)
    #filter
    start = bin_edges[0]
    bins = list()
    
    #add bin to column
    df[str(col)+'_bin'] = None
    for i in range(1,len(bin_edges)):
        
        #labelling
        if len(labels) != num_bins:
            if bin_edges[-1] == bin_edges[i]:
                df.loc[(df[col] >= start) & (df[col] <= round(bin_edges[i])),[str(col)+'_bin']]= str(int(round(start)))+ "-" + str(int(round(bin_edges[i])))
            else:
                df.loc[(df[col] >= start) & (df[col] < round(bin_edges[i])),[str(col)+'_bin']]= str(int(round(start)))+ "-" + str(int(round(bin_edges[i])-1))
        else:
            if bin_edges[-1] == bin_edges[i]:
                df.loc[(df[col] >= start) & (df[col] <= round(bin_edges[i])),[str(col)+'_bin']]= labels[i-1]
            else:
                df.loc[(df[col] >= start) & (df[col] < round(bin_edges[i])),[str(col)+'_bin']]= labels[i-1]
        start = round(bin_edges[i])
    return df


#print(stacked_json())



  
#print(scattered_json())            
'''
chosen_col = ['chest_pain','electrocardiographic_result']#,  'electrocardiographic_result', 'major_vessels', 'thal', 'target']
df = get_data("processed.cleveland.data")
#example bin size is 8
labels=['a','b','c','d','e','f','g','h']
df = binning(df,'age',8)
age_stacked_bar(chosen_col,df)
#age_scattered(df)
'''