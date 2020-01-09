# from . import transferwise_api
import transferwise_api
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

class main :
    def __init__(self) :
        self.headers = {
                        'Accept':          '*/*',
                        'Accept-Encoding': 'gzip, deflate',
                        'Content-Type':    'application/json',
                        'Authorization':   'Bearer ec50cd47-25bc-4db6-9ad0-ebc215631d5c',
                        # 'Authorization':   'Bearer 899f9cb6-8827-4f66-aeca-3b03de013277'
                        }
        self.record_file = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'records.txt')
        self.tw = transferwise_api.transferwise()

    #
    # def get_quotes(self) :
    #     # get historical quotes
    #     file = open(self.record_file, 'r')
    #     records = file.readlines()
    #     file.close()
    #
    #     if len(records) > 0 :
    #         max_rate = 0
    #         max_record = ''
    #         current_records = []
    #         for record in records :
    #             record = record.replace('\n' , '')
    #             record_parts = record.split(',')
    #             if float(record_parts[3]) > float(max_rate) :
    #                 max_rate = record_parts[3]
    #                 max_record = record_parts[5]
    #             if len(record_parts) == 7 :
    #                 current_records.append(record_parts[5])
    #
    #         open_transaction = False
    #         # do nothing if the opened transfer is the highest rate offered
    #         if len(current_records) and max_record in current_records :
    #             if len(current_records) > 1 :
    #                 for current_record in current_records :
    #                     update_records = []
    #                     for record in records :
    #                         record = record.replace('\n' , '')
    #                         record_parts = record.split(',')
    #                         if record_parts[5] == current_record :
    #                             self.tw.cancel_transfer(record_parts[6])
    #                             update_records.append(','.join(record_parts[0:6]))
    #                         else :
    #                             update_records.append(record)
    #
    #                     file = open(self.record_file, 'w+')
    #                     file.write('\n'.join(update_records) + '\n')
    #                     file.close()
    #         # close current opened transfer if new highest rate is obtained
    #         elif len(current_records) and max_record not in current_records :
    #             for current_record in current_records :
    #                 update_records = []
    #                 for record in records :
    #                     record = record.replace('\n' , '')
    #                     record_parts = record.split(',')
    #                     if record_parts[5] == current_record :
    #                         self.tw.cancel_transfer(record_parts[6])
    #                         update_records.append(','.join(record_parts[0:6]))
    #                     else :
    #                         update_records.append(record)
    #
    #                 file = open(self.record_file, 'w+')
    #                 file.write('\n'.join(update_records) + '\n')
    #                 file.close()
    #
    #             open_transaction = True
    #         elif len(current_records) == 0 :
    #             open_transaction = True
    #         # exit()
    #         file = open(self.record_file, 'r')
    #         records = file.readlines()
    #         file.close()
    #         if open_transaction == True and float(max_rate) > 0 :
    #             update_records = []
    #             for record in records :
    #                 record = record.replace('\n' , '')
    #                 record_parts = record.split(',')
    #                 if record_parts[5] == max_record :
    #                     transfer = self.tw.create_transfer(max_record)
    #                     update_records.append(record + ',' + str(transfer['id']))
    #                 else :
    #                     update_records.append(record)
    #
    #             file = open(self.record_file, 'w+')
    #             file.write('\n'.join(update_records) + '\n')
    #             file.close()
    #
    #             return {'Date': max_record[0], 'Rate Sent (UTC)': max_record[1], 'Rate Expire (UTC)': max_record[2], 'Rate': max_record[3], 'Amount': max_record[4], 'TW ID': max_record[5]}
    #
    #     return False

    def clear_quotes(self) :
        # clear historical quotes
        file = open(self.record_file, 'r')
        records = file.readlines()
        file.close()

        if len(records) > 0 :
            for record in records :
                record = record.replace('\n' , '')
                record_parts = record.split(',')
                if datetime.datetime.strptime(record_parts[2], '%Y-%m-%dT%H:%M:%SZ') > datetime.datetime.utcnow() :
                    if len(record_parts) >= 7 :
                        self.tw.cancel_transfer(record_parts[6])

                    file = open(self.record_file, 'w+')
                    file.write('')
                    file.close()


            file = open(self.record_file, 'w+')
            file.write('')
            file.close()

    def create_quote(self, amount=0) :
        # get historical quotes
        file = open(self.record_file, 'r')
        records = file.readlines()
        file.close()
        # compare quotes
        quote = self.tw.get_quote('xxxxxxx', amount)

        now = datetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
        amount = 0
        for option in quote['paymentOptions'] :
            if option['payIn'] == 'BANK_TRANSFER' and option['payOut'] == 'BANK_TRANSFER' :
                amount = option['targetAmount']

        write_record = True
        if len(records) > 0 :
            for record in records :
                record = record.replace('\n' , '')
                record_parts = record.split(',')
                if float(record_parts[3]) > float(quote['rate']) :
                    write_record = False
                    break

        new_record = []
        if write_record == True :
            transfer = self.tw.create_transfer(quote['id'], 'xxxxxxx')
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
    main = main()
    main.create_quote(500000)
    # main.get_quotes()
