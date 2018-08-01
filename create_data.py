
import read_data as rd
import pandas as pd
import re
import test_series as ts
import train_series as train
import datetime as dt


detail_metric = []
operator_metric = []
hour_metric = []


location_metric_hcm = []
location_metric_hn = []


def create_all_train(f_path, metric_names):
    df = rd.read_date_value(f_path)
    cols = df.columns
    arr_date = df['date'].values
    list_train = []
    
    for c in cols[1:]:
        if (c in metric_names):
            df_sing = pd.DataFrame({'date':arr_date, c:df[c].values})
            assign_graph = ''
            
            obj_train = create_sing_train(df_sing, assign_graph)
            
            print obj_train.name + "," + obj_train.graph_type
            list_train.append(obj_train)
            
    train_avg =  create_msg_peruser1(df, metric_names, 'train')
    list_train.extend(train_avg)
    return list_train


def create_all_test(f_path, metric_names):
    '''
    return list of test_object, each test_obj is a single metric and only the last value of this obj need to be check for anomaly
    '''
    df = rd.read_date_value(f_path)
    cols = df.columns
    arr_date = df['date'].values
    list_test = []
    
    for c in cols[1:]:
        if (c in metric_names):
            df_sing = pd.DataFrame({'date':arr_date, c:df[c].values})
            assign_graph = ''
            
            obj_test = create_sing_test(df_sing, assign_graph)

            list_test.append(obj_test)
    
    test_avg =  create_msg_peruser1(df, metric_names, 'test')
    list_test.extend(test_avg)
    
    return list_test


def create_msg_peruser1(df, metric_names, train_or_test):
    '''
    create metrics: msg/user for some metrics in the input df 
    '''
    pat1 = 'user_(.*)' 
    pat2 = 'msg_(.*)'
    
    list_train = []
    cols = df.columns
    
    for n in cols[1:]:
        if(n in metric_names):
            y1 = re.findall(pat1, n, re.I)
            if (len(y1)>0):
                user_val = df[n].values
                for i in cols[1:]:
                    y2 = re.findall(pat2, i, re.I)
                    if (len(y2)>0 and y2[0] == y1[0]):
                        msg_val = df[i].values
                        avg_msg = map(lambda x,y: x/y, msg_val, user_val)
                        name = 'msgperuser_' + y1[0]
                        df_avg = pd.DataFrame({'date': df['date'].values})   
                        df_avg[name] = avg_msg
                        
                        assign_graph = ''
                        if(train_or_test == 'train'):
                            obj_train = create_sing_train(df_avg, assign_graph)
                            list_train.append(obj_train)
                            print obj_train.name + "\t" + obj_train.graph_type 
                        elif(train_or_test == 'test'): 
                            obj_test = create_sing_test(df_avg, assign_graph)
                            list_train.append(obj_test)
                            
    return list_train


def create_sing_train(df, assign_graph):
    
    # (self, name, list_val, list_date, assign_graph)
    cols = df.columns
    name = cols[1]
    
    arr_date_tmp = list(df[cols[0]].values)
    arr_date = [dt.datetime.strptime(change_format_date(d),'%m/%d/%Y') for d in arr_date_tmp]
    arr_val = list(df[cols[1]].values.astype(float))
    
    obj_train = train.train_anomaly(name, arr_val, arr_date, assign_graph)
    return obj_train  


def create_sing_test(df, assign_graph):
    
    # (self,name, arr_date, arr_val, season, assign_graph)
    
    cols = df.columns
    name = cols[1]
    arr_date_tmp = list(df[cols[0]].values)
    n = len(arr_date_tmp)
    arr_date1 = []
    
    for i in  range(0,n):
        d = change_format_date(arr_date_tmp[i])
        arr_date1.append(d)
        
    arr_date = [dt.datetime.strptime(change_format_date(d),'%m/%d/%Y') for d in arr_date1]
    arr_val = list(df[cols[1]].values.astype(float))
    obj_test = ts.test_anomaly(name, arr_date, arr_val, assign_graph)
    return obj_test


def change_format_date(d):
    pat1 = '([0-9]+)-([0-9]+)-([0-9]+)'
    y1 = re.findall(pat1, d, re.I)
    
    if(len(y1)>0):
        return y1[0][1]+"/"+y1[0][2]+"/"+y1[0][0]
    return d

def change_format_date_in_df(df):
    date_arr = df['date'].values
    changed_date = []
    
    for d in date_arr:
        str_date = change_format_date(d)
        changed_date.append(str_date)
    df['date'] = changed_date
    return df

def get_graph_type(metric):
    return "None"



