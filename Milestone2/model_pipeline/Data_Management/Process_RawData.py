#-*- coding: utf-8 -*-
# Created by ys.heo at 220327

from datetime import datetime
import os, json
import os.path as osp
from path.path import get_project_root
from distutils.dir_util import copy_tree
import shutil

class Process_RawData:
    def __init__(self, kafka_dir_path):
        """
        :param kafka_dir_path: a kafka dir path to be stored
        """
        # TODO: UNIT TEST for Checking Directory Path
        if not osp.isdir(kafka_dir_path):
            assert NotADirectoryError

        self.data_path = kafka_dir_path
        self.date_string = datetime.now().strftime('%Y%m%d_%H%M')
        self.dir_name = osp.join("DB/RAW_DATA", self.date_string)
        self.output_path = osp.join(get_project_root(), self.dir_name)

        if not osp.exists(self.output_path):
            os.makedirs(name=self.output_path, exist_ok=True)

    def data_save(self):
        #shutil.copy2(src=self.data_path, dst=self.output_path)
        print("  >> Copy kafka dataset... Wait")
        copy_tree(src=self.data_path, dst=self.output_path)
        print("  >> Complete saving kafka data to {}".format(self.dir_name))

        #save_path = self.set_latest_path()
        #return save_path

    def del_prev_save_dir(self):
        cur_latest_dir = self.get_latest_path()
        #print("  @@@@@ 181818 cur_latest_dir: {}".format(cur_latest_dir))
        filepath = osp.join(osp.join(get_project_root(), "DB/RAW_DATA"), cur_latest_dir)
        print(" >> Deleted save dir path: {}".format(filepath))
        shutil.rmtree(filepath)
        print("  >> Remove the previous RAWDATA: {}".format(filepath))


    def set_latest_path(self):
        filepath = osp.join(osp.join(get_project_root(), "DB/RAW_DATA"), "latest_info.json")
        info = {"latest_path": self.date_string}
        with open(filepath, "w") as f:
            json.dump(info, f)

        print("  >> Complete recording the latest path in RAW_DATA: {}".format(filepath))

        return filepath

    @staticmethod
    def get_latest_path():
        filepath = osp.join(osp.join(get_project_root(), "DB/RAW_DATA"), "latest_info.json")
        # TODO: Unit Test
        if not osp.isfile(filepath):
            assert FileNotFoundError

        with open(filepath, "r") as f:
            latest_info = json.load(f)

        return latest_info["latest_path"]

