import pandas as pd


def read_date_value(f_inp):
    '''
    inp:
        f_inp: input data file
    out:
        dataframe of data
    '''  
    
    df_data = pd.read_csv(f_inp, header=0, index_col=None, sep=",")
    return df_data

def read_value(f_inp):
    df_data = pd.read_csv(f_inp, header=0, index_col=None, sep=",")
    cols = df_data.columns
    arr = df_data[cols[1]].values
    return arr

