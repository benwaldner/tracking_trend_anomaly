import numpy as np
import pandas as pd
import os
import notify_mail as notif_mail
import datetime as dt
from datetime import datetime,timedelta 

def mail_warning_point(obj_result):
    alertstring = ''
    
    if (obj_result.trendanomaly == 1):
        alertstring+="Trend increases abnormally"
    elif (obj_result.trendanomaly == -1):
        alertstring+="Trend decreases abnormally"
    
    
    if (obj_result.noiseanomaly == 1):
        alertstring+=" | "
        alertstring+="Noise increases abnormally"
    elif (obj_result.noiseanomaly == -1):
        alertstring+=" | "
        alertstring+="Noise decreases abnormally"
    
    
    if (obj_result.seasonanomaly == 1):
        alertstring+=" | "
        alertstring+="Season increases abnormally"
    elif (obj_result.seasonanomaly == -1):
        alertstring+=" | "
        alertstring+="Season decreases abnormally"
    
    return alertstring

def mail_warning_trend(obj_result):
    alertstring = ''
    trend_param = obj_result.trend_des
    
    above_under_line = trend_param.get('above or under linear trend') # -1,0,1
    trend_delta = trend_param.get('increasing or decreasing trend') # -1,0,1
    pre_high = trend_param.get('previous high trend') # 
    dec_3day = trend_param.get('trend decreases 3 days')
    
    if(above_under_line == 1):
        alertstring += 'Above linear trend'
    elif(above_under_line == -1):
        alertstring += 'Under linear trend'
    
    if(trend_delta==1):
        alertstring += " | "
        alertstring += 'Trend is increasing'
    elif(trend_delta==-1):
        alertstring += " | "
        alertstring += 'Trend is decreasing'
        
    if(dec_3day==1):
        alertstring += " | "
        alertstring += 'Trend decreases 3 days'
    
    if(pre_high == None):
        alertstring += " | " + "Previous high: None"
    if(pre_high!=None):
        pre_high_date = pre_high[0]
        pre_high_val = pre_high[1]
        alertstring += " | " + "Previous high: "
        alertstring += pre_high_date.strftime("%Y-%m-%d")
        #alertstring += "\t %.2f" %(pre_high_val)
    return alertstring


def mail_warning_all(obj_result):
    
    anomaly_string = mail_warning_point(obj_result)
    trend_string = mail_warning_trend(obj_result)
    
    arrval = obj_result.seriesval
    n = len(arrval)
    del_val1 = arrval[n-1] - arrval[n-2]
    del_val7 = arrval[n-1] - arrval[n-8]
    
    
    outstring = '<br>' + obj_result.name.upper() + ": %.2f, +/- pre_date: %.2f, +/- pre_week: %.2f" %(arrval[n-1], del_val1, del_val7)
        
    if(anomaly_string!=''):
        print anomaly_string
        outstring += '<br>'
        outstring += '- ' + anomaly_string
        
    if(trend_string!=''):
        outstring += '<br>'
        outstring += '- ' + trend_string
        
    outstring += '<br>'
    return outstring
    

    
    
    