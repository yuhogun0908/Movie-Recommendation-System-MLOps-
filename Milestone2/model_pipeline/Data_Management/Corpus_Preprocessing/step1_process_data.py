# -*- coding: utf-8 -*-
# Created by ys.heo at 220203
# mail: yoonseoh@andrew.cmu.edu

import os, json, pickle
import argparse
import random
import numpy as np
import pandas as pd
from path.path import get_project_root
from datetime import datetime
from collections import Counter, OrderedDict
import os.path as osp


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default="tmp_data", help="relative data path from the project directory")
    parser.add_argument("--seed", type=int, default=9595, help='random seed')
    parser.add_argument("--save_path", type=str, default="save_ratings", help="relative filepath from the root directory for save_ratings")
    parser.add_argument("--movie_threshold", type=int, default=7, help="#minimum # of ratings per movie")
    parser.add_argument("--user_threshold", type=int, default=10, help="minumum # of ratings per user")
    parser.add_argument("--user_max_threshold", type=int, default=31, help="maximum # of ratings per user")

    # Parse the arguments.
    args = parser.parse_args()

    # Set seeds
    random.seed(args.seed)
    np.random.seed(args.seed)

    return args


def hogeon_request(movie_list):
    id2title_dict = dict()
    title2id_dict = dict()
    for idx, movie_elem in enumerate(movie_list):
        try:
            id = movie_elem["movieQuery"]["id"]
            title = movie_elem["movieQuery"]["title"]
            id2title_dict[id] = title
            title2id_dict[title] = id

        except KeyError:
            continue

    output_path = os.path.join(get_project_root(), "Build_Dataset/Hogeon")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    filepath_id = os.path.join(output_path, "id2title_dict.json")
    filepath_title = os.path.join(output_path, "title2id_dict.json")
    with open(filepath_id, "w") as f:
        json.dump(id2title_dict, f, indent="\t")

    with open(filepath_title, "w") as f:
        json.dump(title2id_dict, f, indent="\t")

    print("  #######    Hogeon Request      ########")
    print("  >> Check the result in {}".format(filepath_id))
    print("  >> Check the result in {}".format(filepath_title))

    exit(-1)

    return


def main():
    args = parse_args()  # Argument Passing
    data_dir_path = osp.join(get_project_root(), args.data_path)
    all_data = read_data(data_path=data_dir_path)  # Read all data from the copied corpus from "/home/data/"

    # hogeon_request(movie_list=all_data["movie"])

    ratings_dict = get_ratings(args=args, movie_data_list=all_data["movie"])  # Get ratings
    user_movie_rating_dict, user_idx2id, user_id2idx, movie_idx2id, movie_id2idx = \
        build_user_movie_rating_dict(args=args, rating_dict=ratings_dict)

    rating_matrix = build_rating_matrix(user_movie_rating_dict, user_idx2id, user_id2idx, movie_idx2id, movie_id2idx)
    get_statistics(rating_matrix=rating_matrix)
    save_data(args, rating_matrix, user_idx2id, user_id2idx, movie_idx2id, movie_id2idx)

    return


def save_data(save_path, rating_matrix, user_idx2id, user_id2idx, movie_idx2id, movie_id2idx):
    print("  >> Wait.... ")

    dir_path = save_path

    if not os.path.exists(dir_path):
        os.makedirs(name=dir_path)
    rating_filename = os.path.join(dir_path, "rating.csv")
    save_rating_csv(rating_matrix, output_filepath=rating_filename)
    np.save(os.path.join(dir_path, "rating.npy"), rating_matrix)

    with open(os.path.join(dir_path, "user_idx2id.json"), "w") as f:
        json.dump(user_idx2id, f, indent=" ")

    with open(os.path.join(dir_path, "user_id2idx.json"), "w") as f:
        json.dump(user_id2idx, f, indent='\t')

    with open(os.path.join(dir_path, "movie_idx2id.json"), "w") as f:
        json.dump(movie_idx2id, f, indent=" ")

    with open(os.path.join(dir_path, "movie_id2idx.json"), "w") as f:
        json.dump(movie_id2idx, f, indent='\t')

    print("  >> Check the rating matrix in '{}' directory".format(dir_path))
    return


