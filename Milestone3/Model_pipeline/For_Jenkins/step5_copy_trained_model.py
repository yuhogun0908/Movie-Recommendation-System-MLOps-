#-*- coding: utf-8 -*-
# Created by YoonseokHeo at 220330



import sys, json, argparse
#sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone3/")

import os, shutil
import os.path as osp
from path.path import get_project_root

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

    copy_dirpath = osp.join(get_project_root(), args.copy_path, docker_model_dir_name, "trained_model")
    copy_filepath = osp.join(copy_dirpath, "dump.file")

    if not osp.isdir(copy_dirpath):
        os.makedirs(copy_dirpath, exist_ok=True)
    shutil.copyfile(trained_model_path, copy_filepath)

    print("  >> Successfully copying... ")
    print("  >> Go to  {}".format(copy_filepath))
    print("")


if __name__ == "__main__":
    main()


