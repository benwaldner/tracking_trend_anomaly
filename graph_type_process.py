import numpy as np
import pandas as pd
from scipy import signal as sn
from scipy.stats import norm
from scipy.stats import gumbel_l
from scipy.stats import gumbel_r

def determine_graphtype(arr):
    sig_level = 0.99
    trend = complex_smooth(arr)
    sea_comp = map(lambda i: arr[i]/trend[i], range(0,len(arr)))
    
    sea = determine_season(sea_comp, sig_level)
    
    if (sea==0):
        return 'non-season'
    elif(sea ==1 ):
        return 'season-7'
    return 'NaN'


def determine_quantile(arr):
    
    # https://en.wikipedia.org/wiki/Gumbel_distribution
    
    p_low = 0.025
    p_up = 0.975
    n = len(arr)
    m = np.average(arr)
    s = np.std(arr)
    euler = 0.5772
    beta = s*np.sqrt(6)/np.pi
    muy = m - euler*beta
    
    quan_low = muy - beta*np.log(-np.log(p_low))
    quan_up = muy - beta*np.log(-np.log(p_up))
    
    return [quan_low, m, quan_up]


def determine_season(arr, sig_level):
    n = len(arr)
    smooth = complex_smooth(arr)
    linear = linear_smooth(arr)
    sea_comp = map(lambda i: arr[i]/smooth[i], range(6,n))
    
    
    acf = cal_acf(sea_comp)
    can_sea = 7
    sea = []
    
    i = can_sea
    
    #cri_val = norm.pdf(sig_level, loc = 0, scale = 1)
    cri_val = 0.4
    acf_max = max(map(lambda i: abs(acf[i]), range(1,len(acf))))
    
    if(acf[i] > cri_val and acf[i]==acf_max):
        return 1
    return 0


def linear_smooth(arr):
    n = len(arr)
    coeff = np.polyfit(range(0,n), arr, 1)
    
    trend_line = []
    for i in range(0,n):
        trend_line.append(i * coeff[0] + coeff[1])
    return trend_line


def estimated_autocorrelation(x):
    """
    http://stackoverflow.com/q/14297012/190597
    http://en.wikipedia.org/wiki/Autocorrelation#Estimation
    """
    n = len(x)
    variance = x.var()
    x = x-x.mean()
    r = np.correlate(x, x, mode = 'full')[-n:]
    assert np.allclose(r, np.array([(x[:n-k]*x[-(n-k):]).sum() for k in range(n)]))
    result = r/(variance*(np.arange(n, 0, -1)))
    return result


def cal_acf(data):
    n = len(data)
    mean = np.mean(data)
    c0 = np.sum((data - mean) ** 2) / float(n)

    def acf(h):
        acf_lag = ((data[:n - h] - np.mean(data[:n - h])) * (data[h:] - np.mean(data[h:]))).sum() / float(n) / c0
        return round(acf_lag, 3)
    
    
    x = np.arange(12) 
    acf_coeffs = map(lambda i: acf(i), x)
    
    print str(acf_coeffs).strip('[]')
    return acf_coeffs

def complex_smooth(arr):
    #y = sn.savgol_filter(arr,7,1)
    y = my_ma(arr)
    return y

def my_ma(arr):
    
    arr_ma = map(lambda i: np.mean(arr[0:i]), range(1,8))
    arr_ma_tmp = np.empty(len(arr)-7)
    arr_ma_tmp.fill(np.NaN)
    arr_ma.extend(arr_ma_tmp)
    
    for i in range(6, len(arr)):
        arr_ma[i] = np.mean(arr[i-6:i+1])
    
    return arr_ma

    
def all_in_one():
    df = pd.read_csv("dat_1005_3108.txt", header=0, index_col=None)
    arr_val = df['msg']
    
    trend_del = []
    sea = []
    for i in range(10, len(arr_val)):
        nonlinear_tmp = complex_smooth(arr_val[0:i+1])
        n = len(nonlinear_tmp)
        trend_del.append(nonlinear_tmp[n-1]-nonlinear_tmp[n-2])
        sea.append(arr_val[n-1]/nonlinear_tmp[n-1])
    print sea
    
    ma = my_ma(arr_val)
    nonlinear = complex_smooth(arr_val)
    linear = linear_smooth(arr_val)
    
    