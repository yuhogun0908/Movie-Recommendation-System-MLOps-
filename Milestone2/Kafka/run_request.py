from ast import Continue
from kafka import KafkaConsumer
from json import loads
from request import http_request
import json
import os
from pathlib import Path
import argparse
# import pdb; pdb.set_trace()
import sys
# sys.path.insert(0,'..')
# from utils.data_quality import data_quality


# import numpy as np

from datetime import datetime

def check_time(time,data_type):
    try:
        time_input = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
        if time_input.year != 4:
            return -1
    except:
        return 0
    
    return -1

      
def check_user(userID):
    try:
        status=-1 if type(int(userID))==int else 1
        return status
    except:
        status = 1
        return status
    
def check_rating(rating):
    try:
        status=-1 if type(int(rating))==int and int(rating) <= 5 else 2
        return status
    except:
        status = 2
        return status
    
def check_recommend(movie_list):
    try :
        status=-1 if len(movie_list) == 20 else 3
        return status
    except:
        status = 3
        return status

def data_quality(mode,messageValue=None,jsonInfo=None,key=None):
    
    """
    Args:
        messageValue (str): Kafka streaming data info.
        mode (int): data quality check
            0: Check schema error
            1: Data Loss Check
            2: Data duplication check

    Raises:
        status (int): data state
            -1 : normal state
             0 : time format error
             1 : user format error
             2 : rating format error
             3 : recomment format error
             4 : unkwon error
             5 : missing format error
             6 : duplicated data  
    """
    
    error = {0:'The time format of the data is incorrect',
             1:'The user format of the data is incorrect',
             2:'The rating format of the data is incorrect',
             3:'The recommend format of the data is incorrect',
             4:'The unknown format of the data is incorrect',
             5:'Some format of the data have been lost',
             6:'The data is duplicated'}
    
    # consider #1 
    #  <time>,<userid>,recommendation request <server>,status <200 for success>, result: <responsetime>
    # ex
    # '2022-03-28T21:17:58.209926,3230,recommendation request 17645-team24.isri.cmu.edu:8082, status 200, result: {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, {movie_name}, 113 ms'
    
    # consider #2 
    #  <time>,<userid>,GET /data/m/<movieid>/<minute>.mpg
    # ex
    # '2022-03-18T06:12:47,326332,GET /data/m/ghostbusters+1984/54.mpg'
    
    # consider #3 
    #  <time>,<userid>,GET /rate/<movieid>=<rating>
    # ex
    # '2022-03-18T05:53:29,162591,GET /rate/the+incredibles+2004=4'
    # '2022-03-28T04:00: 44,45314,GET /rate/my+left+foot+the+story+of+christy+brown+1989=4'
    

    status = -1
    if mode == 0:
        try:
            if 'recommendation' in messageValue:
                time = messageValue.split(',')[0]
                # time check
                time = time.split('.')[0]
                status = check_time(time, 0)
                # if status == 0:
                    
                if status == -1:
                    try:
                        userID = messageValue.split(',')[1]
                        status = check_user(userID)
                    except:
                        status = 1
                if status == -1:
                    try:
                        movie_list = messageValue.split('result: ')[1].split(', ')[0:20]
                        status = check_recommend(movie_list)
                    except:
                        status = 3
                    
                    
            elif 'GET' in messageValue:
                MovieInfo =  messageValue.split(',')[-1]
                # time check
                time = messageValue.split(',')[0]
                status = check_time(time,1) if '/data/m' in MovieInfo else data_quality(time,2) 
                if status == -1:
                    try:
                        userID = messageValue.split(',')[1]
                        status = check_user(userID)
                    except:
                        status = 1
                if status == -1 and '/rate/' in MovieInfo:
                    try: 
                        rating = messageValue.split('=')[-1]
                        status = check_rating(rating)
                    except:
                        status = 2
        except:
            status = 4
    
    elif mode == 1:
        try:
            if 'recommendation' in messageValue:
                if len(messageValue.split(',')) != 25:
                    # import pdb; pdb.set_trace()
                    status = 5
            elif 'GET' in messageValue:
                if len(messageValue.split(',')) != 3:
                    # import pdb; pdb.set_trace()
                    status = 5
        except:
            status = 4
    
    elif mode == 2:
        # check the data is duplicated
            if key[0] not in jsonInfo.keys():
                jsonInfo[key[0]] = {key[1] : key[2]}
            
            elif key[1] not in jsonInfo[key[0]].keys():
                jsonInfo[key[0]].update({key[1] : key[2]})
            
            else:
                status = 6
        

        # if keyName in jsonDict.keys():
        #     status = 6
            
    if status != -1:
        print(error[status])
        # update logger # TODO


    # 2. Duplicated data
    
    
    #3. Missing Data
        # 형식이 안맞는 애들 -> 통으로 없는 경우 --> 제거
    
    if mode == 2: return status, jsonInfo
    else: return status

    # return status


