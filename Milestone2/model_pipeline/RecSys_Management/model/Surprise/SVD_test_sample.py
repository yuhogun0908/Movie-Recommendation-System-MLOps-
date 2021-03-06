# -*- coding: utf-8 -*-
# Created by ysHeo at 220209

import os, json, argparse, random, time
import pandas as pd
import numpy as np
from datetime import datetime

from surprise import SVD, Dataset, accuracy, Reader, SVDpp, dump
from surprise.model_selection import train_test_split
from tqdm import tqdm


class DF_DATA(object):
    def __init__(self, train, valid, test):
        self.train = train
        self.valid = valid
        self.test = test


class SURPRISE_DATA(object):
    """ ONLY for "fit" method during training"""

    def __init__(self, train, valid, test):
        self.train = train
        self.valid = valid
        self.test = test


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--CSR_dir_path", type=str,
                        default="/home/yoonseoh/Development/Build_Dataset/save_ratings/20220209_1329/data_split",
                        help="data path")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model_name", type=str, default="svd", help="svd, svdpp")
    parser.add_argument("--n_epochs", type=int, default=10)
    parser.add_argument("--n_factors", type=int, default=50, help="# of latent features")
    parser.add_argument("--model_save_path", type=str, default="save")
    parser.add_argument("--do_validation", action='store_const', default=False, const=True)
    parser.add_argument("--do_test", action="store_const", default=False, const=True)
    parser.add_argument("--trained_model_path", type=str,
                        default="/home/yoonseoh/Development/model/Surprise/save/20220209_1810",
                        help="data path")
    parser.add_argument("--num_testcases", type=int, default=20)

    # Parse the arguments.
    args = parser.parse_args()
    # Set seeds
    random.seed(args.seed)

    return args


def train(args, df_data, sp_data, save_dir_path):
    model = get_model(args,
                      n_factors=args.n_factors,
                      n_epochs=args.n_epochs)
    print("  >> model specification")
    print(model)
    start_train = time.time()
    model.fit(sp_data.train)
    end_train = time.time()

    save_filename = os.path.join(save_dir_path, "dump_file")
    dump.dump(save_filename, algo=model)

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
    num_tests = args.num_testcases
    total_movies = movie_idx_list = list(movie_info_dict.values())

    test_userID_list = df_data.test["userID"]
    inference_time = 0.0
    test_res_dict = dict()
    iter_wrapper = (lambda x: tqdm(x, total=len(test_userID_list[:num_tests])))

    print("  >> Start Test...")

    for idx in iter_wrapper(range(len(test_userID_list[:num_tests]))):
        userID = test_userID_list[idx]
        # for idx, userID in enumerate(test_userID_list):
        userID = str(int(userID))
        unseen_movies = get_unseen_surprise(ratings=train_ratings, userID=userID,
                                            total_movies=total_movies)
        result, latency = recomm_movie_by_surprise(trained_model, userID, unseen_movies, movie_idx2id=movie_idx2id,
                                                   top_n=20)
        test_res_dict[userID] = result
        inference_time += latency

    from pprint import pprint
    pprint(test_res_dict)
    print("Latency for {} samples: {}".format(len(test_userID_list), inference_time))
    print("  >> End of test....")

    return


def recomm_movie_by_surprise(algo, userId, unseen_movies, movie_idx2id, top_n=20):
    # ????????? ????????? ????????? ???????????? ?????? ????????? ?????? ?????? ????????? ?????? ??????
    # ?????? ?????? ?????? ????????? ?????? ??????: prediction ?????? ??????
    inference_time = 0.0
    predictions = []
    for movieId in unseen_movies:
        start_time = time.time()
        res_tmp = algo.predict(str(userId), str(movieId))
        end_time = time.time()
        predictions.append(res_tmp)
        inference_time += (end_time - start_time)

    # ????????? ?????? prediction ????????? est??? ???????????? ???????????? ??????
    def sortkey_est(pred):
        return pred.est

    predictions.sort(key=sortkey_est, reverse=True)  # key??? ????????? ??? ????????? ?????? ????????? ??????

    # ?????? top_n?????? prediction ??????
    top_predictions = predictions[:top_n]

    # ?????? ?????????, ??????, ?????? ?????? ??????
    # print(f"Top-{top_n} ?????? ?????? ?????????")

    result = []
    for pred in top_predictions:
        movie_idx = int(pred.iid)
        # movie_title = movies[movies["movieId"] == movie_id]["title"].tolist()
        movie_title = movie_idx2id[movie_idx]
        movie_rating = pred.est

        result.append((movie_title, movie_rating))
        # print(f"{movie_title}: {movie_rating:.2f}")

    return result, inference_time


