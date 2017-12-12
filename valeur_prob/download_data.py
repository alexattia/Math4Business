import pandas as pd
from datetime import datetime
import requests
import json
from reddit_bch_followers import reddit_bch
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def bitinfocharts():
    """
    Download Data from Bitinfo_charts
    Output : html page
    """
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    q = requests.get('https://bitinfocharts.com/index_c.html', headers=hdr)

    the_page = q.text
    return the_page

# Get HTML page
def preprocess_html(html_page):
    """
    Input : html file
    Preprocess the data from the html
    Output : dataframe
    """
    # Put HTML inside Pandas Dataframe
    df = pd.read_html(html_page, header=0, index_col=0)[0]

    # Remove Nans and select good columns
    df = df.transpose().fillna('0')
    df = df[['Price',
    'Market Capitalization',
    'Transactions last 24h',
    'Sent last 24h',
    'Blocks last 24h',
    'Reward last 24h',
    'Active Addresses last 24h',
    'First Block',
    'Reddit subscribers',
    'Tweets per day',
    'Github stars']]
    
    df["Price"] = df["Price"].map(lambda x: float(x.split("$ ")[1].split(" USD")[0].replace(",", "")))
    df["Market Capitalization"] = df["Market Capitalization"].map(lambda x: float(x.split("$")[1].split(" USD")[0].replace(",", "")))
    df["Transactions last 24h"] = df["Transactions last 24h"].astype(float)
    df["Sent last 24h"] = df["Sent last 24h"].map(lambda x:float(x.split( )[0].replace(",","")))
    df["Blocks last 24h"] = df["Blocks last 24h"].astype(float)
    df["Reward last 24h"] = df["Reward last 24h"].map(lambda x:float(x.split('$')[1].split(" USD")[0].replace(",", "")))
    df["Active Addresses last 24h"] = df["Active Addresses last 24h"].astype(float)
    df["First Block"] = df["First Block"].map(lambda x : datetime.strptime(x, "%Y-%m-%d"))
    df["Reddit subscribers"] = df["Reddit subscribers"].astype(float)
    df["Tweets per day"] = df["Tweets per day"].astype(float)
    df["Github stars"] = df["Github stars"].astype(float)
    df.index = df.index.map(lambda x: x.split("(explorer")[0])
    return df

def hand_correction(df):

    # TODO: other file
    d = df.copy()
    d["First Block"].loc["Bitcoin Cash"] = datetime(2017,8,1)
    d["First Block"].loc["Bitcoin Gold"] = datetime(2017,10,25)
    d["Reddit subscribers"].loc["Bitcoin Cash"] = reddit_bch()
    return d

def main():
    html_page = bitinfocharts()
    df = preprocess_html(html_page)
    df = hand_correction(df)
    df.to_csv(BASE_DIR + "/crypto_data.csv")

