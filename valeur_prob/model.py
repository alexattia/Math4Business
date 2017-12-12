import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class model:
    def __init__(self):
        self.df = pd.read_csv("variables.csv", index_col = 0)

    def compute_sumproduct(self, weights):
        s = 0
        self.data = self.df.copy()
        for key in weights.keys():
            self.data[key] = self.df[key]*weights[key]
            s += weights[key]
        self.data = self.data.sum(1)/s

    def save_df(self):
        self.data.to_csv(BASE_DIR + "/valeur_probatoire.csv")



def main():
    weights = {
                'Social' : 1.,
                'Transaction' : 2.,
                'Economy' : 1.,
                'Market Cap' : 4.,
                #'First Block' : 1.,
                'Activity Network' : 1.
              }

    d = model()
    d.compute_sumproduct(weights)
    d.save_df()
