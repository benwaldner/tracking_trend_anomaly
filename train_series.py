from calendar import week
from pandas.core.frame import DataFrame
import numpy as np 
import create_data2 as cd
import test_series1 as ts


import graph_type_process as gt 


class train_anomaly():
    '''
    inp: 
        - name: name of series
        - arr_val: value series
        - arr_date: date series
        - season: season value (7)
    '''
    
    def __init__(self, name, list_val, list_date, assign_graph):
        self.name = name
        self.seriesval = list_val
        self.seriesdate = list_date
        self.season = None
        
        if (assign_graph==''):
            '''
            graph types include: non-season, season-7
            '''
            self.graph_type = gt.determine_graphtype(list_val)
        else:
            self.graph_type = assign_graph
            
        if(self.graph_type=='season-7'):
            self.season = 7
        self.param = self.create_param()
    
######################################## CREATE PARAMS ####################################################
    def create_param(self):
        param = {}
        arr = self.seriesval
        trend = gt.complex_smooth(arr)
        n = len(trend)
        
        trend_tmp = trend[6:n]
        arr_tmp = arr[6:n]
        n_tmp = n-7
        
        del_trend = map(lambda i: trend_tmp[i] - trend_tmp[i-1], range(1,n_tmp+1))
        [low, m, up] = gt.determine_quantile(del_trend)
        param.update({'low_trend_del':low, 'mean_trend_del':m, 'up_trend_del': up})
        
        if (self.graph_type == 'non-season'):
            noise = map(lambda i: arr_tmp[i] - trend_tmp[i], range(0, len(arr_tmp)))
            [low_noise, m_noise, up_noise] = gt.determine_quantile(noise)
            param.update({'low_noise':low_noise, 'mean_noise':m_noise, 'up_noise': up_noise})
        elif (self.graph_type == 'season-7'):
            season_param = self.compute_season_param()
            param.update(season_param)
        return param
    
    def compute_season_param(self):
        seasonal_train = {'Monday': self.get_seasonal_series(self.season, 'Monday'), 'Tuesday': self.get_seasonal_series(self.season, 'Tuesday'), 
                              'Wednesday': self.get_seasonal_series(self.season, 'Wednesday'), 'Thursday': self.get_seasonal_series(self.season, 'Thursday'), 'Friday': self.get_seasonal_series(self.season, 'Friday'), 
                              'Saturday': self.get_seasonal_series(self.season, 'Saturday'), 'Sunday': self.get_seasonal_series(self.season, 'Sunday')}
        wd = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] 
        season_param = {}
        for k in wd:
            seasonal_part_day = seasonal_train.get(k)
            med = np.median(seasonal_part_day)
            s =   np.std(seasonal_part_day)
            season_param.update({k:[med, s]})
        return season_param


