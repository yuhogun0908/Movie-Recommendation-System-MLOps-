import unittest

from matplotlib.font_manager import json_dump
import data_quality

class DataQuality (unittest.TestCase):

    def test_check_time(self):
        # test basic functionality
        time = '2020-03-04T12:03:58'
        result = data_quality.check_time(time, int)
        self.assertEqual(result, -1)

        # check border case
        time = '2020-03-04T12:03: 58'
        result = data_quality.check_time(time, int)
        self.assertEqual(result, 0)

    def test_check_user(self):
        # test basic functionality
        userID = '33'
        result = data_quality.check_user(userID)
        self.assertEqual(result, -1)

        # check border case
        userID = '111 2'
        result = data_quality.check_user(userID)
        self.assertEqual(result, 1)

        # check border case
        userID = '111jj'
        result = data_quality.check_user(userID)
        self.assertEqual(result, 1)

    def test_check_rating(self):
        # test basic functionality
        rating = 2
        result = data_quality.check_rating(rating)
        self.assertEqual(result, -1)                

        # check border case
        rating = 'q1'
        result = data_quality.check_rating(rating)
        self.assertEqual(result, 2)

        # check border case
        rating = '6'
        result = data_quality.check_rating(rating)
        self.assertEqual(result, 2)

    def test_check_recommend(self):
        # test basic functionality
        movie_list = ['harry+potter']*20
        result = data_quality.check_recommend(movie_list)
        self.assertEqual(result, -1)

        # check border case
        movie_list = []
        result = data_quality.check_recommend(movie_list)
        self.assertEqual(result, 3)

if __name__ == '__main__':
    unittest.main()