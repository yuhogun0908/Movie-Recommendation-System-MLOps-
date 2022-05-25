#-*- coding: utf-8 -*-

import numpy as np
import sys
#sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone2/exercise/")
from path.path import get_project_root
from RecSys_Management.datasets import RecDataset
from RecSys_Management.model_training import train, do_prediction, get_metric, get_model
import argparse, random, json, time, os
import os.path as osp
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--CSR_dir_path", type=str, default="DB/CORPUS",
                        help="corpus path to be used in training")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model_name", type=str, default="svd", help="svd, svdpp")
    parser.add_argument("--n_epochs", type=int, default=20)
    parser.add_argument("--n_factors", type=int, default=50, help="# of latent features")
    parser.add_argument("--model_save_path", type=str, default="RecSys_Management/model/save")

    # Parse the arguments.
    args = parser.parse_args()
    # Set seeds
    random.seed(args.seed)

    return args

def main():
    args = parse_args()
    dataset = RecDataset(args)
    df_data, sp_data = dataset.build_train_valid_dataset()

    # TRAIN
    dir_path = osp.join(get_project_root(), args.model_save_path)

    model_name = args.model_name.lower()
    if model_name == "svd" or model_name == "svdpp":
        pass
    else:
        assert "Error: model_name should be either 'svd' or 'svdpp'"

    dir_path = osp.join(dir_path, model_name)   # Project_Root/Rec_Sys/model/save/svd/
    date_string = datetime.now().strftime('%Y%m%d_%H%M')
    save_dir_path = osp.join(dir_path, date_string)
    if not os.path.exists(save_dir_path):
        os.makedirs(name=save_dir_path, exist_ok=True)

    trained_model = train(args, df_data, sp_data, save_dir_path)

    # Do validation loss check
    res = do_prediction(test_data=df_data.valid, model=trained_model)
    print("\n######     VALIDATION Metric   #######")
    metrics = get_metric(result_list=res)
    cur_rmse = metrics["RMSE"]

    print("\n>>  Training is completed... ")
    print("  >> Check the model: {}".format(save_dir_path))

    latest_file_path = osp.join(dir_path, "latest_info.json")
    info = {"latest_path": date_string,
            "valid_rmse": cur_rmse}
    with open(latest_file_path, "w") as f:
        json.dump(info, f)

    print("  >> latest_path has been changed...")

    return

if __name__ == "__main__":
    main()
