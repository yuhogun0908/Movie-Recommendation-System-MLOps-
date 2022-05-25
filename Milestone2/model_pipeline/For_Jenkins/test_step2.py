mport numpy as np
import sys
sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone2/exercise/")
import os, json
import os.path as osp
import unittest
from path.path import get_project_root
from Data_Management import Process_RawData, Process_Corpus
from Data_Management.Corpus_Preprocessing import step1_process_data
from Data_Management.Corpus_Preprocessing import step2_get_CSR_matrix
from Data_Management.Corpus_Preprocessing import step3_data_split
import argparse

class BuildCorpus(unittest.TestCase):
    def __init__(self, args):
        self.corpus = Process_Corpus.Corpus(args=args)
        self.raw_data_path = self.corpus.raw_data_path
        self.output_path = self.corpus.output_path
    def test_Corpus(self):
        # test if input and output path is dir
        self.assertEqual(os.path.isdir(self.raw_data_path), True)
        self.assertEqual(os.path.isdir(self.output_path), True)

        # test if file exists -> 존재해야하는거 맞는지 확인하기.
        self.assertEqual(os.path.exists(self.corpus.rating_mat_path), True)
        self.assertEqual(os.path.exists(self.corpus.rating_mat_csr_path), True)

    def test_do_step1_process_data(self):
        # get output of function
        all_data = step1_process_data.read_data(data_path=self.raw_data_path)
        ratings_dict = step1_process_data.get_ratings(args=args, movie_data_list=all_data["movie"])
        user_movie_rating_dict, user_idx2id, user_id2idx, movie_idx2id, movie_id2idx = \
            step1_process_data.build_user_movie_rating_dict(args=args, rating_dict=ratings_dict)

        rating_matrix = step1_process_data.build_rating_matrix(user_movie_rating_dict, user_idx2id, user_id2idx,
                                                               movie_idx2id, movie_id2idx)
        step1_process_data.get_statistics(rating_matrix=rating_matrix)
        step1_process_data.save_data(self.output_path, rating_matrix, user_idx2id, user_id2idx,
                                     movie_idx2id, movie_id2idx)

        latest_file_path = self.set_latest_path()
        self.latest_CORPUS_path = latest_file_path

        # test if output is eqaul to the desired output.



    def test_do_step2_get_CSR_matrix(self):
        a = 1
    def test_do_step3_data_split(self):
        a = 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Process Corpus - Step2-1: process_data
    parser.add_argument("--movie_threshold", type=int, default=7, help="#minimum # of ratings per movie")
    parser.add_argument("--user_threshold", type=int, default=10, help="minumum # of ratings per user")
    parser.add_argument("--user_max_threshold", type=int, default=31, help="maximum # of ratings per user")

    parser.add_argument("--process_data", action="store_true")

    # Process Corpus - Step2-3: Data Split
    parser.add_argument("--val_ratio", type=float, default=0.1)
    parser.add_argument("--test_ratio", type=float, default=0.2)

    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()
    sys.argv[1:] = args.unittest_args
    unittest.main()