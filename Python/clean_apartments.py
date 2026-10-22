import pandas as pd
import numpy as np
import os

def load_raw():
    lista = []
    for i in os.listdir('../data/raw'):
        if 'apartments_pl_' in i:
            lista.append(i)
    return lista

def read_raw(lista):
    dfs = []
    for x in lista:
        index1 =  x.index('2')
        index2 = x.index('.')
        month = x[index1 : index2]
        arq = pd.read_csv('../data/raw/'+x)
        arq['month'] = month
        dfs.append(arq)
    return pd.concat(dfs)

def clean(df):
    df = df.drop(columns='condition')
    df = df.sort_values(by='month')
    df = df.drop_duplicates(subset='id',keep='last')
    return df

def convert_int64(df):
    df['rooms']  = df['rooms'].astype('Int64')
    df['floor'] = df['floor'].astype('Int64')
    df['price_per_m2'] = round(df['price'] /df['squareMeters'],2)
    df['floorCount'] = df['floorCount'].astype('Int64')
    df['buildYear'] = df['buildYear'].astype('Int64')
    return df

def flag_outliers(df):
    df['city_median_m2']  = df.groupby(df['city'])['price_per_m2'].transform('median')
    df['ratio'] = df['price_per_m2'] / df['city_median_m2']
    return df

def is_outlier(df):
    df['is_outlier'] = np.where((df['ratio'] > 2.0) | (df['ratio'] < 0.5), True, False)
    return df

def save(df):
    df.to_csv('../data/clean/apartments_clean.csv', index=False)

run1 = load_raw()
run2 = read_raw(run1)
run3 = clean(run2)
run4 = convert_int64(run3)
run5 = flag_outliers(run4)
run6 = is_outlier(run5)
run7 = save(run6)
