# -*- coding: utf-8 -*-
# Created by ysHeo at 220329

import os, json, argparse, random, time
import pandas as pd
import numpy as np
import os.path as osp
from datetime import datetime
import pickle

from surprise import SVD, Dataset, accuracy, Reader, SVDpp, dump
from tqdm import tqdm
from path.path import get_project_root
from RecSys_Management.datasets import RecDataset

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--CSR_dir_path", type=str, default="DB/CORPUS",
                        help="corpus path to be used in training")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model_name", type=str, default="svd", help="svd, svdpp")
    parser.add_argument("--n_epochs", type=int, default=20)
    parser.add_argument("--n_factors", type=int, default=50, help="# of latent features")
    parser.add_argument("--model_save_path", type=str, default="RecSys_Management/model/save")


    parser.add_argument("--set_record", action="store_const", default=False, const=True)


    # Parse the arguments.
    args = parser.parse_args()
    # Set seeds
    random.seed(args.seed)

    return args


def main(args):

    dataset = RecDataset(args)
    df_data, sp_data = dataset.build_train_valid_dataset()

    # TRAIN
    date_string = datetime.now().strftime('%Y%m%d_%H%M')
    dir_path = osp.join(get_project_root(), args.model_save_path)
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

    if args.set_record is True:
        latest_file_path = osp.join(dir_path, "latest_info.json")
        info = {"latest_path": date_string,
                "valid_rmse": cur_rmse}
        with open(latest_file_path, "w") as f:
            json.dump(info, f)

        print("  >> latest_path has been changed...")

    return



def train(args, df_data, sp_data, save_dir_path):
    #"""
    model = get_model(args,
                      n_factors=args.n_factors,
                      n_epochs=args.n_epochs)
    #"""
    #model = get_model(args, args.n_factors, 1)
    print("  >> model specification")
    print(model)
    start_train = time.time()
    model.fit(sp_data.train)
    """
    for i in range(args.n_epochs):
        model.fit(sp_data.train)
        # Model save
        save_filename = os.path.join(save_dir_path, "dump_file")
        dump.dump(save_filename, algo=model)
        res = do_prediction(test_data=df_data.valid, model=model)
        print("\n######     VALIDATION Metric   #######")
        metrics = get_metric(result_list=res)
        print("current epoch: {}".format(i))
        print("")
    """


    end_train = time.time()

    # Model save
    save_filename = os.path.join(save_dir_path, "dump_file")
    dump.dump(save_filename, algo=model)

    print("  >> Trained model path... {}".format(save_filename))

    # Args save
    args_filename = osp.join(save_dir_path, "args.bin")
    with open(args_filename, "wb") as f:
        pickle.dump(args, f)

    training_time = end_train - start_train
    num_train_size = df_data.train.shape[0]
    print(" Total Training time with {} data: {:.3f} for {}-epochs ".format(
        num_train_size, training_time, args.n_epochs))

    return model

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



def test(args, df_data, trained_model):
    movie_info_dir = "/home/yoonseoh/Development/Build_Dataset/save_ratings/20220209_1329"
    movie_filepath = os.path.join(movie_info_dir, "movie_id2idx.json")
    with open(movie_filepath, "r") as f:
        movie_info_dict = json.load(f)
    movie_idx2idfilepath = os.path.join(movie_info_dir, "movie_idx2id.json")
    with open(movie_idx2idfilepath, "r") as f:
        movie_idx2id = json.load(f)

    train_ratings = df_data.train

    total_movies = movie_idx_list = list(movie_info_dict.values())

    test_userID_list = df_data.test["userID"]
    inference_time = 0.0
    test_res_dict = dict()
    iter_wrapper = (lambda x: tqdm(x, total=len(test_userID_list)))

    print("  >> Start Test...")

    for idx in iter_wrapper(range(len(test_userID_list))):
        userID = test_userID_list[idx]
    #for idx, userID in enumerate(test_userID_list):
        userID = str(int(userID))
        unseen_movies = get_unseen_surprise(ratings=train_ratings, userID=userID,
                                            total_movies=total_movies)
        result, latency = recomm_movie_by_surprise(trained_model, userID, unseen_movies, movie_idx2id=movie_idx2id, top_n=20)
        test_res_dict[userID] = result
        inference_time += latency

    from pprint import pprint
    pprint(test_res_dict[:10])
    print("Latency for {} samples: {}".format(len(test_userID_list), inference_time))
    print("  >> End of test....")

    return


def recomm_movie_by_surprise(algo, userId, unseen_movies, movie_idx2id, top_n=20):
    # 실제로 한명의 유저가 지금까지 안본 영화에 대한 예상 평점을 모두 계산
    # 아직 보지 않은 영화의 예측 평점: prediction 객체 생성
    inference_time = 0.0
    predictions = []
    for movieId in unseen_movies:
        start_time = time.time()
        res_tmp = algo.predict(str(userId), str(movieId))
        end_time = time.time()
        predictions.append(res_tmp)
        inference_time += (end_time-start_time)

    # 리스트 내의 prediction 객체의 est를 기준으로 내림차순 정렬
    def sortkey_est(pred):
        return pred.est

    predictions.sort(key=sortkey_est, reverse=True)  # key에 리스트 내 객체의 정렬 기준을 입력

    # 상위 top_n개의 prediction 객체
    top_predictions = predictions[:top_n]

    # 영화 아이디, 제목, 예측 평점 출력
    #print(f"Top-{top_n} 추천 영화 리스트")

    result = []
    for pred in top_predictions:
        movie_idx = int(pred.iid)
        # movie_title = movies[movies["movieId"] == movie_id]["title"].tolist()
        movie_title = movie_idx2id[movie_idx]
        movie_rating = pred.est

        result.append((movie_title, movie_rating))
        #print(f"{movie_title}: {movie_rating:.2f}")

    return result, inference_time


# 아직 보지 않은 영화 리스트 함수
#def get_unseen_surprise(ratings, userID, movie_info_dict):
def get_unseen_surprise(ratings, userID, total_movies):
    # 특정 userId가 평점을 매긴 모든 영화 리스트
    seen_movies = ratings[ratings['userID'] == userID]['movieID'].tolist()

    # 모든 영화명을 list 객체로 만듬.
    #total_movies = movies['movieId'].tolist()
    #movie_id_list = list(movie_info_dict.keys())
    #total_movies = movie_idx_list = list(movie_info_dict.values())

    # 한줄 for + if문으로 안 본 영화 리스트 생성
    unseen_movies = [ movie for movie in total_movies if str(movie) not in seen_movies]

    # 일부 정보 출력
    #total_movie_cnt = len(total_movies)
    #seen_cnt = len(seen_movies)
    #unseen_cnt = len(unseen_movies)

    #print(f"전체 영화 수: {total_movie_cnt}, 평점 매긴 영화 수: {seen_cnt}, 추천 대상 영화 수: {unseen_cnt}")

    return unseen_movies

def get_metric(result_list):
    res_dict = dict()
    res_dict["RMSE"] = accuracy.rmse(result_list)
    res_dict["MSE"] = accuracy.mse(result_list)
    res_dict["MAE"] = accuracy.mae(result_list)

    return res_dict

def get_model(args, n_factors, n_epochs):
    if args.model_name.lower() == "svd":
        return SVD(n_factors=n_factors, n_epochs=n_epochs, verbose=True)

    elif args.model_name.lower() == "svdpp":
        return SVDpp(n_factors=n_factors, n_epochs=n_epochs, verbose=True)


if __name__ == "__main__":
    args = parse_args()
    main(args)
