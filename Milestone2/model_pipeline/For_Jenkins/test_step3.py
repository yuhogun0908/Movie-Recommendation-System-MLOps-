import numpy as np
<<<<<<< HEAD
import pandas as pd
import sys
#sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone2/exercise/")
from path.path import get_project_root
from RecSys_Management.datasets import RecDataset
from RecSys_Management.model_training import train, do_prediction, get_metric
=======
import sys
sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone2/exercise/")
from path.path import get_project_root
from RecSys_Management.datasets import RecDataset
from RecSys_Management.model_training import train, do_prediction, get_metric, get_model
>>>>>>> origin/yoonseoh
import argparse, random, json, time, os
import os.path as osp
from datetime import datetime
import unittest

<<<<<<< HEAD
class ModelTraining(unittest.TestCase):
    def __init__(self, args):
        super(ModelTraining, self).__init__(args)
        # set input variable, raw_data_path and output_path, for unit test
        self.dataset = RecDataset(args=args, unit_test=True)
        self.dataset.dir_path = "/home/team24/milestone2/group-project-s22-k-avengers/Milestone2/model_pipeline/DB/CORPUS/unittest/data_split"
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
=======
class FetchDataset(unittest.TestCase):
    def test_main(self):
        dataset = RecDataset(args)
        df_data, sp_data = dataset.build_train_valid_dataset() # -> 체크

        # TRAIN
        date_string = datetime.now().strftime('%Y%m%d_%H%M')
        dir_path = osp.join(get_project_root(), args.model_save_path)
        save_dir_path = osp.join(dir_path, date_string)
        if not os.path.exists(save_dir_path):
            os.makedirs(name=save_dir_path, exist_ok=True)

#        trained_model = train(args, df_data, sp_data, save_dir_path)

        print("  >> Check the model: {}".format(save_dir_path))

        if args.set_record is True:
            latest_file_path = osp.join(dir_path, "latest_info.json")
            info = {"latest_path": date_string,
                    "valid_rmse": 0.133}
            with open(latest_file_path, "w") as f:
                json.dump(info, f)
>>>>>>> origin/yoonseoh

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--CSR_dir_path", type=str, default="DB/CORPUS",
                        help="corpus path to be used in training")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model_name", type=str, default="svd", help="svd, svdpp")
    parser.add_argument("--n_epochs", type=int, default=20)
    parser.add_argument("--n_factors", type=int, default=50, help="# of latent features")
    parser.add_argument("--model_save_path", type=str, default="RecSys_Management/model/save")
<<<<<<< HEAD
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    sys.argv[1:] = args.unittest_args
    unittest.main()
=======

    parser.add_argument("--set_record", action="store_const", default=False, const=True)

    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()
    sys.argv[1:] = args.unittest_args

    # Set seeds
    random.seed(args.seed)

    unittest.main()
>>>>>>> origin/yoonseoh