# ?????? ?????? ?????? ?????? ????????? ??????
# def get_unseen_surprise(ratings, userID, movie_info_dict):
def get_unseen_surprise(ratings, userID, total_movies):
    # ?????? userId??? ????????? ?????? ?????? ?????? ?????????
    seen_movies = ratings[ratings['userID'] == userID]['movieID'].tolist()

    # ?????? ???????????? list ????????? ??????.
    # total_movies = movies['movieId'].tolist()
    # movie_id_list = list(movie_info_dict.keys())
    # total_movies = movie_idx_list = list(movie_info_dict.values())

    # ?????? for + if????????? ??? ??? ?????? ????????? ??????
    unseen_movies = [str(movie) for movie in total_movies if str(movie) not in seen_movies]

    # ?????? ?????? ??????
    # total_movie_cnt = len(total_movies)
    # seen_cnt = len(seen_movies)
    # unseen_cnt = len(unseen_movies)

    # print(f"?????? ?????? ???: {total_movie_cnt}, ?????? ?????? ?????? ???: {seen_cnt}, ?????? ?????? ?????? ???: {unseen_cnt}")

    return unseen_movies


def main(args):
    print(" >> Data Loading...")
    df_data, sp_data = data_loader(args)

    # TEST
    if args.do_test is True:
        dump_file_path = os.path.join(args.trained_model_path, "dump_file")
        _, loaded_model = dump.load(dump_file_path)
        test(args=args, df_data=df_data, trained_model=loaded_model)

    else:
        # TRAIN
        date_string = datetime.now().strftime('%Y%m%d_%H%M')
        save_dir_path = os.path.join(os.getcwd(), os.path.join(args.model_save_path, date_string))
        if not os.path.exists(save_dir_path):
            os.makedirs(name=save_dir_path)

        trained_model = train(args, df_data, sp_data, save_dir_path)
        if args.do_validation is True:
            res = do_prediction(test_data=df_data.valid, model=trained_model)
            print("\n######     VALIDATION Metric   #######")
            metrics = get_metric(result_list=res)

            # print("  >> RMSE: {}".format(metrics["RMSE"]))
            # print("  >> MSE: {}".format(metrics["MSE"]))
            # print("  >> MAE: {}".format(metrics["MAE"]))

            res = do_prediction(test_data=df_data.test, model=trained_model)
            print("\n######     TEST Metric   #######")
            metrics = get_metric(result_list=res)
            # print("\n######     TEST Metric   #######")
            # print("  >> RMSE: {}".format(metrics["RMSE"]))
            # print("  >> MSE: {}".format(metrics["MSE"]))
            # print("  >> MAE: {}".format(metrics["MAE"]))

        print("\n>>  Training is completed... ")
        print("  >> Check the model: {}".format(save_dir_path))

    return


def get_metric(result_list):
    res_dict = dict()
    res_dict["RMSE"] = accuracy.rmse(result_list)
    res_dict["MSE"] = accuracy.mse(result_list)
    res_dict["MAE"] = accuracy.mae(result_list)

    return res_dict


def get_model(args, n_factors, n_epochs):
    if args.model_name.lower() == "svd":
        return SVD(n_factors=n_factors, n_epochs=n_epochs)

    elif args.model_name.lower() == "svdpp":
        return SVDpp(n_factors=n_factors, n_epochs=n_epochs)


def data_loader(args):
    train_path = os.path.join(args.CSR_dir_path, "train_idx.json")
    valid_path = os.path.join(args.CSR_dir_path, "valid_idx.json")
    test_path = os.path.join(args.CSR_dir_path, "test_idx.json")

    with open(train_path, "r") as f:
        train_csr = np.array(json.load(f))
    with open(valid_path, "r") as f:
        valid_csr = np.array(json.load(f))
    with open(test_path, "r") as f:
        test_csr = np.array(json.load(f))

    df_train = pd.DataFrame(train_csr)
    df_valid = pd.DataFrame(valid_csr)
    df_test = pd.DataFrame(test_csr)

    df_train = df_train.astype({0: "int", 1: "int", 2: "float"})
    df_train = df_train.astype({0: str, 1: str})
    # print(df_train.dtypes)

    df_valid = df_valid.astype({0: "int", 1: "int", 2: "float"})
    df_valid = df_valid.astype({0: str, 1: str})
    # print(df_valid.dtypes)

    df_test = df_test.astype({0: "int", 1: "int", 2: "float"})
    df_test = df_test.astype({0: str, 1: str})

    df_train.columns = ["userID", "movieID", "rating"]
    df_valid.columns = ["userID", "movieID", "rating"]
    df_test.columns = ["userID", "movieID", "rating"]

    reader = Reader(rating_scale=(1.0, 5.0))
    train_data = Dataset.load_from_df(df_train[["userID", "movieID", "rating"]], reader=reader)
    valid_data = Dataset.load_from_df(df_valid[["userID", "movieID", "rating"]], reader)
    test_data = Dataset.load_from_df(df_test[["userID", "movieID", "rating"]], reader)

    train_data = train_data.build_full_trainset()

    df_data = DF_DATA(df_train, df_valid, df_test)
    sp_data = SURPRISE_DATA(train_data, valid_data, test_data)

    return df_data, sp_data


if __name__ == "__main__":
    args = parse_args()
    main(args)
