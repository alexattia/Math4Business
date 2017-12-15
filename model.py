import parserM4
import pandas as pd
import numpy as np
import pathlib
from datetime import datetime, timedelta

columns = ['Height', 'Transactions', 'AvgFee/Tx', 'RewardFee', 'WaitingTime', 'Time']


class Model():
    """
    Model object with the different blockchains, the general infos and the model
    :attr model: Pandas dataframe with the scores and values for each blockchaine
    """

    def __init__(self, days_list=[1,2,5,10], dumps=True, W=[0.5, 1, 3]):
        self.blockchains = {}
        self.gen_infos = parserM4.parse_bitinfocharts()
        self.W = W
        if not dumps:
            self.load_blockchains()
        else:
            self.load_dumps()
        self.models = {d:self.create_model(d) for d in days_list}

    def load_blockchains(self, n_block=5):
        self.blockchains['BTC'] = parserM4.parse_btc(1)
        self.blockchains['BTC']['datetime'] = pd.to_datetime(self.blockchains['BTC']['Time'],
                                                             format='%Y-%m-%d %H:%M:%S')
        self.blockchains['ETH'] = parserM4.parse_ether(30)
        print('%s & %s blockchains parsed!' % ('BTC', 'ETH'))
        for chain in ['LTC', 'DASH', 'DOGE']:
            self.blockchains[chain] = parserM4.parse_blockcypher(chain.lower(), n_block=n_block)
            print('%s blockchain parsed!' % chain)

    def load_dumps(self):
        for crypt in ['BTC', 'ETH', 'LTC', 'DASH', 'DOGE']:
            file = 'dump_%s.csv' % crypt.lower()
            p = pathlib.Path(file)
            if p.is_file():
                self.blockchains[crypt] = pd.read_csv(file, index_col=0)

    def create_model(self, ndays, perc=0.95):
        model = pd.DataFrame()
        for chain, df_chain in self.blockchains.items():
            df_chain[columns[5]] = pd.to_datetime(df_chain[columns[5]])
            df_chain = df_chain[df_chain[columns[5]] > df_chain[columns[5]].max()-timedelta(ndays)]
            df_chain[columns[4]] = df_chain[columns[5]].diff(periods=-1).apply(lambda x: x.total_seconds())
            model.at['Days', chain] = int(ndays)
            model.at['Number_Blocks', chain] = len(df_chain)
            model.at['Currency_Market', chain] = self.gen_infos.loc[1][chain]
            model.at['Price_USD', chain] = self.gen_infos.loc[2][chain]
            model.at['Market_Capitalization', chain] = self.gen_infos.loc[3][chain]
            for col in columns[1:5]:
                model.at[col + '_Mean', chain] = df_chain[col].mean()
                model.at[col + '_Std', chain] = df_chain[col].std()
                model.at[col + '_Percentile%i' % (perc * 100), chain] = df_chain[col].quantile(perc)
            rows = model.index
           # FYI rows format :
           # ['Days', 'Number_Blocks', 'Currency_Market', 'Price_USD',
           # 'Market_Capitalization', 'Transactions_Mean', 'Transactions_Std',
           # 'Transactions_Percentile95', 'AvgFee/Tx_Mean', 'AvgFee/Tx_Std',
           # 'AvgFee/Tx_Percentile95', 'RewardFee_Mean', 'RewardFee_Std',
           # 'RewardFee_Percentile95', 'WaitingTime_Mean', 'WaitingTime_Std',
           # 'WaitingTime_Percentile95', 'Liquidity_', 'Cost_', 'Processing time_',
           # 'Liquidity', 'Processing time', 'Cost', 'Score']
        
            model.loc['Liquidity_'] = (np.power(model.loc[rows[4]], 0.1) * model.loc[rows[5]] * 1E-6) / \
                                           model.loc[rows[14]]
            model.loc['Cost_'] = np.abs(1 - model.loc[rows[10]] / model.loc[rows[8]]) * model.loc[
                rows[3]] * (model.loc[rows[8]] + 0.4 * model.loc[rows[9]])
            model.loc['Processing time_'] = (model.loc[rows[15]] / (
                    model.loc[rows[14]] * model.loc[rows[16]]))

            for feature in ['Liquidity', 'Processing time']:
                model.loc[feature] = model.loc[feature + '_'] / model.loc[feature + '_'].max()
            model.loc['Cost'] = 1 - (model.loc['Cost_'] / model.loc['Cost_'].sum())

            model = self.compute_score(model)
        model = model.sort_values(by='Score', ascending=False, axis=1)
        return model

    def compute_score(self, model):
        model.loc['Score'] = (self.W[0] * model.loc['Liquidity'] +
                               self.W[1] * model.loc['Cost'] +
                               self.W[2] * model.loc['Processing time']) / np.sum(self.W)
        return model

    def update_model(self):
        self.models = {d:self.create_model(d) for d in self.models.keys()}


