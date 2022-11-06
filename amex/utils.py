import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

import os
import yaml
import logging
from git import Repo

def denoise(df):
    df['D_63'] = df['D_63'].apply(lambda t: {'CR':0, 'XZ':1, 'XM':2, 'CO':3, 'CL':4, 'XL':5}[t]).astype(np.int8)
    df['D_64'] = df['D_64'].apply(lambda t: {np.nan:-1, 'O':0, '-1':1, 'R':2, 'U':3}[t]).astype(np.int8)
    for col in tqdm(df.columns):
        if col not in ['customer_ID','S_2','D_63','D_64']:
            df[col] = np.floor(df[col]*100)
    return df

def create_feather_files(settings):
    train_csv = settings['data'] + settings['train_csv']
    train_feather = settings['data'] + settings['train_feather']

    train = pd.read_csv(train_csv)
    train = denoise(train)
    train.to_feather(train_feather)

    del train

    test_csv = settings['data'] + settings['test_csv']
    test_feather = settings['data'] + settings['test_feather']

    test = pd.read_csv(test_csv)
    test = denoise(test)
    test.to_feather(test_feather)

def get_root_dir():
    """Return the root directory of the repository.

    Returns:
        string: Project root directory
    """
    repo = Repo(search_parent_directories=True)
    return repo.git_dir[:-5]


def get_settings(yaml_file="amex.yaml"):
    """Return the project configuration settings.

    Args:
        yaml_file (str): YAML filename

    Returns:
        settings (dict): Project settings
    """
    file_path = os.path.join(get_root_dir(), "conf", yaml_file)

    with open(file_path, "r") as config_file:
        return yaml.safe_load(config_file)



