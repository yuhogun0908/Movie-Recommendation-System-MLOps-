import sys
sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone2/exercise/")

import unittest
import os
from Data_Management import Process_RawData

class FetchDataset(unittest.TestCase):
    def test_main(self):
        # Step1 only copies data from kafka_dir_path to output_path. Thus, there's nothing much to test.
        kafka_dir_path = '/home/daink/Development/tmp_data'
        RawData = Process_RawData.Process_RawData(kafka_dir_path= kafka_dir_path)
        self.assertEqual(RawData.data_path, kafka_dir_path)

        # test if output path is file
        self.assertEqual(os.path.isdir(RawData.output_path), True)

if __name__ == '__main__':

    unittest.main()

