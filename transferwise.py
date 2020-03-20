from . import tw_api
# import tw_api
import datetime
import requests
import json
import pytz
import pandas as pd
import numpy as np
import math
from pandas_datareader import data as pdr
import yfinance as yf
import scipy.optimize as sco
import sys
import os
import os.path
import time
import yaml
import xlrd
import urllib.request

class transferwise :
    def __init__(self) :
        # reading config parameters
        file = open(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'config.yaml'), 'r')
        data = file.read()
        data = yaml.load(data, Loader=yaml.FullLoader)
        for param in data :
            setattr(self, param, data[param])
        self.data_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], self.data_path)

        self.record_file = os.path.join(self.data_path, 'records.txt')
        self.tw = tw_api.tw_api(api_key=self.api_key)

    def clear_quotes(self) :
        # clear historical quotes
        if os.path.isfile(self.record_file) :
            file = open(self.record_file, 'r')
            records = file.readlines()
            file.close()
        else :
            records = []

        if len(records) > 0 :
            for record in records :
                record = record.replace('\n' , '')
                record_parts = record.split(',')
                if datetime.datetime.strptime(record_parts[2], '%Y-%m-%dT%H:%M:%SZ') < datetime.datetime.utcnow() :
                    if len(record_parts) >= 7 :
                        self.tw.cancel_transfer(record_parts[6])

                    file = open(self.record_file, 'w+')
                    file.write('')
                    file.close()

    def create_quote(self, amount=0) :
        # get historical quotes
        if os.path.isfile(self.record_file) :
            file = open(self.record_file, 'r')
            records = file.readlines()
            file.close()
        else :
            records = []
        # compare quotes
        quote = self.tw.get_quote(self.profile, amount)

        now = datetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
        amount = 0
        for option in quote['paymentOptions'] :
            if option['payIn'] == 'BANK_TRANSFER' and option['payOut'] == 'BANK_TRANSFER' :
                amount = option['targetAmount']

        write_record = True
        if len(records) > 0 :
            max_rate = 0.0
            max_date = ''
            for record in records :
                record = record.replace('\n' , '')
                record_parts = record.split(',')
                if len(record_parts) > 6 and float(record_parts[3]) > float(max_rate) :
                    max_rate = record_parts[3]
                    max_date = record_parts[2]

            if float(max_rate) > float(quote['rate']) :
                write_record = False
            elif float(max_rate) == float(quote['rate']) and max_date == quote['rateExpirationTime'] :
                write_record = False

        new_record = []
        if write_record == True :
            transfer = self.tw.create_transfer(quote['id'], self.target_account)
            new_record = [now, quote['rateTimestamp'], quote['rateExpirationTime'], quote['rate'], amount, quote['id'], transfer['id']]

        if len(new_record) > 0 :
            if len(records) > 0 :
                for record in records :
                    record = record.replace('\n' , '')
                    record_parts = record.split(',')
                    if len(record_parts) >= 7 :
                        self.tw.cancel_transfer(record_parts[6])

                file = open(self.record_file, 'w+')
                file.write('')
                file.close()

            file = open(self.record_file, 'a')
            file.write(','.join(map(str, new_record)) + '\n')
            file.close()

        if write_record == True :
            return new_record

        return False

if __name__ == '__main__' :
    transferwise = transferwise()
    transferwise.create_quote(500000)
    # transferwise.get_quotes()
