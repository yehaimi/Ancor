#### Author: Haimi Ye (Brian) ;
#### Date: 2022-08-07 ;
#### Note: To make this program work, please place the target excel in your python projects and have packages pre-installed ;
####       To change the input for the analysis, go to INPUT Section and key in the asset and benchmark accordingly

import pandas as pd
import numpy as np
import scipy.stats as sci

######################################## INPUT Section ########################################

asset_input = ['SPY', 'IWM']
benchmark_input = ['S&P 500 Index']
combine_list = asset_input + benchmark_input

######################################## ETL Process ########################################

### load assets data from excel DB and clean it
assetdb = pd.read_excel('Assignment DB.xlsx', sheet_name='Assets')
assetdb.columns = assetdb.iloc[0]  ### use symbol as column names
assetdb = assetdb.drop([0, 1], axis=0) ### drop first two rows
assetdb.rename(columns = {'Symbol':'Date'}, inplace = True) ### rename the first column to be Date
assetdb = assetdb[['Date'] + asset_input] ### extract data for the asset from input only
assetdb.reset_index(inplace=True) ### reset_index
assetdb = assetdb.drop(['index'], axis=1)

### load benchmarks data from excel DB, Clean it, and Convert the value to be return
benchmarkdb = pd.read_excel('Assignment DB.xlsx',sheet_name='Benchmarks')
benchmarkdb = benchmarkdb.drop([0,1],axis=0) ### drop first two rows
benchmarkdb.rename(columns = {'Descriptive Name':'Date'}, inplace = True) ### rename the frist column to be Date
benchmarkdb = benchmarkdb[['Date'] + benchmark_input] ### extract data for the benchmark from input only
benchmarkdb.reset_index(inplace=True) ### reset_index
b = benchmarkdb.copy()
rownumber = len(benchmarkdb.index) - 1
for i in range(rownumber):
    b.iloc[i+1] = ( benchmarkdb.iloc[i+1] / benchmarkdb.iloc[i] ) - 1  ### convert the value to be return
b['Date'] = benchmarkdb['Date'] ### rebuild Date column
benchmarkdb = b
benchmarkdb = benchmarkdb.drop(['index'],axis=1)

### Join assets data and benchmark data by Date
data_merge = pd.merge(assetdb, benchmarkdb, left_on='Date', right_on='Date')

######################################## Slicing data into different Periods ########################################

df1 = data_merge[-12:]  ### 1 year data
df2 = data_merge[-36:]  ### 3 year data
df3 = data_merge[-60:]  ### 5 year data
df4 = data_merge[-84:]  ### 7 year data
df5 = data_merge[-120:]  ### 10 year data
df6 = data_merge[-180:]  ### 15 year data
df7 = data_merge[-240:]  ### 20 year data
# df8 = data_merge[]  ### data since inception

######################################## Function to calculate risk measures ########################################

def riskmetric(data):
    r = 1
    rownumber = len(data.index) - 1
    t = len(data.index)/12  ### how many years for compounding

    ### Calculate Cumulative Return
    for i in range(rownumber):
        r = r * (data.iloc[i] + 1)
    cum_return = r - 1
    metric = pd.DataFrame(data=cum_return,columns=['Cumulative Return'])
    metric = metric.drop(['Date'],axis=0)
    pd.options.display.float_format = '{:.2%}'.format

    ### Calulate CAGR
    metric['CAGR'] = (metric['Cumulative Return'] + 1) ** (1/t) - 1

    ### Calculate Standard Deviation
    metric['Standard Deviation'] = data.std()

    ### Calculate Beta
    corr = 0
    cov = 0
    metric['Beta'] = 0
    for j in combine_list:
        corr = np.corrcoef(data[j].astype('float64'), data[benchmark_input[0]].astype('float64'))[0,1]
        cov = corr * metric.loc[[j], 'Standard Deviation']
        metric.loc[[j], 'Beta'] = cov / metric.loc[benchmark_input[0],'Standard Deviation']

    ### Calulate CVaR 95%
    metric['CVaR 95%'] = 0
    for j in combine_list:
        pm = data[j].mean()
        ps = data[j].std()
        VaR_95 = sci.norm.ppf(0.95, loc = pm, scale = ps)
        tail_loss = sci.norm.expect(lambda x: x, loc = pm, scale = ps, lb = VaR_95)
        CVaR_95 = (1 / (1 - 0.95)) * tail_loss
        # print(type(CVaR_95))
        metric.loc[[j], 'CVaR 95%'] = CVaR_95

    ### Maximum Drawdown
    metric['Maximum Drawdown'] = 0
    peak = 0
    trough = 0
    for j in combine_list:
        v = 1
        list = []
        mask = data[j]
        mask = mask + 1
        for i in mask:
            v = v * i
            list.append(v)
        peak = max(list)
        trough = min(list[list.index(max(list)):])
        draw = (peak - trough) / peak
        metric.loc[[j], 'Maximum Drawdown'] = draw

    print(metric)

######################################## Populate DataFrame for different periods ########################################

print("1 Year Metric:")
riskmetric(df1)

print("3 Year Metric:")
riskmetric(df2)

print("5 Year Metric:")
riskmetric(df3)

print("5 Year Metric:")
riskmetric(df4)

print("10 Year Metric:")
riskmetric(df5)

print("15 Year Metric:")
riskmetric(df6)

print("20 Year Metric:")
riskmetric(df7)

print("Metric Since Inception:")
# riskmetric(df8)

