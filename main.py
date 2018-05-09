import os

import read_data as rd
import pandas as pd
import train_series1 as train

import create_data2 as cd
import test_series1 as ts
from datetime import date, timedelta
import datetime as dt
import warning1 as warn
import notify_mail as nm


datadir = ""
train_detail_file = ""
test_detail_file = ""


train_operator_file = ""
test_operator_file = ""


hour_train_dir = ""
hour_test_dir = ""

receiver = ""

def create_train_from_file(f_path, metrics):
    train_list = cd.create_all_train(f_path, metrics)
    return train_list

def create_test_from_file(f_path, metrics):
    test_list = cd.create_all_test(f_path, metrics)
    return test_list



def pipeline(train_path, test_path, metrics, mail_sub):
    train_list = create_train_from_file(train_path, metrics)
    test_list = create_test_from_file(test_path, metrics)
    
    email_content = ''
    for test_obj in test_list:
        for train_obj in train_list:
            if(test_obj.name == train_obj.name):
                test_obj = train_obj.check_anomaly(test_obj)
                test_obj = train_obj.trend_description(test_obj)
                
                email_content += warn.mail_warning_all(test_obj)
                
    outfile = ""
    f_out = open(outfile, "a")
    print >> f_out, email_content
    nm.send_mail(mail_sub, receiver, email_content)                     
    return email_content


def main_detail_location_general(train_path, test_path, loc):

    yes_date = date.today() - timedelta(1)

    if(loc == 'hn'):
        metrics = cd.location_metric_hn
	mail_sub = " " + str(yes_date)

    elif(loc == 'hcm'):
        metrics = cd.location_metric_hcm
	mail_sub = " " + str(yes_date)
        
    content = pipeline(train_path, test_path, metrics, mail_sub)

    return content


def main_detail_location():
    train_path = ""
    test_path = ""
    main_detail_location_general(train_path, test_path, 'hcm')


    train_path = ""
    test_path = ""
    main_detail_location_general(train_path, test_path, 'hn')
    
    return 0


def main_detail_day():
    train_path = os.path.join(datadir, train_detail_file)
    test_path = os.path.join(datadir, test_detail_file)
    
    metrics = cd.detail_metric
    yes_date = date.today() - timedelta(1)
    mail_sub = "Detail chat for date: " + str(yes_date)
    
    pipeline(train_path, test_path, metrics, mail_sub)
    return 0

def main_operator_day():
    train_path = os.path.join(datadir, train_operator_file)
    test_path = os.path.join(datadir, test_operator_file)
    
    metrics = cd.operator_metric
    yes_date = date.today() - timedelta(1)
    mail_sub = "" + str(yes_date)
    
    pipeline(train_path, test_path, metrics, mail_sub)
    return 0


main_detail_day()
main_operator_day()
