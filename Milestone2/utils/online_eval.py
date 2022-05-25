# -*- coding: utf-8 -*-

from calendar import c
from lib2to3.pgen2.token import DEDENT
import os
import json
from xmlrpc.client import boolean
import numpy as np
from datetime import datetime
from pathlib import Path
import argparse
from json.decoder import JSONDecodeError

import arrow
from splitio import get_factory
from splitio.exceptions import TimeoutException
import sys

# B scheme

def readJson(path):
    flag_ = False
    while not flag_:
        try:
            file = open(path)
            json_data = json.load(file)
        except json.decoder.JSONDecodeError: 
            pass
        else:
            flag_ = True
    # json_data = json.load(file)
    file.close()
    return json_data

def emptyJson(args):
    requestPath = os.path.join(args.request_dir, 'request.json')
    assert(os.path.exists(requestPath))
    with open(requestPath, 'w') as write_file:
        json.dump({}, write_file, ensure_ascii=False, indent = '\t')
        write_file.close() 

def deleteJson(args):
    requestPath = os.path.join(args.request_dir, 'request.json')
    assert(os.path.exists(requestPath))
    if os.path.exists(requestPath):
        os.remove(requestPath)

def writeJson(RootDir, fileInfo):
    with open(RootDir, 'w') as write_file:
        json.dump(fileInfo, write_file, ensure_ascii=False, indent = '\t')
    write_file.close() 
    return

def get_requesting_userid_lst(args):

    num = args.num_test
    # load recommend data

    requestPath = os.path.join(args.request_dir, 'request.json')
    assert(os.path.exists(requestPath))
    print('start to readJson')
    request_data = readJson(requestPath)
    print('success to readJson')
    # # get recommeneded times from recommend Query
    # latest
    # recommend_time_lst = list(request_data["timeQuery"].keys())[-num:]

    # # get requested users from recommend Query
    # user_id_lst = list(request_data["timeQuery"].values())[-num:]

    # earliest
    # get recommeneded times from recommend Query
    recommend_time_lst = list(request_data["timeQuery"].keys())[:num]

    # get requested users from recommend Query
    user_id_lst = list(request_data["timeQuery"].values())[:num]

    return user_id_lst, recommend_time_lst

def get_movies_from_request(args, userID):

    # load recommend data
    requestPath = os.path.join(args.request_dir, 'request.json')
    assert(os.path.exists(requestPath))
    request_data = readJson(requestPath) 

    # get recommeneded movie list from recommend Query
    try:
        movies_recommended_lst = request_data["movieQuery"][userID]
    except KeyError:
        movies_recommended_lst = []

    return movies_recommended_lst

def get_telemetry_from_user(args, userID, rec_time):

    # load telemetry data
    userJsonDir = os.path.join(args.telem_dir, 'user')
    userPath = os.path.join(userJsonDir, str(userID)+'.json')

    if os.path.exists(userPath):
        user_data = readJson(userPath)    

        # get movie indices which is watched after recommeded time 
        mov_idx = 0
        recommeded_time = datetime.strptime(str(rec_time.split('.')[0]), '%Y-%m-%dT%H:%M:%S')
        watched_time = datetime.strptime(str(list(user_data["movieList"].values())[mov_idx]["time"]), '%Y-%m-%dT%H:%M:%S')
        
        #print('searching data for user {} '.format(userID))
        while recommeded_time > watched_time:
            try:
                watched_time = datetime.strptime(str(list(user_data["movieList"].values())[mov_idx+1]["time"]), '%Y-%m-%dT%H:%M:%S')
                mov_idx += 1
            except IndexError:
                break
        
        #print('search complete')

        # get telemetry data which is watched after recommeded time 
        movie_id_lst = []
        rating_lst = []
        for mov_idx in range(len(user_data["movieList"].keys())):
            movie_id_lst.append(list(user_data["movieList"].keys())[mov_idx])
            rating_lst.append(list(user_data["movieList"].values())[mov_idx]["rating"])

    # there is no user data
    else:
        movie_id_lst = []
        rating_lst = []
        #print("There is no user {} data in directory".format(userID))
        print("user {} has not yet watched any movie.".format(userID))
    
    return movie_id_lst, rating_lst