def save_rating_csv(numpy_mat, output_filepath):
    rows = np.shape(numpy_mat)[0]
    cols = np.shape(numpy_mat)[1]

    index_dict = dict()
    for i in range(rows):
        name = "usr#" + str(i)
        # index_dict[str(i)] = name
        index_dict[i] = name

    cols_dict = dict()
    for i in range(cols):
        name = "mov#" + str(i)
        # cols_name.append(name)
        # cols_dict[str(i)] = name
        cols_dict[i] = name

    df_data = pd.DataFrame(data=numpy_mat)
    df_data.rename(index=index_dict, inplace=True)
    df_data.rename(columns=cols_dict, inplace=True)

    df_data.to_csv(output_filepath, mode="w")

    return


def get_statistics(rating_matrix):
    num_rows = np.shape(rating_matrix)[0]
    num_cols = np.shape(rating_matrix)[1]
    num_all_pairs = num_rows * num_cols
    num_non_zeros = np.count_nonzero(rating_matrix)
    value_ratio = num_non_zeros / num_all_pairs

    print("###########  Statistics of Rating Matrix ################\n")
    print("  >> size of (user, movie) rating matrix(R): {}*{}  ({})".format(num_rows, num_cols, num_all_pairs))
    print("  >> # of actual ratings: {}".format(num_non_zeros))
    print("  >> Ratio of ratings in the matrix(R): {:.4f}".format(value_ratio))
    print("\n#########################################################\n")


def make_pair_list(key_list):
    idx2key = []
    key2idx = OrderedDict()
    for idx, key in enumerate(key_list):
        idx2key.append(key)
        key2idx[key] = idx

    return idx2key, key2idx


def build_rating_matrix(user_movie_rating_dict, user_idx2id, user_id2idx, movie_idx2id, movie_id2idx):
    rating_matrix = np.zeros(shape=(len(user_idx2id), len(movie_idx2id)), dtype=float)
    for idx, (user_info, movie_score_list) in enumerate(user_movie_rating_dict.items()):
        user_idx = user_id2idx[user_info]
        for info in movie_score_list:
            movie_id = info[0]
            movie_score = info[1]
            movie_idx = movie_id2idx[movie_id]
            rating_matrix[user_idx][movie_idx] = movie_score  # Rating
    # TODO: Unit test of rating_matrix about TYPE(numpy.ndarray)
    # TODO: Unit test of rating_matrix about Dimension( len(user_id2idx), len(movie_id2idx) )
    return rating_matrix

class PRUNING_CASE():
    """
    2 types of removing data from the corpus
    - CASE1: Remove the movie category from the training data
                if # of ratings for a movie is smaller than self.args.movie_threshold
    - CASE2: Remove the user information from the training data
                if # of movies that an user has rated
                    1) is small than self.args.user_threshold OR
                    2) is larger than self.args.user_max_threshold      # TODO: (yoon)이건 지워야 될거 같아...
            (More specifically, remove it from the user-movie-rating matrix)
    """
    def __init__(self, sample, args, case_number):
        self.testcase = sample
        self.args = args
        self.case_number = case_number

    @property
    def get_pruning_result(self):
        if self.case_number == 1:
            return self.__case_1__
        elif self.case_number == 2:
            return self.__case_2__

    @property
    def __case_1__(self):
        bool_result = False
        if len(self.testcase) < self.args.movie_threshold:
            return True
        else:
            return bool_result

    @property
    def __case_2__(self):
        bool_result = False
        if len(self.testcase) < self.args.user_threshold:
            return True
        elif len(self.testcase) > self.args.user_max_threshold:
            return True
        else:
            return bool_result


