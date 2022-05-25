#-*- coding: utf-8 -*-

import numpy as np
import sys
#sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone2/exercise/")
import os
from path.path import get_project_root
from Data_Management import Process_RawData, Process_Corpus
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    # Process Corpus - Step2-1: process_data
    parser.add_argument("--movie_threshold", type=int, default=7, help="#minimum # of ratings per movie")
    parser.add_argument("--user_threshold", type=int, default=10, help="minumum # of ratings per user")
    parser.add_argument("--user_max_threshold", type=int, default=31, help="maximum # of ratings per user")

    parser.add_argument("--process_data", action="store_true")

    # Process Corpus - Step2-3: Data Split
    parser.add_argument("--val_ratio", type=float, default=0.1)
    parser.add_argument("--test_ratio", type=float, default=0.2)


    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    corpus = Process_Corpus.Corpus(args=args)

    corpus.do_step1_process_data()

    corpus.do_step2_get_CSR_matrix()

    corpus.do_step3_data_split()

if __name__ == "__main__":
    main()
