import numpy as np
import pandas as pd
import create_data as cd
import graph_type_process as gt

class test_anomaly():
    '''
    inp: 
        - name: name of series
        - arr_val: value series
        - arr_date: date series
        - seasonal: seasonal value (7)
        - graph type:
        - output_param: anomaly param, adjusted param
    '''
    
    def __init__(self, name, arr_date, arr_val, assign_graph):
        self.name = name
        self.seriesdate = arr_date
        self.seriesval = arr_val
        self.season = None
        self.trend_des = None
        
        
        '''
        trend description:
        - above trend-line: 1: above linear trend, 0: equal linear trend, -1: under linear trend  
        - increasing or decreasing: -1: trend decreasing, 1: trend increasing, 0: flat trend  
        - previous high: previous high trend value 
        '''
        
        if(assign_graph==''):
            self.graph_type = gt.determine_graphtype(self.seriesval)
        else:
            self.graph_type = assign_graph
        
        self.trendanomaly = 0 # trend anomaly
        self.noiseanomaly = 0
        self.seasonanomaly = 0 # seasonal anomaly
        
        self.adjusted_val = None
        self.param = None # mean, low, high
    
    def get_ma(self):
        arr_val = self.seriesval
        
        n = len(arr_val)
        ma = np.empty(n)
        ma.fill(np.NaN)
        ma[6:n] = map(lambda i: np.mean(arr_val[i-6:i+1]), range(6,n))
        
        return ma
    
    
    def get_trend(self):
        trend = gt.complex_smooth(self.seriesval)
        return trend
    
    def get_noise(self):
        trend = self.get_trend()
        n = len(self.seriesval)
        noise = map(lambda i: self.seriesval[i] - trend[i], range(0, n))
        return noise
        
    def get_seasonality(self):
        df_data = pd.DataFrame({'date':self.seriesdate})
        
        arr_data = self.seriesval
        trend = self.get_trend()
        n = len(self.seriesval)
        
        seasonality = np.empty(len(trend))
        seasonality.fill(np.nan)
        
        for i in range(0, n):
            seasonality[i] =  arr_data[i]/trend[i]
        
        df_data.insert(1, 'seasonality', seasonality)
        return df_data 
            
    
    def update_param(self, param):
        self.param = param
        
    
