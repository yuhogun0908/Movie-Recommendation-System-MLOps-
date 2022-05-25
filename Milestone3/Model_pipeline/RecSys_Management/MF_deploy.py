# -*- coding: utf-8 -*-
# Created by ysHeo at 220209
# Reference URL: https://techblog-history-younghunjo1.tistory.com/117?category=924148
# We exploit how to use "surprise" library

import os, json, argparse, random, time
import pandas as pd
import numpy as np
import os.path as osp
from datetime import datetime
from surprise import SVD, Dataset, accuracy, Reader, SVDpp, dump
from path.path import get_project_root

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


    # Parse the arguments.
    args = parser.parse_args()
    # Set seeds
    random.seed(args.seed)

    return args




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


class deployment_process():
    def __init__(self, CSR_data_path, trained_model_path):
        # CSR_data_path : ./large_data

        self.movie_info_dir =  CSR_data_path
        print(" >> Data Loading...")
        self.df_data = self.data_loader(CSR_dir_path = CSR_data_path)
        self.movie_id2idx, self.movie_idx2id, self.user_id2idx, self.user_idx2id = self.load_metadata()
        self.all_ratings = self.df_data.train

        print(" >> Model Loading...")
        dump_file_path = os.path.join(trained_model_path, "dump_file")
        _, loaded_model = dump.load(dump_file_path)
        self.trained_model = loaded_model

        self.total_movies_idx = list(self.movie_id2idx.values())
        self.unseen_movies_dict = dict()
        print("  >> Ready to recommend!")

    def recommend(self, test_userID, top_n=20):
        """
        :param test_userID: int,
        :param top_n : # of outputs
        :return: top-N output list
        """
        userIDX = str(int(test_userID))
        try:
            #print("@@@@@  {} @@@@", userID)

            #userIDX = self.user_id2idx[userID]
            #print("@@@@@@ {}  @@@@@".format(userIDX))
            #unseen_movies = self.get_unseen_surprise(ratings=self.all_ratings, userID=userID,
            unseen_movies=self.get_unseen_surprise(ratings=self.all_ratings, userIDX=userIDX,
                                                     total_movies=self.total_movies_idx)
        except KeyError:
            print("  >> ERROR: COLD_START!!!!!")
            return -1

        #result, latency = self.recomm_movie_by_surprise(userID, unseen_movies, top_n=top_n)
        result, latency = self.recomm_movie_by_surprise(userIDX, unseen_movies, top_n=top_n)

        #print("Latency for {} samples: {}".format(len(test_userID_list), inference_time))

        return result

    def recomm_movie_by_surprise(self, userIdx, unseen_movies, top_n=20):
        inference_time = 0.0
        predictions = []
        algo = self.trained_model
        start_time = time.time()
        for movieId in unseen_movies:
            res_tmp = algo.predict(str(userIdx), str(movieId))

            predictions.append(res_tmp)

        def sortkey_est(pred):
            return pred.est

        predictions.sort(key=sortkey_est, reverse=True)  

        top_predictions = predictions[:top_n]

        result = []
        for pred in top_predictions:
            movie_idx = int(pred.iid)
            movie_title = self.movie_idx2id[movie_idx]
            movie_rating = pred.est

            result.append((movie_title, movie_rating))

        end_time = time.time()
        inference_time += (end_time - start_time)

        return result, inference_time

    def get_unseen_surprise(self, ratings, userIDX, total_movies):
        seen_movies = ratings[ratings['userID'] == userIDX]['movieID'].tolist()

        unseen_movies = [str(movie) for movie in total_movies if str(movie) not in seen_movies]

        return unseen_movies

    def load_metadata(self):
        movie_filepath = os.path.join(self.movie_info_dir, "movie_id2idx.json")
        with open(movie_filepath, "r") as f:
            movie_id2idx = json.load(f)
        movie_idx2idfilepath = os.path.join(self.movie_info_dir, "movie_idx2id.json")
        with open(movie_idx2idfilepath, "r") as f:
            movie_idx2id = json.load(f)

        user_idx2idfilepath = os.path.join(self.movie_info_dir, "user_idx2id.json")
        with open(user_idx2idfilepath, "r") as f:
            user_idx2id = json.load(f)
        user_id2idxfilepath = os.path.join(self.movie_info_dir, "user_id2idx.json")
        with open(user_id2idxfilepath, "r") as f:
            user_id2idx = json.load(f)

        return movie_id2idx, movie_idx2id, user_id2idx, user_idx2id,


    def data_loader(self, CSR_dir_path):

        all_data_path = os.path.join(CSR_dir_path, "rating_csr.npy")
        all_csr = np.load(all_data_path)
        df_all = pd.DataFrame(all_csr)
        df_all = df_all.astype({0: "int", 1: "int", 2: "float"})
        df_all = df_all.astype({0: str, 1: str})
        df_all.columns = ["userID", "movieID", "rating"]

        df_data = DF_DATA(df_all, None, None)
        return df_data

if __name__ == "__main__":
    args = parse_args()
    CORPUS_DIR_PATH = osp.join(get_project_root(), "DB/CORPUS")
    model_name = args.model_name.lower()
    if model_name == "svd" or model_name == "svdpp":
        pass
    else:
        assert "Error: model_name should be either 'svd' or 'svdpp'"

    save_dir_path = osp.join(get_project_root(), args.trained_model_dir_path, model_name)
    with open(osp.join(save_dir_path, "latest_info.json")) as f:
        dir_name = json.load(f)["latest_path"]

    trained_model_path = osp.join(save_dir_path, dir_name)


    TRAINED_MODEL_PATH = osp.join(get_project_root(), )

    # Debug
    dp_class = deployment_process(CSR_data_path="/home/yoonseoh/Development/Build_Dataset/save_ratings/20220209_1329",
                                  trained_model_path="/home/team24/milestone1/Flask/trained_MF/model_save")

    result = dp_class.recommend(test_userID=int("33174"), top_n=5)
    result2 = dp_class.recommend(test_userID=int("12849"), top_n=5)
    from pprint import pprint
    #pprint(result)
    final = [k for k,v in result]
    pprint(final)

    final = [k for k, v in result2]
    pprint(final)