# MOVIE 파일에 있는 ratingUserList의 모든 User 수로 Rating MATRIX의 ROW가 결정됨
def build_user_movie_rating_dict(args, rating_dict):
    """

    :param args:
    :param rating_dict: a dictionary containing ratings for movies
    :return: user_movie_rating_dict:  A dictionary containing a record of each user's movie ratings.
            user_idx2id, user_id2idx: lists for users_ids and "INDEX to USER_IDS"
            movie_idx2id, movie_id2idx: lists for movies ids and "INDEX to movie_ids"
    """
    movie_ids = sorted(list(rating_dict.keys()))
    #movie_idx2id, movie_id2idx = make_pair_list(key_list=movie_ids)

    user_movie_rating_dict = dict()
    user_Counter = Counter()
    revised_movie_ids = []
    for movie in movie_ids:
        rating_info = rating_dict[movie]
        userid_list = list(rating_info.keys())

        revised_movie_ids.append(movie)     # Rating Matrix가 될 movie ID

        for userid in userid_list:
            user_Counter.update([userid])
        # user_Counter.update([userid] for userid in userid_list)
        for userid, score in rating_info.items():
            added = (movie, score)
            if userid in user_movie_rating_dict:
                user_movie_rating_dict[userid].append(added)
            else:
                user_movie_rating_dict[userid] = [added]

    # User가 Rating한 Movie 수가 THRESHOLD 이하이면, USER 제거하기
    key_pop_list = []
    for userid, movie_score_list in user_movie_rating_dict.items():
        # TODO: Unit Test for checking the minimum or maximum # of movies that an user has rated
        check_flag = PRUNING_CASE(sample=movie_score_list, args=args, case_number=2)
        if check_flag.get_pruning_result is True:
            key_pop_list.append(userid)
            continue
    cur_size = len(user_movie_rating_dict)
    for userid in key_pop_list:
        user_movie_rating_dict.pop(userid, "181818")
    after_size = len(user_movie_rating_dict)
    print("  >> # users deleted: {}".format(cur_size - after_size))
    print("  >> Successfully preprocessing....")


    movie_ids = sorted(list(revised_movie_ids))
    movie_idx2id, movie_id2idx = make_pair_list(key_list=movie_ids)
    #user_ids = sorted(list(user_Counter.keys()))
    user_ids = sorted(list(user_movie_rating_dict.keys()))
    user_idx2id, user_id2idx = make_pair_list(user_ids)

    return user_movie_rating_dict, user_idx2id, user_id2idx, movie_idx2id, movie_id2idx


def get_ratings(args, movie_data_list):
    """
    :param args: argument
    :param movie_data_list: all the movies from the raw data
    :return: rating_dict: a dictionary(movie_name, user_rating_dictionary)
                            Each movie has ratings more than self.args.movie_threshold
    """
    rating_dict = dict()
    movieID_error_list = []
    for idx, movie_elem in enumerate(movie_data_list):
        movie_info = movie_elem["movieQuery"]
        # already_seen_users = movie_elem["userList"]
        # TODO: Unit Test for checking the data quality of data integrity: Missing a movieID in a movie data
        try:
            movieID = movie_info["id"]
        except KeyError:
            movieID_error_list.append(movie_data_list[idx])
        if "ratingUserList" in movie_elem.keys():
            # TODO: (by Yoon)Data Preprocessing
            check_flag = PRUNING_CASE(sample=movie_elem["ratingUserList"], args=args, case_number=1)
            if check_flag.get_pruning_result is True:
                continue
            rating_dict[movieID] = movie_elem["ratingUserList"]
    """
    if len(movieID_error_list) != 0:
        with open("movieID_error.json", "w") as f:
            json.dump(movieID_error_list, f, indent='\t')
    """
    print("  >> # of rated movies: {}".format(len(rating_dict)))
    return rating_dict


def read_data(data_path):
    """
    :param data_path: filepath to the all corpus for training
    :return: a dictionary loaded "movie" and "user" json files from the path
    """
    # TODO: Unit Test for checking the existence of directory in the {data_path}

    dir_list = ["movie", "user"]
    bigdata_dict = dict()
    for dir_name in dir_list:
        bigdata_dict[dir_name] = []
        cur_dirpath = os.path.join(data_path, dir_name)
        filelist = os.listdir(cur_dirpath)
        for idx, filename in enumerate(filelist):
            cur_filepath = os.path.join(cur_dirpath, filename)
            with open(cur_filepath, "r") as f:
                data_info = json.load(f)
                bigdata_dict[dir_name].append(data_info)  # Store all the metadata as list

        print("  >> # of {}: {}\n".format(dir_name, len(bigdata_dict[dir_name])))

    # TODO: Unit Test for DataType(Dict), Key Existence Check

    return bigdata_dict


if __name__ == "__main__":
    main()
