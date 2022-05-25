# -*-coding: utf-8
# Created by ys.heo at 220206

import os, json, random, argparse
import numpy as np
from path.path import get_project_root
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all_data_dir", type=str, default="save_ratings/20220209_1329",
                        help="all_data_directory")
    parser.add_argument("--seed", type=int, default=42, help='random seed')
    parser.add_argument("--val_ratio", type=float, default=0.1)
    parser.add_argument("--test_ratio", type=float, default=0.2)

    # Parse the arguments.
    args = parser.parse_args()

    # Set seeds
    random.seed(args.seed)
    np.random.seed(args.seed)

    return args


def make_dict_elem(row_idx, col_idx, elem):
    elem_dict = dict()
    elem_dict["row"] = row_idx
    elem_dict["col"] = col_idx
    elem_dict["score"] = elem

    return elem_dict


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


def train_valid_test_split(rating_mat, num_cols, test_ratio, val_ratio):
    nonzero_idx_list = np.flatnonzero(rating_mat)
    num_idx_list = np.arange(len(nonzero_idx_list))

    np.random.shuffle(num_idx_list)

    num_test = int(len(num_idx_list) * test_ratio)
    test_idx = [nonzero_idx_list[num_idx_list[idx]] for idx in range(num_test)]

    num_valid = int(len(num_idx_list) * val_ratio)
    val_idx = [nonzero_idx_list[num_idx_list[num_test + idx]] for idx in range(num_valid)]

    train_idx = nonzero_idx_list[num_idx_list[(num_test + num_valid):]]

    # print(len(train_idx))
    # print(len(val_idx))
    # print(len(test_idx))

    train_data_2d_idx = []
    for _1d_idx in train_idx:
        row_idx = _1d_idx // num_cols
        col_idx = _1d_idx % num_cols
        # train_data_2d_idx.append(make_dict_elem(row_idx, col_idx, rating_mat[row_idx][col_idx]))
        train_data_2d_idx.append((row_idx, col_idx, rating_mat[row_idx][col_idx]))

    valid_data_2d_idx = []
    for _1d_idx in val_idx:
        row_idx = _1d_idx // num_cols
        col_idx = _1d_idx % num_cols
        valid_data_2d_idx.append((row_idx, col_idx, rating_mat[row_idx][col_idx]))
        # valid_data_2d_idx.append([row_idx, col_idx, rating_mat[row_idx][col_idx]])
        # valid_data_2d_idx.append(make_dict_elem(row_idx, col_idx, rating_mat[row_idx][col_idx]))

    test_data_2d_idx = []
    for _1d_idx in test_idx:
        row_idx = _1d_idx // num_cols
        col_idx = _1d_idx % num_cols
        # test_data_2d_idx.append([row_idx, col_idx, rating_mat[row_idx][col_idx]])
        test_data_2d_idx.append((row_idx, col_idx, rating_mat[row_idx][col_idx]))
        # test_data_2d_idx.append(make_dict_elem(row_idx, col_idx, rating_mat[row_idx][col_idx]))

    splited_rating_matrix = np.copy(rating_mat)
    for (row, col, score) in valid_data_2d_idx:
        splited_rating_matrix[row][col] = 0.0

    for (row, col, score) in test_data_2d_idx:
        splited_rating_matrix[row][col] = 0.0

    return train_data_2d_idx, valid_data_2d_idx, test_data_2d_idx, splited_rating_matrix


