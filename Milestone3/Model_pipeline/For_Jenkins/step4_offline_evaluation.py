#-*- coding: utf-8 -*-
# Created by YoonseokHeo at 220329

import sys, json, argparse
#sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone3/Model_/")

import os
import os.path as osp
import pickle
from surprise import accuracy, dump
from tqdm import tqdm
from path.path import get_project_root
from datetime import datetime
from RecSys_Management.datasets import RecDataset
from RecSys_Management.offline_evaluation import load_model, get_metric, do_prediction
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--CSR_dir_path", type=str, default="DB/CORPUS",
                        help="corpus path to be used in training")

    parser.add_argument("--model_name", type=str, default="svd", help="svd or svdpp")
    parser.add_argument("--trained_model_dir_path", type=str,
                        default="RecSys_Management/model/save",
                        help="data path")
    parser.add_argument("--off_eval_save_path", type=str, 
                        default="/home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/results_offline.json",
                        help="minwoo_path")
    # Parse the arguments
    args = parser.parse_args()


    return args

def readJson(path):
    flag_ = False
    while not flag_:
        try:
            file = open(path)
            json_data = json.load(file)
        except json.decoder.JSONDecodeError:
            pass
        else:
            flag_ = True
    # json_data = json.load(file)
    file.close()

    return json_data


def writeJson(RootDir, fileInfo):
    with open(RootDir, 'w') as write_file:
        json.dump(fileInfo, write_file, ensure_ascii=False, indent = '\t')
    
    return

def main():
    args = parse_args()
    model_name = args.model_name.lower()
    if model_name == "svd" or model_name == "svdpp":
        pass
    else:
        assert "Error: model_name should be either 'svd' or 'svdpp'"

    save_dir_path = osp.join(get_project_root(), args.trained_model_dir_path, model_name)
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
    print("  >> Do prediction...")
    res = do_prediction(test_data=df_data.test, model=trained_model)

    print("\n######     OFFLINE EVALUATION   #######")
    metrics = get_metric(result_list=res)
    cur_rmse = metrics["RMSE"]

    # save result to log data
    time_info = datetime.now()
    tmp_dict = {"time":str(time_info),"result":cur_rmse}
    if os.path.isfile(args.off_eval_save_path):
        resultsJsonInfo = readJson(args.off_eval_save_path)
        print("181818: ".format(type(resultsJsonInfo["OfflineQuery"])))
        resultsJsonInfo['OfflineQuery'].append(tmp_dict) 
       
    else:
        resultsJsonInfo = {}
        resultsJsonInfo['OfflineQuery'] = [tmp_dict]

    writeJson(args.off_eval_save_path, resultsJsonInfo)

    return

if __name__ == "__main__":
    main()
