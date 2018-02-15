import parserM4
import pandas as pd
import numpy as np
import pathlib
from datetime import datetime, timedelta

# name of the rows for the dumps
columns = ['Height', 'Transactions', 'AvgFee/Tx', 'RewardFee', 'WaitingTime', 'Time']


class Model():
    """
    Model object with the different blockchains, the general infos and the model
    :attr model: Pandas dataframe with the scores and values for each blockchaine
    """

    def __init__(self, days_list=[1,2,5,10], dumps=True, W=[0.5, 1, 3]):
        self.blockchains = {}
        # load general infos (market cap, price, etc)
        self.gen_infos = parserM4.parse_bitinfocharts()
        # weights for the liquidity, cost, time
        self.W = W
        # if no dump available, we crawl
        if not dumps:
            self.load_blockchains()
        else:
            self.load_dumps()
        # different models regarding the number of days we want to based our model on
        # self.model = {number_days:model based on number_days days}
        self.models = {d:self.create_model(d) for d in days_list}

    def load_blockchains(self, n_block=50):
        """
        Parse different websites for a few number of blocks each crypto
        self.blockchains = {crypto_name:pd.DataFrame}
        """
        self.blockchains['BTC'] = parserM4.parse_btc(1)
        self.blockchains['BTC']['datetime'] = pd.to_datetime(self.blockchains['BTC']['Time'],
                                                             format='%Y-%m-%d %H:%M:%S')
        self.blockchains['ETH'] = parserM4.parse_ether(200)
        print('%s & %s blockchains parsed!' % ('BTC', 'ETH'))
        for chain in ['LTC', 'DASH', 'DOGE']:
            self.blockchains[chain] = parserM4.parse_blockcypher(chain.lower(), n_block=n_block)
            print('%s blockchain parsed!' % chain)

    def load_dumps(self):
        """
        Load save dumped with many blocks for all crypto, 
        we directly edit the blockchains attributes
        self.blockchains = {crypto_name:pd.DataFrame}
        """
        for crypt in ['BTC', 'ETH', 'LTC', 'DASH', 'DOGE']:
            file = 'dump_%s.csv' % crypt.lower()
            p = pathlib.Path(file)
            if p.is_file():
                self.blockchains[crypt] = pd.read_csv(file, index_col=0)

    def create_model(self, ndays, perc=0.95):
        """
        Create a model for a fixed number of days and compute the score
        to compare the different crypto currencies
        :param n_days: number of days we based our model on
        :param perc: X-th percentile for the variation of a variable
        :return: pandas dataframe model
        """
        model = pd.DataFrame()
        for chain, df_chain in self.blockchains.items():
            # convert Time to the format datetime
            df_chain[columns[5]] = pd.to_datetime(df_chain[columns[5]])
            # Keep only the ndays first days
            df_chain = df_chain[df_chain[columns[5]] > df_chain[columns[5]].max()-timedelta(ndays)]
            # Compute the block waiting time from the exact time
            df_chain[columns[4]] = df_chain[columns[5]].diff(periods=-1).apply(lambda x: x.total_seconds())
            model.at['Days', chain] = int(ndays)
            # Number of blocks we are taking into account
            model.at['Number_Blocks', chain] = len(df_chain)
            model.at['Currency_Market', chain] = self.gen_infos.loc[1][chain]
            model.at['Price_USD', chain] = self.gen_infos.loc[2][chain]
            model.at['Market_Capitalization', chain] = self.gen_infos.loc[3][chain]
            # Compute Mean, STD, and perc-th percentile for 'Transactions', 'AvgFee/Tx', 'RewardFee', 'WaitingTime'
            for col in columns[1:5]:
                model.at[col + '_Mean', chain] = df_chain[col].mean()
                model.at[col + '_Std', chain] = df_chain[col].std()
                model.at[col + '_Percentile%i' % (perc * 100), chain] = df_chain[col].quantile(perc)
            rows = model.index

            # FYI rows format :
            # [(0, 'Days'), (1, 'Number_Blocks'), (2, 'Currency_Market'), (3, 'Price_USD'), (4, 'Market_Capitalization'), 
            # (5, 'Transactions_Mean'), (6, 'Transactions_Std'), (7, 'Transactions_Percentile95'), (8, 'AvgFee/Tx_Mean'), 
            # (9, 'AvgFee/Tx_Std'), (10, 'AvgFee/Tx_Percentile95'), (11, 'RewardFee_Mean'), (12, 'RewardFee_Std'), 
            # (13, 'RewardFee_Percentile95'), (14, 'WaitingTime_Mean'), (15, 'WaitingTime_Std'), (16, 'WaitingTime_Percentile95')]  
        
            # Compute the unnormalized Liquidity (manually crafter formula)
            # Depends on the Market Cap and number of transactions per hour
            model.loc['Liquidity_'] = (np.power(model.loc[rows[4]], 0.1) * model.loc[rows[5]] * 1E-6) / \
                                           model.loc[rows[14]]
            
            # Compute the unnormalized Cost (manually crafter formula)
            # Depends on the average fee per transaction and its variation
            model.loc['Cost_'] = np.abs(1 - model.loc[rows[10]] / model.loc[rows[8]]) * model.loc[
                rows[3]] * (model.loc[rows[8]] + 0.4 * model.loc[rows[9]])
            
            # Compute the unnormalized Processing Time (manually crafter formula)
            # Depends on the waiting time per block and its variation
            # TODO add MemPool : waiting time per transaction
            model.loc['Processing time_'] = (model.loc[rows[14]] / (
                     model.loc[rows[15]] * model.loc[rows[16]]))

            # Normalization of the variable
            # for feature in ['Liquidity', 'Processing time']:
            #     model.loc[feature] = model.loc[feature + '_'] / model.loc[feature + '_'].max()
            model.loc['Processing time'] = (model.loc['Processing time_'] / model.loc['Processing time_'].sum())    
            model.loc['Liquidity'] = (model.loc['Liquidity_'] / model.loc['Liquidity_'].sum())
            model.loc['Cost'] = 1 - (model.loc['Cost_'] / model.loc['Cost_'].sum())

            # Compute the final score
            model = self.compute_score(model)
        model = model.sort_values(by='Score', ascending=False, axis=1)
        return model

    def compute_score(self, model):
        """
        Compute the final score from normalized parameters (liquidity, cost,
        processing time) and regarding the weights W
        :param model: model from self.create_model()
        :return: pandas dataframe with a Score row at the bottom
        """
        model.loc['Score'] = (self.W[0] * model.loc['Liquidity'] +
                               self.W[1] * model.loc['Cost'] +
                               self.W[2] * model.loc['Processing time']) / np.sum(self.W)
        return model

    def update_model(self):
        """
        Method to update the model, for example if we want to edit the weights W
        :no return: directly update all the models
        """
        self.models = {d:self.create_model(d) for d in self.models.keys()}

    def volatility(self, chain):
        """
        Get the value grouped by day for a blockchain
        :param chain: blockchain to consider
        """
        df = self.blockchains[chain]
        df['Day'] = df['Time'].apply(lambda x:str(x).split(' ')[0])
        return df.groupby('Day')


