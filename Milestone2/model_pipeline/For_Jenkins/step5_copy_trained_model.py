#-*- coding: utf-8 -*-
# Created by YoonseokHeo at 220330



import sys, json, argparse
sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone2/exercise/")

import os, shutil
import os.path as osp
from path.path import get_project_root

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trained_model_dir_path", type=str,
                        default="RecSys_Management/model/save", 
                        help = "a directory path to the latest trained model")
    parser.add_argument("--copy_path", type=str,
                        default="../Pipeline/Flask/trained_MF/model_update",
                        help="a  directory path to the master branch")

    parser.add_argument("--update_flag_path", type=str,
                        default="../Pipeline/Flask/trained_MF",
                        help="An directory path to the master branch")

    args = parser.parse_args()

    return args

def main():
    args = parse_args()

    save_dir_path = osp.join(get_project_root(), args.trained_model_dir_path)
    with open(osp.join(save_dir_path, "latest_info.json")) as f:
        dir_name = json.load(f)["latest_path"]

    trained_model_path = osp.join(osp.join(save_dir_path, dir_name), "dump_file")
    print(" >> Trained_model_path: {}".format(trained_model_path))

    copy_filepath = osp.join(osp.join(get_project_root(), args.copy_path),
                             "dump.file")

    if not osp.isdir(osp.join(get_project_root(), args.copy_path)):
        os.makedirs(osp.join(get_project_root(), args.copy_path), exist_ok=True)
    shutil.copyfile(trained_model_path, copy_filepath)

    print("  >> Successfully copying... ")
    print("  >> Go to  {}".format(copy_filepath))
    print("")

    if not osp.isdir(osp.join(get_project_root(), args.update_flag_path)):
        os.makedirs(osp.join(get_project_root(), args.update_flag_path), exist_ok=True)
    update_filepath = osp.join(osp.join(get_project_root(), args.update_flag_path), 
                               "update_flag.json")

    with open(update_filepath, "w") as f:
        json.dump({"model_update": 1}, f)

    print("  >> Successfully update the flag...")
    print("  >> Go to   {}".format(update_filepath))



    


if __name__ == "__main__":
    main()