def do_split(args, data_path, rating_npy_path):
    #rating_data_dir_path = os.path.join(get_project_root(), args.all_data_dir)

    rating_data_dir_path = data_path
    save_dir_path = os.path.join(rating_data_dir_path, "data_split")
    if not os.path.exists(save_dir_path):
        os.makedirs(name=save_dir_path, exist_ok = True)

    #rating_npy = os.path.join(rating_data_dir_path, "rating.npy")
    rating_npy = rating_npy_path
    rating_mat = np.load(rating_npy)

    num_rows = np.shape(rating_mat)[0]
    num_cols = np.shape(rating_mat)[1]

    """
    nonzero_idx_list = np.flatnonzero(rating_mat)
    num_idx_list = np.arange(len(nonzero_idx_list))

    np.random.shuffle(num_idx_list)

    num_test = int(len(num_idx_list) * args.test_ratio)
    test_idx = [nonzero_idx_list[num_idx_list[idx]] for idx in range(num_test)]

    num_valid = int(len(num_idx_list) * args.val_ratio)
    val_idx = [nonzero_idx_list[num_idx_list[num_test + idx]] for idx in range(num_valid)]

    train_idx = nonzero_idx_list[num_idx_list[(num_test + num_valid):]]

    print(len(train_idx))
    print(len(val_idx))
    print(len(test_idx))


    train_data_2d_idx = []
    for _1d_idx in train_idx:
        row_idx = _1d_idx // num_cols
        col_idx = _1d_idx % num_cols
        #train_data_2d_idx.append(make_dict_elem(row_idx, col_idx, rating_mat[row_idx][col_idx]))
        train_data_2d_idx.append((row_idx, col_idx, rating_mat[row_idx][col_idx]))


    valid_data_2d_idx = []
    for _1d_idx in val_idx:
        row_idx = _1d_idx // num_cols
        col_idx = _1d_idx % num_cols
        valid_data_2d_idx.append((row_idx, col_idx, rating_mat[row_idx][col_idx]))
        #valid_data_2d_idx.append([row_idx, col_idx, rating_mat[row_idx][col_idx]])
        #valid_data_2d_idx.append(make_dict_elem(row_idx, col_idx, rating_mat[row_idx][col_idx]))


    test_data_2d_idx = []
    for _1d_idx in test_idx:
        row_idx = _1d_idx // num_cols
        col_idx = _1d_idx % num_cols
        #test_data_2d_idx.append([row_idx, col_idx, rating_mat[row_idx][col_idx]])
        test_data_2d_idx.append((row_idx, col_idx, rating_mat[row_idx][col_idx]))
        #test_data_2d_idx.append(make_dict_elem(row_idx, col_idx, rating_mat[row_idx][col_idx]))
    """

    train_data_2d_idx, valid_data_2d_idx, test_data_2d_idx, splited_rating_matrix = train_valid_test_split(rating_mat,
                                                                                                           num_cols,
                                                                                                           args.test_ratio,
                                                                                                           args.val_ratio)


    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return super(NpEncoder, self).default(obj)

    with open(os.path.join(save_dir_path, "train_idx.json"), "w") as f:
        json.dump(train_data_2d_idx, f, indent=" ", cls=NpEncoder)
    with open(os.path.join(save_dir_path, "valid_idx.json"), "w") as f:
        json.dump(valid_data_2d_idx, f, indent=" ", cls=NpEncoder)
    with open(os.path.join(save_dir_path, "test_idx.json"), "w") as f:
        json.dump(test_data_2d_idx, f, indent=" ", cls=NpEncoder)

    """
    new_rating = np.copy(rating_mat)
    for (row, col, score) in valid_data_2d_idx:
        new_rating[row][col] = 0.0

    for (row, col, score) in test_data_2d_idx:
        new_rating[row][col] = 0.0

    #new_nonzero_idx_list = np.flatnonzero(new_rating)
    #print(len(new_nonzero_idx_list))

    """
    print("  >> Wait...Saving splited dataset ")
    np.save(os.path.join(save_dir_path, "split_rating.npy"), splited_rating_matrix)
    save_rating_csv(splited_rating_matrix, output_filepath=os.path.join(save_dir_path, "split_rating.csv"))

    print("  >> Check train/valid/test rating data in {} path".format(save_dir_path))


if __name__ == "__main__":
    args = parse_args()
    main(args)