def evaluation_1(movies_recommended_lst, movie_id_lst):

    total_count = 0
    empty_flag = 0

    # when the user hasn't yet seen any movies
    if len(movie_id_lst) == 0:
         empty_flag = 1

    # counts how many recommended movie the user has watched
    else:
        for tmp in range(len(movie_id_lst)):
            if movie_id_lst[tmp] in movies_recommended_lst:
                total_count += 1
    
    return total_count, empty_flag

def evaluation_2(movies_recommended_lst, movie_id_lst, rating_lst):

    total_count = 0
    empty_flag = 0
    if len(movie_id_lst) == 0:
         empty_flag = 1
    else:
        for tmp in range(len(movie_id_lst)):
            if movie_id_lst[tmp] in movies_recommended_lst:
                if args.metric == 0:
                    total_count += 1
                elif args.metric == 1:
                    total_count += 1 * rating_lst[tmp]

    return total_count, empty_flag

def run(args):

    # run split
    factory = get_factory('cgaj8soepi94hme6sdl07pf83kpkud4o42h3')
    try:
        factory.block_until_ready(5)
    except TimeoutException:
        # The SDK failed to initialize in 5 seconds. Abort!
        sys.exit()
    split = factory.client()

    # initailization
    num_test_samples = args.num_test
    
    # get user_ids requesting recommendation
    user_id_lst, recommend_time_lst = get_requesting_userid_lst(args)
    assert(len(user_id_lst) != 0 and len(recommend_time_lst) != 0)

    cnt = 0
    empty_cnt = 0
    # recommend movies to the users
    if args.metric == 0:
        print('metric 1 is on')
    elif args.metric == 1:
        print('metric 2 is on')
    for n in range(num_test_samples):
        #print(n)
        movies_recommended_lst = get_movies_from_request(args, user_id_lst[n])
        if len(movies_recommended_lst) == 0:
            print("Recommended list of user {} doen't exist.".format(user_id_lst[n]))
            empty_cnt += 1
    # check which movie the user is watching 
        movie_id_lst, rating_lst = get_telemetry_from_user(args, user_id_lst[n], recommend_time_lst[n])

    # evaluate conversion rate

        if args.metric == 0:
            c, e = evaluation_1(movies_recommended_lst, movie_id_lst)                          # metric 1: on / off
            track_event = split.track(user_id_lst[n],"user","conversion",c)
            print('track_event',track_event)
            cnt += c
            empty_cnt += e
        elif args.metric == 1:
            c, e = evaluation_2(movies_recommended_lst, movie_id_lst, rating_lst)              # metric 2: on / off + rate
            track_event = split.track(user_id_lst[n],"user","conversion",c)
            print('track_event',track_event)
            cnt += c
            empty_cnt += e     

    assert(num_test_samples != empty_cnt)
    conversion_rate = cnt / (num_test_samples - empty_cnt) * 100
    print("The number of data set actually used is: ",(num_test_samples - empty_cnt))
    print('Average conversion rate is :',conversion_rate)    

    # save result to log data
    time_info = datetime.now()
    tmp_dict = {"time":str(time_info),"result":conversion_rate}
    if os.path.isfile(args.results_dir):
        resultsJsonInfo = readJson(args.results_dir)
        resultsJsonInfo['OnlineQuery'].append(tmp_dict) 
       
    else:
        resultsJsonInfo = {}
        resultsJsonInfo['OnlineQuery'] = [tmp_dict]

    
    writeJson(args.results_dir, resultsJsonInfo)

    # empty json file if reset flag is on
    if args.reset_json:
        # emptyJson(args)
        deleteJson(args)

    factory.destroy()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--telem_dir', type = str, default = "/home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/", help = 'Telemetry data directory')
    parser.add_argument('--request_dir', type = str, default = "/home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/", help = 'request.json directory')
    parser.add_argument('--results_dir', type = str, default = "/home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/results_online.json", help = 'online_results.json directory')
    parser.add_argument('--num_test', type = int, default = 1000, help = "The num of test samples")
    parser.add_argument('--reset_json', type = boolean, default = False, help = "Flag whether or not to empty the json file")
    parser.add_argument('--metric', type = int, default = 0, help = "0: conversion rate, 1: conversion rate * rating")
    args = parser.parse_args()

    run(args)