"""
Kafka data streaming
    
    provided data :    
        #1. <time>,<userid>,recommendation request <server>,status <200 for success>, result: <responsetime>
        #2. <time>,<userid>,GET /data/m/<movieid>/<minute>.mpg
        #3. <time>,<userid>,GET /rate/<movieid>=<rating>
    
    arguments : save directory

"""

def write_Json(RootDir, fileInfo):
    with open(RootDir, 'w') as write_file:
        json.dump(fileInfo, write_file, ensure_ascii=False, indent = '\t')
    write_file.close() 
    return

def read_Json(RootDir):
    with open(RootDir, 'r') as read_file:
        movieJsonInfo = json.load(read_file)
    read_file.close()
    return movieJsonInfo

def run(args):
    Path.mkdir(Path(args.save_dir), exist_ok=True)
    # Create a consumer to read data from kafka
    offset_reset = 'latest' 
    consumer = KafkaConsumer(
        'movielog24',
        bootstrap_servers=['localhost:9092'],
        #bootstrap_servers=['localhost'],
        # Read from the start of the topic; Default is latest
        auto_offset_reset= offset_reset
    )

    # Prints all messages, again and again!
    requestDir = os.path.join(args.save_dir, 'request.json')
    userJsonDir = os.path.join(args.save_dir, 'user')
    movieJsonDir = os.path.join(args.save_dir, 'movie')
    for idx, message in enumerate(consumer):
        # print(message)
        # Default message.value type is bytes!
        messageValue = message.value.decode('utf-8')
        # print(messageValue)
        status_1 = data_quality(0,messageValue=messageValue,jsonInfo=None,key=None)
        status_2 = data_quality(1,messageValue=messageValue,jsonInfo=None,key=None)
        # status_1 = -1
        # status_2 = -1
        if status_1 == -1 and status_2 == -1:

            if args.save_request:
                # consider # 1 data
                if 'recommendation' in messageValue:
                    print(message)
                    # import pdb;pdb.set_trace()
        
                    userID = str(messageValue.split(',')[1])
                    time_info = messageValue.split(',')[0]
                    print(messageValue) 
                    if 'status 200' in messageValue:
                        #print(messageValue)
                        movies = messageValue.split('result: ')[1].split(', ')[0:20]
                        if not os.path.isfile(requestDir):
                            requestJsonInfo = {}
                            # requestJsonInfo['timeQuery'] = {str(time_info) : [userID] }
                            requestJsonInfo['timeQuery'] = {str(time_info) : userID }
                            requestJsonInfo['movieQuery'] = {str(userID) : movies}
                            
                        else:
                            requestJsonInfo = read_Json(requestDir)
                            # if str(time_info) in requestJsonInfo['timeQuery'].keys():
                                # requestJsonInfo['timeQuery'][str(time_info)].extend([userID])
                            requestJsonInfo['timeQuery'].update({str(time_info) : userID})    
                            requestJsonInfo['movieQuery'].update({str(userID) : movies})
                        
                        write_Json(requestDir, requestJsonInfo)


            elif 'GET' in messageValue:
                # import pdb; pdb.set_trace()
                userID = messageValue.split(',')[1]
                userPath = os.path.join(userJsonDir, str(userID)+'.json')
                MovieInfo =  messageValue.split(',')[-1]
                time_info = messageValue.split(',')[0]
                
                if '/data/m/' in MovieInfo:                
                    # consider #2 data
                    
                    movieID = MovieInfo.split('/')[-2]
                    userQuery = http_request('user', str(userID))

                    if args.save_movie:
                        
                        ####################   movie  ####################
                        movieQuery = http_request('movie', str(movieID))
                        moviePath = os.path.join(movieJsonDir,str(movieID)+'.json')
                        if os.path.isfile(moviePath):
                            # add userId & userQuery to movie.json
                            
                            movieJsonInfo = read_Json(moviePath)
                            
                            # if 'userList' not in movieJsonInfo.keys():
                            #     movieJsonInfo["userList"] = {str(userID) : userQuery}
                            # # if userID not in movieJsonInfo['userList']:
                            # movieJsonInfo["userList"].update({str(userID) : userQuery})
                            status_3, movieJsonInfo = data_quality(2,messageValue=None,jsonInfo=movieJsonInfo,key=['userList',str(userID),userQuery])
                            
                            if status_3 == -1:
                                write_Json(moviePath, movieJsonInfo)

                        else:
                            Path.mkdir(Path(movieJsonDir), exist_ok=True)
                            movieJsonInfo = {}
                            movieJsonInfo["movieQuery"] = movieQuery
                            movieJsonInfo["userList"] = {str(userID) : userQuery}
                            write_Json(moviePath, movieJsonInfo)
            
                        
                        
                    ####################   user   ####################
                    if args.save_user:
                        if os.path.isfile(userPath):
                            userJsonInfo = read_Json(userPath)
                            
                            # if str(movieID) not in userJsonInfo['movieList'].keys():
                            #     userJsonInfo["movieList"].update({str(movieID):{"rating" : "0", str('time'):str(time_info)}})
                            #     write_Json(userPath, userJsonInfo)
                            
                            status_3, userJsonInfo = data_quality(2,messageValue=None,jsonInfo=userJsonInfo,key=['movieList',str(movieID), {"rating" : "0", str('time'):str(time_info)}])
                            if status_3 == -1:
                                write_Json(userPath, userJsonInfo)
  
                        else:
                            Path.mkdir(Path(userJsonDir), exist_ok=True)
                            userJsonInfo = {}
                            userJsonInfo["userQuery"] = userQuery
                            userJsonInfo["movieList"] = {str(movieID): {"rating" : "0", str('time'):time_info}}
                            write_Json(userPath, userJsonInfo)

                else: 
                    # consider #3 data
                    print(messageValue)
                    # import pdb; pdb.set_trace()

                    movieID = MovieInfo.split('/')[-1].split('=')[0]
                    rating = MovieInfo.split('/')[-1].split('=')[-1]
                    
                    ####################    movie   ####################
                    if args.save_movie:
                        movieQuery = http_request('movie', str(movieID))
                        moviePath = os.path.join(movieJsonDir,str(movieID)+'.json')
                        if os.path.isfile(moviePath):
                            # add userID & rating to movie.json
                            movieJsonInfo = read_Json(moviePath)
                            
                            # if "ratingUserList" not in movieJsonInfo.keys():
                            #     movieJsonInfo["ratingUserList"]= {str(userID) : str(rating)}    
                            # # if userID not in movieJsonInfo['ratingUserList']:
                            # movieJsonInfo["ratingUserList"].update({str(userID) : str(rating)})
                            
                            status_3, movieJsonInfo = data_quality(2,messageValue=None,jsonInfo=movieJsonInfo,key=['ratingUserList',str(userID),str(rating)])
                            if status_3 == -1:
                                write_Json(moviePath, movieJsonInfo)
                            
                        else:
                            Path.mkdir(Path(movieJsonDir), exist_ok=True)
                            movieJsonInfo = {}
                            movieJsonInfo["movieQuery"] = movieQuery
                            movieJsonInfo["ratingUserList"] = {str(userID) : str(rating)}
                            write_Json(moviePath, movieJsonInfo)
                    
                    
                    ####################   user   ####################
                    if args.save_user:
                        userQuery = http_request('user', str(userID))
                        
                        if os.path.isfile(userPath):
                            userJsonInfo = read_Json(userPath)
                            
                            # if str(movieID) not in userJsonInfo['movieList'].keys():
                            #     userJsonInfo["movieList"].update({str(movieID):{"rating" : rating, str('time'):str(time_info)}})
                            #     write_Json(userPath, userJsonInfo)
  
                            status_3, userJsonInfo = data_quality(2,messageValue=None,jsonInfo=userJsonInfo,key=['movieList',str(movieID), {"rating" : rating, str('time'):str(time_info)}])
                            if status_3 == -1:
                                write_Json(userPath, userJsonInfo)
    
                            if int(userJsonInfo['movieList'][str(movieID)]["rating"]) == 0:
                                print("rating {} ==> {}".format(userJsonInfo['movieList'][str(movieID)]["rating"], rating))
                                userJsonInfo['movieList'][str(movieID)]["rating"] = rating
                                write_Json(userPath, userJsonInfo)
                                
                        else:
                            Path.mkdir(Path(userJsonDir), exist_ok=True)
                            userJsonInfo = {}
                            userJsonInfo["userQuery"] = userQuery
                            userJsonInfo["movieList"] = {str(movieID): {"rating" : rating, str('time'): time_info}}
                            write_Json(userPath, userJsonInfo)
        else:
            Continue
            

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--save_dir', type = str, default = "./data/", help = 'Save directory')
    parser.add_argument('-m', '--save_movie', type = int, default=False , help= 'If want to save {movieID}.csv, True')
    parser.add_argument('-u', '--save_user', type = int, default=False, help= 'If want to save {userID},csvm True')
    parser.add_argument('-r', '--save_request', type=int, default=True, help= 'If want to save {request},csvm True')
    
    args = parser.parse_args()
    
    run(args)
    ##
