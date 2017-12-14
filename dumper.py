import parserM4
from datetime import datetime
import pathlib
import pandas as pd
import numpy as np
import time
abs_path = '/home/alexattia/Work/Math4Business/'

def dump_btc():
    file = abs_path + 'dump_btc.csv'
    p = pathlib.Path(file)
    if not p.is_file():
        new_dump = parserM4.parse_btc()
    else:
        previous_dump = pd.read_csv(file, index_col=0)
        last_time_dump = datetime.strptime(previous_dump.Time.max(), '%Y-%m-%d %H:%M:%S')
        temp_dump = parserM4.parse_btc(first_time=last_time_dump)
        new_dump = pd.concat([temp_dump, previous_dump])
        new_dump = new_dump.drop_duplicates(new_dump.columns[0])
    new_dump.to_csv(file)
    print('BTC done!')

def dump_eth():
    file = abs_path + 'dump_eth.csv'
    p = pathlib.Path(file)
    if not p.is_file():
        new_dump = parserM4.parse_ether(250)
    else:
        previous_dump = pd.read_csv(file, index_col=0)
        last_block_dump = int(previous_dump.Height.max())
        first_new_block = int(parserM4.parse_ether(25).Height.max())
        n_block = first_new_block - last_block_dump
        if n_block < 25:
            n_block = 25
        temp_dump = parserM4.parse_ether(n_block)
        new_dump = pd.concat([temp_dump, previous_dump])
        new_dump = new_dump.drop_duplicates(new_dump.columns[0])
    new_dump.to_csv(file)
    print('ETH (%s blocks) done!' % n_block)

def dump_crypto(crypto):
    """
    :param crypto: crypto symbol e.g LTC, DASH, DOGE
    """
    crypto = crypto.lower()
    file = abs_path + 'dump_%s.csv' % crypto
    p = pathlib.Path(file)
    if not p.is_file():
        new_dump = parserM4.parse_blockcypher(crypto)
    else:
        previous_dump = pd.read_csv(file, index_col=0)
        # Getting the last 200 blocks (it won't be continuous)
        first_new_block = parserM4.get_first_block(crypto)
        if first_new_block == -1:
            print('Too many requests')
            return -1
        n_block = 200 # first_new_block - last_block_dump
        temp_dump = parserM4.parse_blockcypher(crypto, 
                            first_block=first_new_block, n_block=n_block)
        new_dump = pd.concat([temp_dump, previous_dump])
        new_dump = new_dump.drop_duplicates(new_dump.columns[0])
    new_dump.to_csv(file)
    print('%s (%s blocks) done!' % (crypto.upper(), n_block))

if __name__ == '__main__':
    print('-- %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cryptos = ['LTC', 'DASH', 'DOGE']
    time.sleep(np.random.rand(1)[0])
    dump_btc()
    dump_eth()
    c = np.random.choice(cryptos)
    code = dump_crypto(c)
