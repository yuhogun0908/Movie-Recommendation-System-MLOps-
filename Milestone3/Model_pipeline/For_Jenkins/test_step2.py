import numpy as np
import sys
#sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone2/exercise/")
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
        super(BuildCorpus, self).__init__(args)
        corpus = Process_Corpus.Corpus(args=args)
        # set input variable, raw_data_path and output_path, for unit test
        if not os.path.exists(os.path.join(get_project_root(), "DB/RAW_DATA/unittest")):
            os.makedirs(name=os.path.join(get_project_root(), "DB/RAW_DATA/unittest"), exist_ok = True)
        corpus.raw_data_path = osp.join(get_project_root(), "DB/RAW_DATA/unittest")
        corpus.output_path = osp.join(get_project_root(), "DB/CORPUS/unittest")
        self.raw_data_path = corpus.raw_data_path
        self.output_path = corpus.output_path

        corpus.rating_mat_path = osp.join(self.output_path, "rating.npy")
        corpus.rating_mat_csr_path = osp.join(self.output_path, "rating_csr.npy")
        self.rating_mat_path = corpus.rating_mat_path
        self.rating_mat_csr_path = corpus.rating_mat_csr_path

    def test_path(self):
        # test if all path is valid
        self.assertEqual(os.path.isdir(self.raw_data_path), True)
        self.assertEqual(os.path.isdir(self.output_path), True)
        self.assertEqual(os.path.isfile(self.rating_mat_path), True)
        self.assertEqual(os.path.isfile(self.rating_mat_csr_path), True)

    def test_do_step1_process_data(self):
        # get output of function
        all_data = step1_process_data.read_data(data_path=self.raw_data_path)
        # test if the output returns a dictionary with user and movie.
        self.assertIsInstance(all_data, dict)
        self.assertIn('movie', all_data.keys())
        self.assertIn('user', all_data.keys())

        # get output of function
        ratings_dict = step1_process_data.get_ratings(args=args, movie_data_list=all_data["movie"])
        # test if the output returns a dictionary.
        self.assertIsInstance(ratings_dict, dict)

        # get output of function
        user_movie_rating_dict, user_idx2id, user_id2idx, movie_idx2id, movie_id2idx = \
            step1_process_data.build_user_movie_rating_dict(args=args, rating_dict=ratings_dict)
        # test if the output returns a dictionary.
        self.assertIsInstance(user_movie_rating_dict, dict)
        self.assertEqual(len(user_id2idx), len(user_idx2id))
        self.assertEqual(len(movie_id2idx), len(movie_idx2id))
        
        # get output of function
        rating_matrix = step1_process_data.build_rating_matrix(user_movie_rating_dict, user_idx2id, user_id2idx,                                                                movie_idx2id, movie_id2idx)
        #test if the output returns a numpy array with float
        self.assertIsInstance(rating_matrix, np.ndarray)
        self.assertIs(rating_matrix.dtype.type, np.float64)
        #test if the dimension of the output matrix matches to desired value.
        self.assertEqual(rating_matrix.shape, (len(user_idx2id), len(movie_idx2id)))
        #test if the rating matrix has atleast one nonzero entries.        
        self.assertGreater(np.count_nonzero(rating_matrix), 0)

    def test_do_step2_get_CSR_matrix(self):
        # get output of function
        data_2d_idx = step2_get_CSR_matrix.calculate_CSR(filepath = self.rating_mat_path,
                                           save_path = self.rating_mat_csr_path, unit_test=True)
        # test if the output is right format
        self.assertIsInstance(data_2d_idx, np.ndarray)
        self.assertGreater(len(data_2d_idx), 0)
        self.assertTrue(all(len(elem) == 3 for elem in data_2d_idx))
        self.assertTrue(all(elem.dtype.type == np.float64 for elem in data_2d_idx))
    
    def test_do_step3_data_split(self):
        # set input for unit test
        rating_mat = np.load(self.rating_mat_path)
        num_cols = np.shape(rating_mat)[1]
        test_ratio, val_ratio = 0.2, 0.1
        # get output of function
        train_data_2d_idx, valid_data_2d_idx, test_data_2d_idx, splited_rating_matrix = step3_data_split.train_valid_test_split(rating_mat, num_cols, test_ratio, val_ratio)
        self.assertIsInstance(train_data_2d_idx, list)
        self.assertGreater(len(train_data_2d_idx), 0)
        self.assertTrue(all(len(elem) == 3 for elem in train_data_2d_idx))

        self.assertIsInstance(valid_data_2d_idx, list)
        self.assertGreater(len(valid_data_2d_idx), 0)
        self.assertTrue(all(len(elem) == 3 for elem in valid_data_2d_idx))

        self.assertIsInstance(test_data_2d_idx, list)
        self.assertGreater(len(test_data_2d_idx), 0)
        self.assertTrue(all(len(elem) == 3 for elem in test_data_2d_idx))

        self.assertIsInstance(splited_rating_matrix, np.ndarray)
        self.assertTrue(len(train_data_2d_idx), np.count_nonzero(splited_rating_matrix))
        
        # generate data for test_step3
        #step3_data_split.do_split(args, self.output_path, self.rating_mat_path)

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
