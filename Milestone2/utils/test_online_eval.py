import unittest
import online_eval
import sys
from xmlrpc.client import boolean
import argparse
import random
import online_eval

class TestOnlineEval (unittest.TestCase):

    def test_args(self):
        print('telem_dir:', args.telem_dir)
        print('request_dir:', args.request_dir)
        print('num_test:', args.num_test)
        print('reset_json:', args.reset_json)

    def test_get_req_lst(self):

        u_lst, t_lst = online_eval.get_requesting_userid_lst(args)
        self.assertEqual(len(u_lst), args.num_test)
        self.assertEqual(len(t_lst), args.num_test)

    def test_get_recom_lst(self):

        # u_id = random.randint(0,args.num_test)
        u_id = "617995"
        u_id = "400163"
        rec_lst = online_eval.get_movies_from_request(args, u_id)
        self.assertIn(len(rec_lst), [0,20])

    def test_get_tele(self):

        u_id = "617995"
        u_id = "400163"
        rec_time = "2022-03-31T02:31:30.261246"
        m_lst, r_lst = online_eval.get_telemetry_from_user(args, u_id, rec_time)
        self.assertIsNotNone(m_lst)
        self.assertIsNotNone(r_lst)

    def test_cal(self):

        rec_lst = [
         "moive_name","moive_name","moive_name","moive_name",
            "moive_name","moive_name","moive_name","moive_name",
            "moive_name","moive_name","moive_name","moive_name",
            "moive_name","moive_name","moive_name","moive_name",
            "moive_name","moive_name","moive_name","moive_name"
      ]
        m_lst = [
            "moive_name_a"
        ]
        c, e = online_eval.evaluation_1(rec_lst, m_lst)
        self.assertNotEqual(e, args.num_test)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--telem_dir', type = str, default = "/home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/", help = 'Telemetry data directory')
    parser.add_argument('--request_dir', type = str, default = "/home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/", help = 'request.json directory')
    parser.add_argument('--results_dir', type = str, default = "/home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/results.json", help = 'online_results.json directory')
    parser.add_argument('--num_test', type = int, default = 100, help = "The num of test samples")
    parser.add_argument('--reset_json', type = boolean, default = False, help = "Flag whether or not to empty the json file")
    parser.add_argument('--metric', type = int, default = 0, help = "0: conversion rate, 1: conversion rate * rating")
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()

    sys.argv[1:] = args.unittest_args
    unittest.main()  