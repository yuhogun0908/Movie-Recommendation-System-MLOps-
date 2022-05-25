#-*- coding: utf-8 -*-
# Created by ys.heo at 220327

import os, json
import os.path as osp
from path.path import get_project_root
from Data_Management.Corpus_Preprocessing import step1_process_data
from Data_Management.Corpus_Preprocessing import step2_get_CSR_matrix
from Data_Management.Corpus_Preprocessing import step3_data_split
from Data_Management.Process_RawData import Process_RawData
from datetime import datetime
import numpy as np
import shutil


class Corpus:

    def __init__(self, args):

        self.args = args
        latest_raw_data = Process_RawData.get_latest_path()
        self.raw_data_path = osp.join(osp.join(get_project_root(), "DB/RAW_DATA"), latest_raw_data)
        if not osp.isdir(self.raw_data_path):
            assert NotADirectoryError

        """
        if self.args.process_data:
            self.date_string = datetime.now().strftime('%Y%m%d_%H%M')
            self.dir_name = osp.join("DB/CORPUS", self.date_string)

        else:
            self.latest_CORPUS_path = self.get_latest_path()
            self.date_string= self.latest_CORPUS_path
            self.dir_name = osp.join("DB/CORPUS", self.latest_CORPUS_path)
        """
        
        self.date_string = datetime.now().strftime('%Y%m%d_%H%M')
        self.dir_name = osp.join("DB/CORPUS", self.date_string)

        self.output_path = osp.join(get_project_root(), self.dir_name)
        self.rating_mat_path = osp.join(self.output_path, "rating.npy")
        self.rating_mat_csr_path = osp.join(self.output_path, "rating_csr.npy")
        #self.latest_CORPUS_path = self.get_latest_path()

    def do_step1_process_data(self):
        all_data = step1_process_data.read_data(data_path=self.raw_data_path)
        ratings_dict = step1_process_data.get_ratings(args=self.args,
                                                      movie_data_list=all_data["movie"])

        user_movie_rating_dict, user_idx2id, user_id2idx, movie_idx2id, movie_id2idx = \
            step1_process_data.build_user_movie_rating_dict(args=self.args, rating_dict=ratings_dict)

        rating_matrix = step1_process_data.build_rating_matrix(user_movie_rating_dict, user_idx2id, user_id2idx,
                                                               movie_idx2id, movie_id2idx)
        step1_process_data.get_statistics(rating_matrix=rating_matrix)
        step1_process_data.save_data(self.output_path, rating_matrix, user_idx2id, user_id2idx,
                                     movie_idx2id, movie_id2idx)

        
        self.del_prev_save_dir()


        latest_file_path = self.set_latest_path()
        self.latest_CORPUS_path = latest_file_path

        print("  >> Success Step1....")


    def do_step2_get_CSR_matrix(self):
        filepath = self.rating_mat_path
        if not osp.isfile(filepath):
            assert FileNotFoundError

        save_dir_path = self.output_path
        if not osp.isdir(save_dir_path):
            assert NotADirectoryError

        step2_get_CSR_matrix.calculate_CSR(filepath = filepath,
                                           save_path = self.rating_mat_csr_path)

        print("  >> Success Step2....")

    def do_step3_data_split(self):

        step3_data_split.do_split(args = self.args,
                                  data_path = self.output_path,
                                  rating_npy_path=self.rating_mat_path)

        print("  >> Success Step3....")

    def del_prev_save_dir(self):
        cur_latest_dir = self.get_latest_path()
        #filepath = osp.join(osp.join(get_project_root(), "DB/CORPUS"), "latest_info.json")
        filepath = osp.join(osp.join(get_project_root(), "DB/CORPUS"), cur_latest_dir)
        shutil.rmtree(filepath)
        print("  >> Remove the previous CORPUS: {}".format(filepath))


    def set_latest_path(self):
        filepath = osp.join(osp.join(get_project_root(), "DB/CORPUS"), "latest_info.json")
        info = {"latest_path": self.date_string}
        with open(filepath, "w") as f:
            json.dump(info, f)

        print("  >> Complete writing the latest path in the CORPUS dir: {}".format(filepath))

        return filepath

    @staticmethod
    def get_latest_path():
        filepath = osp.join(osp.join(get_project_root(), "DB/CORPUS"),
                            "latest_info.json")

        # TODO: Unit Test
        if not osp.isfile(filepath):
            return " "

        with open(filepath, "r") as f:
            latest_info = json.load(f)

        return latest_info["latest_path"]






