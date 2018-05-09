import numpy as np
import pandas as pd
from matplotlib import pyplot as plt 
from scipy import signal as sn
from scipy.stats import norm
from scipy.stats import gumbel_l
from scipy.stats import gumbel_r


def est_skewed_dist():
    r = gumbel_r.rvs(size=1000)
    plt.hist(r, bins=20)
    plt.show()
    

def determine_season(arr, sig_level):
    n = len(arr)
    smooth = complex_smooth(arr)
    linear = linear_smooth(arr)
    ma = my_ma(arr)
    sea_comp = lambda i: arr[i]/smooth[i], range(0,n)
    sea_ma =  lambda i: arr[i]/ma[i], range(0,n)
    
    acf = cal_acf(sea_ma, sig_level)
    can_sea = [7, 30]
    sea = []
    
    for i in sea:
        cri_val = norm.pdf(acf[i], loc=0, scale=1)
        if(acf[i] > cri_val or acf[i] < -cri_val):
            sea.append(i)
    return sea


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
    
    
    x = np.arange(12) # Avoiding lag 0 calculation
    acf_coeffs = map(lambda i: acf(i), x)
    return acf_coeffs

def complex_smooth(arr):
    y = sn.savgol_filter(arr,7,1)
    return y

def my_ma(arr):
    arr_ma = np.empty(len(arr))
    arr_ma.fill(np.NaN)
    for i in range(6, len(arr_ma)):
        arr_ma[i] = np.mean(arr[i-6:i+1])
    
    return arr_ma

    
def all_in_one():
    df = pd.read_csv("D:\\workspace\\R project\\data\\user_1005_3108.txt", header=0, index_col=None)
    arr_val = df['msg']
    
    trend_del = []
    sea = []
    for i in range(10, len(arr_val)):
        nonlinear_tmp = complex_smooth(arr_val[0:i+1])
        n = len(nonlinear_tmp)
        trend_del.append(nonlinear_tmp[n-1]-nonlinear_tmp[n-2])
        sea.append(arr_val[n-1]/nonlinear_tmp[n-1])
        
    #plt.hist(trend_del, bins=30)
    #plt.plot(sea)
    #plt.show()
    print sea
    
    ma = my_ma(arr_val)
    nonlinear = complex_smooth(arr_val)
    linear = linear_smooth(arr_val)
    
    # plot
    
    hand1, = plt.plot(list(arr_val), label='series')
    hand2, = plt.plot(nonlinear, label='savgol_filter')
    hand3, = plt.plot(linear, label='linear')
    hand4, = plt.plot(ma, label='ma')
    plt.legend([hand1, hand2, hand3, hand4], ['series', 'savgol_filter', 'linear', 'ma'])
    plt.show()
    
    

def main():   
    all_in_one()
    #est_skewed_dist()
    
main()
    
    