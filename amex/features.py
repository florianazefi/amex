import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gc,os,random
import time,datetime
from tqdm import tqdm
from multiprocessing import Pool as ThreadPool
from amex.utils import get_settings, get_root_dir
settings = get_settings()

def one_hot_encoding(df,cols,is_drop=True):
    for col in cols:
        print('one hot encoding:',col)
        dummies = pd.get_dummies(pd.Series(df[col]),prefix='oneHot_%s'%col)
        df = pd.concat([df,dummies],axis=1)
    if is_drop:
        df.drop(cols,axis=1,inplace=True)
    return df

def cat_feature(df):
    one_hot_features = [col for col in df.columns if 'oneHot' in col]
    if lastk is None:
        num_agg_df = df.groupby("customer_ID",sort=False)[one_hot_features].agg(['mean', 'std', 'sum', 'last'])
    else:
        num_agg_df = df.groupby("customer_ID",sort=False)[one_hot_features].agg(['mean', 'std', 'sum'])
    num_agg_df.columns = ['_'.join(x) for x in num_agg_df.columns]

    if lastk is None:
        cat_agg_df = df.groupby("customer_ID",sort=False)[cat_features].agg(['last', 'nunique'])
    else:
        cat_agg_df = df.groupby("customer_ID",sort=False)[cat_features].agg(['nunique'])
    cat_agg_df.columns = ['_'.join(x) for x in cat_agg_df.columns]

    count_agg_df = df.groupby("customer_ID",sort=False)[['S_2']].agg(['count'])
    count_agg_df.columns = ['_'.join(x) for x in count_agg_df.columns]
    df = pd.concat([num_agg_df, cat_agg_df,count_agg_df], axis=1).reset_index()
    print('cat feature shape after engineering', df.shape )

    return df

def num_feature(df):
    if num_features[0][:5] == 'rank_':
        num_agg_df = df.groupby("customer_ID",sort=False)[num_features].agg(['last'])
    else:
        if lastk is None:
            num_agg_df = df.groupby("customer_ID",sort=False)[num_features].agg(['mean', 'std', 'min', 'max', 'sum', 'last'])
        else:
            num_agg_df = df.groupby("customer_ID",sort=False)[num_features].agg(['mean', 'std', 'min', 'max', 'sum'])
    num_agg_df.columns = ['_'.join(x) for x in num_agg_df.columns]
    if num_features[0][:5] != 'rank_':
        for col in num_agg_df.columns:
            num_agg_df[col] = num_agg_df[col] // 0.01
    df = num_agg_df.reset_index()
    print('num feature shape after engineering', df.shape )

    return df

def diff_feature(df):
    diff_num_features = [f'diff_{col}' for col in num_features]
    cids = df['customer_ID'].values
    df = df.groupby('customer_ID')[num_features].diff().add_prefix('diff_')
    df.insert(0,'customer_ID',cids)
    if lastk is None:
        num_agg_df = df.groupby("customer_ID",sort=False)[diff_num_features].agg(['mean', 'std', 'min', 'max', 'sum', 'last'])
    else:
        num_agg_df = df.groupby("customer_ID",sort=False)[diff_num_features].agg(['mean', 'std', 'min', 'max', 'sum'])
    num_agg_df.columns = ['_'.join(x) for x in num_agg_df.columns]
    for col in num_agg_df.columns:
        num_agg_df[col] = num_agg_df[col] // 0.01

    df = num_agg_df.reset_index()
    print('diff feature shape after engineering', df.shape )

    return df


