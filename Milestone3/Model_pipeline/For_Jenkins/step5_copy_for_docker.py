#-*- coding: utf-8 -*-
# Created by YoonseokHeo at 220330

import sys, json, argparse
#sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone3/")
import numpy as np
import os, shutil
import os.path as osp
from path.path import get_project_root

DATA_COPY_LIST = ["rating_csr.npy", "movie_id2idx.json", "movie_idx2id.json",
                  "user_id2idx.json", "user_idx2id.json"]
MOST_POPULAR_FILE = ["rating.npy"]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trained_model_dir_path", type=str,
                        default="RecSys_Management/model/save", 
                        help = "a directory path to the latest trained model")
    parser.add_argument("--model_name", type=str, required=True, help="svd, svdpp")
    parser.add_argument("--copy_path", type=str,
                        default="../Deployment",
                        #default="../Pipeline/Flask/trained_MF/model_update",
                        help="a  directory path to the master branch")

    parser.add_argument("--corpus_path", type=str,
                        default="DB/CORPUS",
                        help = "A dataset for movie_id and rating_csr")

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    save_dir_path = osp.join(get_project_root(), args.trained_model_dir_path,
                             args.model_name.lower())
    with open(osp.join(save_dir_path, "latest_info.json")) as f:
        dir_name = json.load(f)["latest_path"]

    trained_model_path = osp.join(osp.join(save_dir_path, dir_name), "dump_file")
    print(" >> Trained_model_path: {}".format(trained_model_path))

    docker_model_dir_name = "Docker_"+args.model_name.upper()
    if docker_model_dir_name == "Docker_SVD" or docker_model_dir_name == "Docker_SVDPP":
        pass
    else:
        assert "Errors: Model names: {svd, svdpp}"

    docker_dir_path = osp.join(get_project_root(), args.copy_path, docker_model_dir_name)
    # STEP1. MODEL COPY
    copy_trained_model(docker_dir_path, trained_model_path)

    # STEP2. DATA COPY
    load_data_path = osp.join(get_project_root(), args.corpus_path)

    for data_elem in DATA_COPY_LIST:
        copy_data(docker_dir_path, load_data_path, copy_file_name=data_elem)

    # STEP3. MOST_POPULAR for Docker
    print("  >> Wait.... ")
    copy_most_popular_top_20_movie_idx(docker_dir_path, load_data_path, TopK=20)

def copy_most_popular_top_20_movie_idx(docker_dir_path, load_data_path, TopK=20):
    """
    Return index of N most popular movies
    """
    copy_dir_path = osp.join(docker_dir_path, "most_popular")
    if not osp.isdir(copy_dir_path):
        os.makedirs(copy_dir_path, exist_ok=True)
    copy_data_path = osp.join(copy_dir_path, "most_popular.npy")

    with open(osp.join(load_data_path, "latest_info.json"), "r") as f:
        data_dir = (json.load(f))["latest_path"]

    rating_file_path = osp.join(load_data_path, data_dir, "rating.npy")

    # Extract the indices of Top 20 movies
    rating_mat = np.load(rating_file_path)

    if TopK > rating_mat.shape[1]:
        res = np.argsort(np.mean(rating_mat, axis=0))
    else:
        res = np.argsort(np.mean(rating_mat, axis=0))[::-1][:TopK]

    np.save(copy_data_path, res)

    print("  >> Complete copying for most_popular: {}".format(copy_data_path))
    return



def copy_data(docker_dir_path, load_data_path, copy_file_name):
    with open(osp.join(load_data_path, "latest_info.json"), "r") as f:
        data_dir = (json.load(f))["latest_path"]

    rating_csr_path = osp.join(load_data_path, data_dir, copy_file_name)
    copy_data_path = osp.join(docker_dir_path, "data_for_deployment")
    if not osp.isdir(copy_data_path):
        os.makedirs(copy_data_path, exist_ok=True)
    copy_data_path = osp.join(copy_data_path, copy_file_name)
    shutil.copyfile(src=rating_csr_path, dst=copy_data_path)

    print("  >> Successfully copying data for deployment ")
    print("  >> Go to  {}".format(copy_data_path))
    print("")

    return


def copy_trained_model(docker_dir_path, trained_model_path):
    copy_dirpath = osp.join(docker_dir_path, "trained_model")
    copy_filepath = osp.join(copy_dirpath, "dump_file")

    if not osp.isdir(copy_dirpath):
        os.makedirs(copy_dirpath, exist_ok=True)
    shutil.copyfile(trained_model_path, copy_filepath)
    print("  >> Successfully copying trained_model ")
    print("  >> Go to  {}".format(copy_filepath))
    print("")

    return


if __name__ == "__main__":
    main()


