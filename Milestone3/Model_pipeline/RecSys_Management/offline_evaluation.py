#-*- coding: utf-8 -*-
# Created by YoonseokHeo at 220329
import argparse, random
from path.path import get_project_root
import os, json, argparse, random, time
import pandas as pd
import numpy as np
import os.path as osp
from datetime import datetime
import pickle
from surprise import SVD, Dataset, accuracy, Reader, SVDpp, dump
from tqdm import tqdm
from RecSys_Management.datasets import RecDataset

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--CSR_dir_path", type=str, default="DB/CORPUS",
                        help="corpus path to be used in training")

    parser.add_argument("--trained_model_dir_path", type=str,
                        default="RecSys_Management/model/save",
                        help="data path")
    # Parse the arguments
    args = parser.parse_args()


    return args

def main(args):
    save_dir_path = osp.join(get_project_root(), args.trained_model_dir_path)
    with open(osp.join(save_dir_path, "latest_info.json")) as f:
        dir_name = json.load(f)["latest_path"]

    trained_model_path = osp.join(save_dir_path, dir_name)
    # TODO: UNIT TEST
    if not osp.isdir(trained_model_path):
        assert NotADirectoryError


    # STEP1: Load Test Data
    dataset = RecDataset(args=args)
    df_data, sp_data = dataset.build_test_dataset()

    # STEP2: Load Model
    print("  >> Load a trained model from {}".format(trained_model_path))
    trained_model, args = load_model(trained_model_path, args)

    # STEP3: OFFLINE EVALUATION - RMSE, MSE, MAE
    res = do_prediction(test_data=df_data.test, model=trained_model)

    print("\n######     OFFLINE EVALUATION   #######")
    metrics = get_metric(result_list=res)
    cur_rmse = metrics["RMSE"]

    return


def load_model(trained_model_dir_path, args):
    _, loaded_model = dump.load(osp.join(trained_model_dir_path, "dump_file"))
    with open(osp.join(trained_model_dir_path, "args.bin"), "rb") as f:
        configs = pickle.load(f)

    # args update 하는 방법(URL: https://cs230.stanford.edu/blog/hyperparameters/)
    vars(args).update(vars(configs))

    return loaded_model, args


def do_prediction(test_data, model):
    num_rows = test_data.shape[0]
    infer_time = 0.0
    pred_list = []
    iter_wrapper = (lambda x: tqdm(x, total=num_rows))
    for i in iter_wrapper(range(num_rows)):
        sample = test_data.loc[i, :]
        uid = sample["userID"]
        movie_id = sample["movieID"]
        target_rate = sample["rating"]

        start_time = time.time()
        res = model.predict(uid, movie_id, target_rate)
        end_time = time.time()
        pred_list.append(res)
        infer_time += end_time - start_time
    print("Total inference time for {} samples: {:.3f}".format(infer_time, num_rows))

    return pred_list

def get_metric(result_list):
    res_dict = dict()
    res_dict["RMSE"] = accuracy.rmse(result_list)
    res_dict["MSE"] = accuracy.mse(result_list)
    res_dict["MAE"] = accuracy.mae(result_list)

    return res_dict


if __name__ == "__main__":
    args = parse_args()
    main(args)