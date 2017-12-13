import parserM4
import pandas as pd
import numpy as np
import imp
import pathlib
columns = ['Height', 'Transactions', 'AvgFee/Tx', 'RewardFee', 'WaitingTime', 'Time']

class Model():
    """
    Model object with the different blockchains, the general infos and the model
    :attr model: Pandas dataframe with the scores and values for each blockchaine
    """
    def __init__(self, dumps=True, W=None):
        self.blockchains = {}
        self.gen_infos = parserM4.parse_bitinfocharts()
        if not W:
            self.W = [0.5, 1, 3]
        else:
            self.W = W
        if not dumps:
            self.load_blockchains()
        else:
            self.load_dumps()
        self.create_model()

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
                self.blockchains[crypt] = pd.read_csv(file) 

    def create_model(self, perc=0.95):
        self.model = pd.DataFrame()
        for chain, df_chain in self.blockchains.items():
            df_chain[columns[4]] = pd.to_datetime(df_chain[columns[5]]).diff(periods=-1).apply(lambda x:x.total_seconds())
            if chain != 'DOGE':
                self.model.at['Currency_Market', chain] = self.gen_infos.loc[1][chain]
                self.model.at['Price_USD', chain] = self.gen_infos.loc[2][chain]
                self.model.at['Market_Capitalization', chain] = self.gen_infos.loc[3][chain]
            for col in columns[1:5]:
                self.model.at[col+'_Mean', chain] = df_chain[col].mean()
                self.model.at[col+'_Std', chain] = df_chain[col].std()
                self.model.at[col+'_Percentile%i' % (perc*100), chain] = df_chain[col].quantile(perc)
            rows = self.model.index
            self.model.loc['Liquidity_'] = (np.power(self.model.loc[rows[2]], 0.1)*self.model.loc[rows[3]]*1E-6)/self.model.loc[rows[12]]
            self.model.loc['Cost_'] = np.abs(1 - self.model.loc[rows[8]]/self.model.loc[rows[6]])*self.model.loc[rows[1]]*(self.model.loc[rows[6]]+0.4*self.model.loc[rows[7]])
            self.model.loc['Processing time_'] = (self.model.loc[rows[13]]/(self.model.loc[rows[12]]*self.model.loc[rows[14]]))**3
            # self.model.loc['Processing time_'] = self.model.loc['Processing time_'].apply(lambda x:np.log(x))

            for feature in ['Liquidity', 'Processing time']:
                self.model.loc[feature] = self.model.loc[feature+'_']/self.model.loc[feature+'_'].max()
            self.model.loc['Cost'] = 1-(self.model.loc['Cost_']/self.model.loc['Cost_'].sum())

            self.model.loc['Score'] = (self.W[0]*self.model.loc['Liquidity'] +
                                       self.W[1]*self.model.loc['Cost'] + 
                                       self.W[2]*self.model.loc['Processing time'])/np.sum(self.W)




