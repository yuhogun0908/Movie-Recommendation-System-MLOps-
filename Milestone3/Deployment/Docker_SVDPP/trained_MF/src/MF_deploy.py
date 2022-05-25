# -*- coding: utf-8 -*-
# Created by ysHeo at 220209
# Reference URL: https://techblog-history-younghunjo1.tistory.com/117?category=924148
# We exploit how to use "surprise" library

import os, json, time
import pandas as pd
import numpy as np
from datetime import datetime
from surprise import dump

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
        """

        :param CSR_data_path: ./data_for_deployment
        :param trained_model_path: ./trained_model/dump.file
        """
        # CSR_data_path : ./data_for_deployment
        self.movie_info_dir =  CSR_data_path
        print(" >> Data Loading...")
        # CSR_data_path는 rating_csr.npy전까지 디렉토리 path를 넘겨주고,
        # 실제로 도커에는 npy 파일만 전달하자!
        self.df_data = self.data_loader(CSR_dir_path = CSR_data_path)   # rating_csr.npy 데이터를 읽어옴
        self.all_ratings = self.df_data.train  # rating_csr.npy data

        # 실제로 아래 네 개중에 첫 2개(movie_id2idx, movie_idx2id)만 사용됨
        self.movie_id2idx, self.movie_idx2id, self.user_id2idx, self.user_idx2id = self.load_metadata()
        #self.movie_id2idx, self.movie_idx2id = self.load_metadata()


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
            # parameters:
            # ratings: rating_csr.npy, # userIDX: one user id, total_movies: self.movie_id2idx
            unseen_movies=self.get_unseen_surprise(ratings=self.all_ratings, userIDX=userIDX,
                                                     total_movies=self.total_movies_idx)
        except KeyError:
            print("  >> ERROR: COLD_START!!!!!")
            return -1

        result, latency = self.recomm_movie_by_surprise(userIDX, unseen_movies, top_n=top_n)
        return result

    def recomm_movie_by_surprise(self, userIdx, unseen_movies, top_n=20):
        inference_time = 0.0
        predictions = []
        algo = self.trained_model
        start_time = time.time()
        # 여기서 유저가 한번도 보지 않은 영화들 각각에 대한 추천 스코어를 계산
        for movieId in unseen_movies:
            res_tmp = algo.predict(str(userIdx), str(movieId))

            predictions.append(res_tmp)

        def sortkey_est(pred):
            return pred.est

        # Score 순서대로 Sorting
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
    # Debug
    #dp_class = deployment_process(CSR_data_path="/home/yoonseoh/Development/Build_Dataset/save_ratings/20220209_1329",
    #                              trained_model_path="/home/team24/milestone1/Flask/trained_MF/model_save")
    dp_class = deployment_process(CSR_data_path="/home/yoonseoh/group-project-s22-k-avengers/Milestone3/Model_pipeline/DB/CORPUS/20220410_0059",
                                  trained_model_path="/home/team24/milestone1/Flask/trained_MF/model_save")
    result = dp_class.recommend(test_userID=int("33174"), top_n=5)
    result2 = dp_class.recommend(test_userID=int("12849"), top_n=5)
    from pprint import pprint
    #pprint(result)
    final = [k for k,v in result]
    pprint(final)

    final = [k for k, v in result2]
    pprint(final)

