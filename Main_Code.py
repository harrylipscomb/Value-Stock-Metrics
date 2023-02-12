# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 16:27:31 2021

@author: Harry Lipscomb
"""

import pandas as pds
import numpy as np
import matplotlib.pyplot as plt

def main():
    portfolio_size = 30
    length_of_holding = 22
    invested_amount = 1
    
    def filter_function(large_data): #set conditions for pool of stocks to be analysed.
        number_companies = len(large_data[:, 0])
        required_data_set = np.zeros([1, len(large_data[0, :])])
        index = 0
        while index < number_companies:
            market_value = large_data[index, 10]
            date_of_data = large_data[index, 1]
            if (date_of_data < 2005 and market_value > 2000) or (market_value > 5000):
                required_data_set = np.vstack([required_data_set, large_data[index, :]])
            index += 1
        required_data_set = np.delete(required_data_set, obj=0, axis=0)
    
        return required_data_set
    
    def return_on_capital(net_income, dividends, debt, equity):
        roc = (net_income - dividends)/(debt + equity)
        
        return roc
    
    def earnings_yield(ebit, enterprise_value): 
        earnings_yield = ebit/enterprise_value
    
        return earnings_yield
    
    def weighting_function(return_on_capital, earnings_yield, debt, equity):
        if equity < 0:
            weighting = -100
        elif (return_on_capital < 0) and (earnings_yield < 0): 
            weighting = -1 * return_on_capital * earnings_yield * (np.exp((-1*debt)/equity))
        else:
            weighting = return_on_capital * earnings_yield * (np.exp((-1*debt)/equity))
    
        return weighting
    
    #-----------------------------------------------------------------------------
    #preparing data file
    
    file = ('C:\Investing\Value_Stock_Metrics\Study_1\BIG_DATA_SET.xlsx')
    xls = pds.ExcelFile(file)
    df1 = pds.read_excel(xls)
    large_data = df1.to_numpy()
    
    large_data_rows, large_data_columns = large_data.shape
    stock_metrics = large_data_columns + 3 + 1 #plus 1 for indexs added
    
    x = 0
    y = 0
    
    for x in range(0, large_data_rows):
        y = 0
        for y in range(3, large_data_columns):
            cell = large_data[x, y]
            if  np.isnan(cell): 
                large_data[x, y] = 0.0
    
    #ebit column 6
    
    delete_list = []
    for i in range(0, large_data_rows):
        if large_data[i, 6] == 0:
            delete_list.append(i)
    large_data = np.delete(large_data, delete_list, axis=0)
    
    #date must be in first column
    
    for position, date in enumerate(large_data[: , 0]):
        date = date.strftime('%Y')
        date = int(date)
        large_data[position, 0] = date + 1
    
    large_data_rows, large_data_columns = large_data.shape
    large_data = np.column_stack([np.arange(0, large_data_rows, 1), large_data])
    
    data = filter_function(large_data)
    
    data_rows, data_columns = data.shape
    data = data[data[:, 1].argsort()] #sorts data in order of date
    
    #-----------------------------------------------------------------------------
    #adding return on capital column 
    
    return_on_capital_column = np.empty([data_rows, 1])
    
    for i in range(0, data_rows):
        if (data[i, 5] + data[i, 9]) == 0:
            return_on_capital_column[i, 0] = 0
        else:
            return_on_capital_column[i, 0] = return_on_capital(
                data[i, 8], data[i, 6], data[i, 5], data[i, 9])
    
    data = np.column_stack([data, return_on_capital_column])
    
    #-----------------------------------------------------------------------------
    #adding an earnings yield column
    
    earnings_yield_column = np.empty([data_rows, 1])
    
    for i in range(0, data_rows):
       enterprise_value = data[i, 9] + data[i, 5] - data[i, 4]
       if enterprise_value == 0:
           earnings_yield_column[i, 0] = 0
       else:
           earnings_yield_column[i, 0] = earnings_yield(data[i, 7], enterprise_value)
    
    data = np.column_stack([data, earnings_yield_column])
    
    #-----------------------------------------------------------------------------
    #Split data and add weighting function column.
    
    yearly_data = np.split(data, np.where(np.diff(data[:,1]))[0]+1)
    
    for year, array in enumerate(yearly_data):
        array_rows, array_columns = array.shape
        weighting_column = np.empty([array_rows, 1])
        for i in range(0, array_rows):
            weighting_column[i, 0] = weighting_function(array[i, 11], array[i,12], array[i, 5], array[i, 9])
        yearly_data[year] = np.column_stack([array, weighting_column])
        yearly_data[year] = yearly_data[year][yearly_data[year][:, 13].argsort()[::-1]]
    
    required_portfolios = np.array([])
    
    for year, companies in enumerate(yearly_data):
        required_portfolios = np.append(required_portfolios, [companies[0:(portfolio_size+10), :]])
        
    required_portfolios = np.reshape(required_portfolios, [int(len(required_portfolios)/stock_metrics), stock_metrics])
    
    data_rows, data_columns = data.shape
    
    relevant_indexs = required_portfolios[:, 0]
    returns = np.array([])
    
    for index in relevant_indexs: #Finds corresponding returns of companies making up portfolios.
        try:
            if (large_data[index, 1] == (large_data[index+1, 1] - 1)) and (large_data[index, 2] == (large_data[index+1, 2])):
                company_return = (((large_data[index+1, 10] / large_data[index, 10]) - 1) * 100)
                returns = np.append(returns, [large_data[index, 1], company_return])
        except IndexError:
            print('There was an index error.')
            continue
    
    return_rows = int((returns.shape[0]/2))
    returns = np.reshape(returns, [return_rows, 2])
    seperated_returns = np.split(returns, np.where(np.diff(returns[:,0]))[0]+1)
    
    for year, array in enumerate(seperated_returns): #Ensures portfolios are correct size.
        excess_stocks = len(array[:, 1]) - portfolio_size
        if excess_stocks > 0:
            array = array[:(-excess_stocks), :]
            seperated_returns[year] = array
    
    value_array = np.array([invested_amount])
    print('Annual Returns for Portfolio of', portfolio_size, 'stocks per year.')
    growth_array = np.array([])
    for year in seperated_returns:
        growth_array = np.append(growth_array, np.average(year[:, 1])/100 + 1)
        invested_amount = invested_amount * ((np.average(year[:, 1])/100) + 1)
        print(round(year[0,0], 0), ':', round(np.average(year[:, 1]), 2), '%')
        value_array = np.append(value_array, invested_amount)
    
    #-----------------------------------------------------------------------------
    #Plotting final results: 
        
    #delete final year if insufficient data:
    value_array = np.delete(value_array, len(value_array)-1)
    
    starting_year = 1999
    CAGR = ((value_array[len(value_array)-1]**(1/length_of_holding)) - 1)*100
    volatility = np.std(growth_array[0:len(growth_array)-1])
    
    print("Final amount is: " + str(round(value_array[len(value_array)-1], 3)))
    print("Volatility of returns: " + str(round(volatility, 3)))
    print("CAGR: " + str(round(CAGR, 2)) + "%")
    
    plt.figure()
    plt.title('The growth of $1 invested in return on capital*earnings yield*e^(-debt/equity) weighted stocks')
    years = np.arange(1998, 2021, 1)
    plt.plot(years+1, value_array, ':', label='Study 1 Portfolio Returns (' + str(portfolio_size) + ' Stocks), CAGR: ' + str(round(CAGR, 2)) + '%, Volatility: ' + str(round(volatility, 2)) + ' (annual)')
    plt.yticks(ticks=np.arange(0, round(value_array[len(value_array)-1]), step=1))
    plt.xticks(ticks=np.arange(1998, 2023, step=2))
    plt.legend()
    plt.grid()
    
    #import total stock market data and figures. note: here large cap stocks are used
    #as in the case of study 1. the total market is also shown in comparison to this.
    
    excel_file = pds.ExcelFile(r'C:\Investing\Value_Stock_Metrics\Study_1\totalmarket.xlsx')
    df2 = pds.read_excel(excel_file, sheet_name='Values by Period')
    total_market_data = df2.to_numpy()
    
    total_market_returns_data = total_market_data[:, 1]
    dates = np.arange((11995/6), (24253/12), (1/12))
    
    volatility = np.std(total_market_data[0:portfolio_size, 3])
    plt.plot(dates, total_market_returns_data, ':', label='Total US Stock Market Returns, CAGR: 7.09%, Volatility: 0.78 (monthly)')
    plt.legend()
    plt.xlabel('Year')
    plt.ylabel('Value of $1 invested in 1999')
    plt.show()
