import numpy as np
import pandas as pd
import sys
#sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone2/exercise/")
from path.path import get_project_root
from RecSys_Management.datasets import RecDataset
from RecSys_Management.model_training import train, do_prediction, get_metric
import argparse, random, json, time, os
import os.path as osp
from datetime import datetime
import unittest



parser = argparse.ArgumentParser()
parser.add_argument("--CSR_dir_path", type=str, default="DB/CORPUS",
                    help="corpus path to be used in training")
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--model_name", type=str, default="svd", help="svd, svdpp")
parser.add_argument("--n_epochs", type=int, default=20)
parser.add_argument("--n_factors", type=int, default=50, help="# of latent features")
parser.add_argument("--model_save_path", type=str, default="RecSys_Management/model/save")
parser.add_argument("--dataset_dir_path", required=True)
parser.add_argument('unittest_args', nargs='*')

args = parser.parse_args()
dataset_dir_path = args.dataset_dir_path

class ModelTraining(unittest.TestCase):
    def __init__(self, args):
        super(ModelTraining, self).__init__(args)
        # set input variable, raw_data_path and output_path, for unit test
        self.dataset = RecDataset(args=args, unit_test=True)
        self.dataset.dir_path = dataset_dir_path
    def test_path(self):
        # test if all path is valid
        self.assertTrue(os.path.isdir(self.dataset.dir_path))

    def test_RecDataset(self):
        # Since model training and validation process is based on other library,
        # we only test whether the input data is valid.
        # get output of function
        train_csr = self.dataset.set_load_data("train_idx.json")
        # test if the output returns array
        self.assertIsInstance(train_csr, np.ndarray)

        # get output of function
        df_data, sp_data = self.dataset.build_train_valid_dataset()
        # test if the output returns dataframe with correct column names
        self.assertIsInstance(df_data.train, pd.DataFrame)
        self.assertListEqual(df_data.train.columns.to_list(), ["userID", "movieID", "rating"])
        self.assertIsInstance(df_data.valid, pd.DataFrame)
        self.assertListEqual(df_data.valid.columns.to_list(), ["userID", "movieID", "rating"])

        # get output of function
        df_data, sp_data = self.dataset.build_test_dataset()
        # test if the output returns dataframe with correct column names
        self.assertIsInstance(df_data.test, pd.DataFrame)
        self.assertListEqual(df_data.test.columns.to_list(), ["userID", "movieID", "rating"])

if __name__ == '__main__':
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--CSR_dir_path", type=str, default="DB/CORPUS",
                        help="corpus path to be used in training")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model_name", type=str, default="svd", help="svd, svdpp")
    parser.add_argument("--n_epochs", type=int, default=20)
    parser.add_argument("--n_factors", type=int, default=50, help="# of latent features")
    parser.add_argument("--model_save_path", type=str, default="RecSys_Management/model/save")
    parser.add_argument("--dataset_dir_path", required=True)
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    from pprint import pprint
    pprint(vars(args))
    """
    sys.argv[1:] = args.unittest_args
    unittest.main()
