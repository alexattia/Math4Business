import pandas as pd
import numpy as np
import preprocessing as prepro

import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class data_to_variables:
    def __init__(self, coinbase_param = 1.5):
        self.data = pd.read_csv('crypto_data.csv', index_col = 0)
        self.variables = self.data.columns.tolist()
        self.currencies = self.data.index.tolist()
        self.df = pd.DataFrame(index = self.currencies)
        self.coinbase_param = coinbase_param

    def social_data(self):
        Y = self.data['Reddit subscribers']
        Y = prepro.cap_floor(Y, cap = 10**5, floor = 0)
        Y = prepro.rescalling(Y)
        self.df['Social'] = Y

    def transaction(self):
        Y = self.data['Transactions last 24h'] - self.coinbase_param*self.data['Blocks last 24h']
        Y = prepro.cap_floor(Y, cap =10**5, floor = Y.min())
        Y = prepro.rescalling(Y)
        self.df['Transaction'] = Y

    def economy(self):
        Y = prepro.cap_floor(self.data['Reward last 24h'], cap =5*10**6, floor = self.data['Reward last 24h'].min())
        Y = prepro.rescalling(Y)
        self.df['Economy'] = Y

    def market_cap(self):
        X = self.data['Market Capitalization'].values
        Y = prepro.cap_floor(X, cap =10**9, floor = 0)
        Y = prepro.rescalling(Y)
        one  = (Y == 1).sum()
        a = (1-np.sqrt(-np.sort(-Y)[one]))/one
        index = np.argsort(-X)[0:one]
        Y[index] = 1 - np.arange(one)*a
        self.df['Market Cap'] = Y

    # def first_block(self):
    #     Y = self.data['First Block'].apply(prepro.date_difference)
    #     Y = prepro.cap_floor(Y, cap =(365*2), floor = Y.min())
    #     Y = prepro.rescalling(Y)
    #     self.df['First Block'] = Y

    # def activity_network(self):
    #     Y = self.data['Active Addresses last 24h']
    #     Y = prepro.cap_floor(Y, cap = 10**5, floor = Y.min())
    #     Y = prepro.rescalling(Y)
    #     self.df['Activity Network'] = Y


    def activity_network(self):
        Y = self.data['First Block'].apply(prepro.date_difference)
        Y = prepro.cap_floor(Y, cap =(365*2), floor = Y.min())
        Y2 = self.data['Active Addresses last 24h']
        Y2 = prepro.cap_floor(Y2, cap = 10**5, floor = Y2.min())
        Y = prepro.rescalling(Y*Y2)
        self.df['Activity Network'] = Y

    def get_df(self):
        self.social_data()
        self.transaction()
        self.economy()
        self.market_cap()
        #self.first_block()
        self.activity_network()

    def save_df(self):
        self.df.to_csv(BASE_DIR + "/variables.csv")


def main():
    d = data_to_variables()
    d.get_df()
    d.save_df()