################################################ FIND PREVIOUS HIGH ##################################################
    def find_previous_high(self, test_inst):
        n = len(test_inst.seriesval)
        trend = gt.complex_smooth(test_inst.seriesval)
        pre_high = None
        
        if(trend[n-1] < max(trend[n-14:n-2])):
            m = max(trend[n-14:n-2])
            m_ind = list(trend[n-14:n-2]).index(m)
            pre_high_ind = n-14 + m_ind
            pre_high = [test_inst.seriesdate[pre_high_ind], test_inst.seriesval[pre_high_ind]]
            
        else:
            for i in range(n-14, 7, -1):
                if(trend[n-1] <= trend[i]):
                    pre_high_ind = i
                    pre_high = (test_inst.seriesdate[pre_high_ind], test_inst.seriesval[pre_high_ind])
                    break
        return pre_high
    
    def trend_description(self, test_inst):
        
        ############################# under of above trend line ################
        above_under_line = 0
        linear_trend = gt.linear_smooth(test_inst.seriesval)
        trend = gt.complex_smooth(test_inst.seriesval)
                
        n = len(trend)
        if(trend[n-1] < linear_trend[n-1]):
            above_under_line = -1
        elif(trend[n-1] > linear_trend[n-1]):
            above_under_line = 1
        else:
            above_under_line = 0
                    
        ########################### trend increase or decrease #################
        trend_delta = 0
        if(trend[n-1] > trend[n-2]):
            trend_delta = 1
        elif(trend[n-1] < trend[n-2]):
            trend_delta = -1
        else:
            trend_delta = 0
        
        ########################### previous high ##############################
        pre_high = self.find_previous_high(test_inst)
        
        ######################### decrease continuously in 3 days ##############        
        dec_3day = 0
        if(trend[n-1] < trend[n-2] and trend[n-2] < trend[n-3] and trend[n-3] < trend[n-4]):
            dec_3day = 1
        #################################################################
        
        trend_dict = {}
        trend_dict.update({'above or under linear trend': above_under_line})
        trend_dict.update({'increasing or decreasing trend': trend_delta})
        trend_dict.update({'previous high trend': pre_high})
        trend_dict.update({'trend decreases 3 days': dec_3day})
        
        test_inst.trend_des = trend_dict
        return test_inst
        
    
    def check_trend(self, test_inst):
        trend = gt.complex_smooth(test_inst.seriesval)
        
        n = len(trend)
        trend_delta = trend[n-1] - trend[n-2]
        # 'low_trend_del':low, 'mean_trend_del':m, 'up_trend_del'
        low = self.param.get('low_trend_del')
        up = self.param.get('up_trend_del')
        adjusted_param = {}
        
        if(trend_delta < low):
            return -1
        elif(trend_delta > up):
            return 1
        else:
            return 0
        
    def check_noise(self, test_inst):
        noise = test_inst.get_noise()
        n = len(noise)
        low = self.param.get('low_noise')
        up = self.param.get('up_noise')
        if (noise[n-1] > up):
            return 1
        elif (noise[n-1] < low):
            return -1
        else:
            return 0
    
    
    def check_season(self, test_inst):
        arr_date = self.seriesdate
        n = len(arr_date)
        k = arr_date[n-1].strftime("%A")
        
        dfsea = test_inst.get_seasonality()
        
        h = len(dfsea.index)
        sea = dfsea.ix[h-1,dfsea.columns[1]]
        
        [med, s] = self.param.get(k)
        
        low = med - 3*s
        up = med + 3*s
        
        if ( sea > up):
            return 1
        elif (sea < low):
            return -1
        else:
            return 0
    
########################################## CHECK TEST DATA ##########################################################    
    def check_anomaly(self, test_inst):
        if (self.graph_type == "non-season"):
            ct = self.check_trend(test_inst)
            cn = self.check_noise(test_inst)
            test_inst.trendanomaly = ct
            test_inst.noiseanomaly = cn
             
            
        elif (self.graph_type == "season-7"):
            ct = self.check_trend(test_inst)
            cs = self.check_season(test_inst)
            test_inst.trendanomaly = ct
            test_inst.seasonanomaly = cs
        
        return test_inst
    
         
    def get_seasonal_series(self, seas_param, w = None):
        if (w == None):
            return None
        
        ma = self.moving_avg1(seas_param)
        start_point = 6
        inp_w = w 
        seasonal_part = []
        
        for i in range(start_point, len(ma)):
            sea = self.seriesval[i]/ma[i]
            k = self.seriesdate[i].strftime("%A")
            if (k==inp_w):
                seasonal_part.append(sea)
            
        return seasonal_part
    
    
    def moving_avg1(self, ma_param):
        ma = np.empty(len(self.seriesval))
        ma.fill(np.nan)
        start_point = ma_param-1
        
        for i in range(start_point, len(self.seriesval)):
            ma[i] = np.mean(self.seriesval[i-start_point:i+1])
        return ma
    
    
    def adjust_data(self, test_inst):
        return 0
         
    
    
    
