# -*- coding: utf-8 -*-
# Created by ysHeo at 220209

import os, json, argparse, random, time
import pandas as pd
import numpy as np
from datetime import datetime

from surprise import SVD, Dataset, accuracy, Reader, SVDpp, dump
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


class deployment_process():
    def __init__(self, CSR_data_path, trained_model_path):
        start = time.time()
        # CSR_data_path : ./large_data
        #self.movie_info_dir = CSR_data_path    #"/home/yoonseoh/Development/Build_Dataset/save_ratings/20220209_1329"
        CSR_data_path = "/home/yoonseoh/Development/Build_Dataset/save_ratings/20220209_1329"
        # Yoon-Debug
        self.movie_info_dir =  CSR_data_path
        print(" >> Data Loading...")
        self.df_data = self.data_loader(CSR_dir_path = CSR_data_path)
        self.movie_id2idx, self.movie_idx2id, self.user_id2idx, self.user_idx2id = self.load_metadata()
        self.all_ratings = self.df_data.train
        end = time.time()

        print( " >> Check: ", end-start)

        start = time.time()
        print(" >> Model Loading...")
        dump_file_path = os.path.join(trained_model_path, "dump_file")
        _, loaded_model = dump.load(dump_file_path)
        self.trained_model = loaded_model
        end = time.time()

        print(" >> Check2: ", end - start)

        start = time.time()
        self.total_movies_idx = list(self.movie_id2idx.values())
        self.unseen_movies_dict = dict()
        #self.before_inference()
        end = time.time()

        print(" >> Check3: ", end - start)
        print("PAUSE")

    def before_inference(self):
        print("  >> Preparing test...")

        all_userID_list = self.user_idx2id

        # Calculate "Unseen movies" for each user
        iter_wrapper = (lambda x: tqdm(x, total=len(all_userID_list)))
        for idx, userID in iter_wrapper(enumerate(all_userID_list)):
            unseen_movies = self.get_unseen_surprise(ratings=self.all_ratings, userID=userID,
                                                     total_movies=self.total_movies_idx)
            self.unseen_movies_dict[userID] = unseen_movies

    def recommend(self, test_userID, top_n=20):
        """
        :param test_userID: int??? ?????????
        :return:
        """
        userID = str(int(test_userID))

        user_idx = self.user_idx2id

        # ?????????????????? ?????? ID??? ??????????????????, ?????? ??????????????? ??? INDEX??? ?????????
        try:
            userID_idx = self.user_id2idx[userID]

            #unseen_movies = self.unseen_movies_dict[userID]
            unseen_movies = self.get_unseen_surprise(ratings=self.all_ratings, userIDX=userID_idx,
                                                     total_movies=self.total_movies_idx)
        except KeyError:
            print("  >> ERROR: COLD_START!!!!!")
            return -1

        #result, latency = self.recomm_movie_by_surprise(userID, unseen_movies, top_n=top_n)
        result, latency = self.recomm_movie_by_surprise(userID_idx, unseen_movies, top_n=top_n)

        #print("Latency for {} samples: {}".format(len(test_userID_list), inference_time))

        return result

    def recomm_movie_by_surprise(self, userIdx, unseen_movies, top_n=20):
        # ????????? ????????? ????????? ???????????? ?????? ????????? ?????? ?????? ????????? ?????? ??????
        # ?????? ?????? ?????? ????????? ?????? ??????: prediction ?????? ??????
        # userId: ???????????? ????????? ?????????!!!!!
        inference_time = 0.0
        predictions = []
        algo = self.trained_model
        start_time = time.time()
        for movieId in unseen_movies:
            res_tmp = algo.predict(str(userIdx), str(movieId))

            predictions.append(res_tmp)

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
            movie_title = self.movie_idx2id[movie_idx]
            movie_rating = pred.est

            result.append((movie_title, movie_rating))
            # print(f"{movie_title}: {movie_rating:.2f}")

        end_time = time.time()
        inference_time += (end_time - start_time)

        return result, inference_time

    # ?????? ?????? ?????? ?????? ????????? ??????
    # def get_unseen_surprise(ratings, userID, movie_info_dict):
    def get_unseen_surprise(self, ratings, userIDX, total_movies):
        # ?????? userId??? ????????? ?????? ?????? ?????? ?????????
        seen_movies = ratings[ratings['userID'] == userIDX]['movieID'].tolist()

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

        #reader = Reader(rating_scale=(1.0, 5.0))
        #train_data = Dataset.load_from_df(df_all[["userID", "movieID", "rating"]], reader=reader)
        #train_data = train_data.build_full_trainset()

        df_data = DF_DATA(df_all, None, None)
        #sp_data = SURPRISE_DATA(train_data, None, None)

        return df_data

if __name__ == "__main__":
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