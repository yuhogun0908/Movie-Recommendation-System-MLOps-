# -*- coding: utf-8 -*-
# Created by ys.heo at 220209

import os, argparse
import numpy as np
from path.path import get_project_root


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_path", type=str,
                        default="save_ratings/20220209_2251",
                        help="data path for our corpus")

    # Parse the arguments.
    args = parser.parse_args()


    return args

args = parse_args()

#dir_path = "/home/yoonseoh/Development/Build_Dataset/save_ratings/20220209_1329"
#dir_path = "/home/yoonseoh/Development/Build_Dataset/save_ratings/20220209_1329/scalable_data/20220209_1350/1"


dir_path = os.path.join(get_project_root(), args.dir_path)
filepath = os.path.join(dir_path, "rating.npy")
save_path = os.path.join(dir_path, "rating_csr.npy")
ratings = np.load(filepath)

num_cols = np.shape(ratings)[1]
nonzero_idx_list = np.flatnonzero(ratings)
data_2d_idx = []
for _1d_idx in nonzero_idx_list:
    row_idx = _1d_idx // num_cols
    col_idx = _1d_idx % num_cols
    # train_data_2d_idx.append(make_dict_elem(row_idx, col_idx, rating_mat[row_idx][col_idx]))
    data_2d_idx.append((row_idx, col_idx, ratings[row_idx][col_idx]))

data_2d_idx = np.array(data_2d_idx)

print("  >> Save CSR 2d matrix.... Wait....")
np.save(save_path, data_2d_idx)
print("  >> Check the result in {}".format(save_path))

