#-*- coding: utf-8 -*-
# Created by Yoonseok heo at 200329
import json, os
import pandas as pd
import numpy as np
import os.path as osp
from path.path import get_project_root
from surprise import Dataset, Reader


class DF_DATA(object):
    def __init__(self, train, valid, test=None):
        self.train = train
        self.valid = valid
        self.test = test


class SURPRISE_DATA(object):
    """ ONLY for "fit" method during training"""

    def __init__(self, train, valid, test=None):
        self.train = train
        self.valid = valid
        self.test = test


class RecDataset:
    def __init__(self, args, do_test=False, unit_test=False):
        self.args = args
        self.do_test = do_test
        if not unit_test:
            dir_path = osp.join(get_project_root(), args.CSR_dir_path)

            if not osp.isdir(dir_path):
                assert NotADirectoryError

            with open(osp.join(dir_path, "latest_info.json"), "r") as f:
                data_dir = (json.load(f))["latest_path"]

            self.dir_path = osp.join(osp.join(dir_path, data_dir), "data_split")

    def build_test_dataset(self):
        print("  >> Load test dataset...")
        self.test_csr = self.set_load_data("test_idx.json")

        df_test = pd.DataFrame(self.test_csr)
        df_test = df_test.astype({0: "int", 1: "int", 2: "float"})
        df_test = df_test.astype({0: str, 1: str})
        df_test.columns = ["userID", "movieID", "rating"]

        reader = Reader(rating_scale=(1.0, 5.0))
        test_data = Dataset.load_from_df(df_test[["userID", "movieID", "rating"]], reader)
        df_data = DF_DATA(None, None, df_test)
        sp_data = SURPRISE_DATA(None, None, test_data)

        self.print_statistics(df_data=df_test, data_name="test")

        return df_data, sp_data

    def build_train_valid_dataset(self):
        print("  >> Load train and validation dataset...")
        self.train_csr = self.set_load_data("train_idx.json")
        self.valid_csr = self.set_load_data("valid_idx.json")
        df_train = pd.DataFrame(self.train_csr)
        df_valid = pd.DataFrame(self.valid_csr)

        df_train = df_train.astype({0: "int", 1: "int", 2: "float"})
        df_train = df_train.astype({0: str, 1: str})

        df_valid = df_valid.astype({0: "int", 1: "int", 2: "float"})
        df_valid = df_valid.astype({0: str, 1: str})

        df_train.columns = ["userID", "movieID", "rating"]
        df_valid.columns = ["userID", "movieID", "rating"]

        reader = Reader(rating_scale=(1.0, 5.0))
        train_data = Dataset.load_from_df(df_train[["userID", "movieID", "rating"]], reader=reader)
        valid_data = Dataset.load_from_df(df_valid[["userID", "movieID", "rating"]], reader)

        train_data = train_data.build_full_trainset()

        df_data = DF_DATA(df_train, df_valid)
        sp_data = SURPRISE_DATA(train_data, valid_data)

        self.print_statistics(df_data=df_train, data_name="train")
        self.print_statistics(df_data=df_valid, data_name="valid")

        return df_data, sp_data

    def set_load_data(self, data_path):
        data_path = osp.join(self.dir_path, data_path)
        print("  >> Load data from {}".format(data_path))
        with open(data_path, "r") as f:
            return np.array(json.load(f))

    def print_statistics(self, df_data, data_name):
        print("")
        print("  >> # of {} datasets: {}".format(data_name.lower(), df_data.shape[0]))
        print("  >> shape of {} datasets: [ {}, {} ]".format(
            data_name.lower(), df_data.shape[0], df_data.shape[1]))
        print("")

        return

def data_loader(args):

    dir_path = osp.join(get_project_root(), args.CSR_dir_path)

    if not osp.isdir(dir_path):
        assert NotADirectoryError

    with open(osp.join(dir_path, "latest_info.json"), "r") as f:
        data_dir = (json.load(f))["latest_path"]
    dir_path = osp.join(osp.join(dir_path, data_dir), "data_split")
    train_path = os.path.join(dir_path, "train_idx.json")
    valid_path = os.path.join(dir_path, "valid_idx.json")
    test_path = os.path.join(dir_path, "test_idx.json")

    with open(train_path, "r") as f:
        train_csr = np.array(json.load(f))
    with open(valid_path, "r") as f:
        valid_csr = np.array(json.load(f))
    """
    with open(test_path, "r") as f:
        test_csr = np.array(json.load(f))
    """

    df_train = pd.DataFrame(train_csr)
    df_valid = pd.DataFrame(valid_csr)
    #df_test = pd.DataFrame(test_csr)

    df_train = df_train.astype({0: "int", 1: "int", 2: "float"})
    df_train = df_train.astype({0: str, 1: str})
    #print(df_train.dtypes)

    df_valid = df_valid.astype({0: "int", 1: "int", 2: "float"})
    df_valid = df_valid.astype({0: str, 1: str})
    #print(df_valid.dtypes)

    #df_test = df_test.astype({0: "int", 1: "int", 2: "float"})
    #df_test = df_test.astype({0: str, 1: str})

    df_train.columns = ["userID", "movieID", "rating"]
    df_valid.columns = ["userID", "movieID", "rating"]
    #df_test.columns = ["userID", "movieID", "rating"]

    reader = Reader(rating_scale=(1.0, 5.0))
    train_data = Dataset.load_from_df(df_train[["userID", "movieID", "rating"]], reader=reader)
    valid_data = Dataset.load_from_df(df_valid[["userID", "movieID", "rating"]], reader)
    #test_data = Dataset.load_from_df(df_test[["userID", "movieID", "rating"]], reader)

    train_data = train_data.build_full_trainset()

    #df_data = DF_DATA(df_train, df_valid, df_test)
    df_data = DF_DATA(df_train, df_valid)
    #sp_data = SURPRISE_DATA(train_data, valid_data, test_data)
    sp_data = SURPRISE_DATA(train_data,valid_data)

    return df_data, sp_data