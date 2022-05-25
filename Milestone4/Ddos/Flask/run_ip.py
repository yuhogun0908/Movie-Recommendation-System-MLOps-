from ast import Continue
from kafka import KafkaConsumer, KafkaProducer
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
import pdb
import json

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

"""
def delete_old_files(path_target, days_elapsed):
    """path_target:삭제할 파일이 있는 디렉토리, days_elapsed:경과일수"""
    for f in os.listdir(path_target): # 디렉토리를 조회한다
        f = os.path.join(path_target, f)
        if os.path.isfile(f): # 파일이면
            timestamp_now = datetime.now().timestamp() # 타임스탬프(단위:초)
            # st_mtime(마지막으로 수정된 시간)기준 X일 경과 여부
            is_old = os.stat(f).st_mtime < timestamp_now - (days_elapsed * 24 * 60 * 60)
            if is_old: # X일 경과했다면
                try:
                    os.remove(f) # 파일을 지운다
                    print(f, 'is deleted') # 삭제완료 로깅
                except OSError: # Device or resource busy (다른 프로세스가 사용 중)등의 이유
                    print(f, 'can not delete') # 삭제불가 로깅

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
    print('consumer created')
    
    producer = KafkaProducer(acks=0, compression_type='gzip', bootstrap_servers=['localhost:9092']) 
                              #value_serializer= lambda x : dumps(x).encode('utf-8'))

    print('producer created')


    # Prints all messages, again and again!
    requestDir = os.path.join(args.save_dir, 'request.json')
    userJsonDir = os.path.join(args.save_dir, 'user')
    movieJsonDir = os.path.join(args.save_dir, 'movie')
    while(True):    
        """ check IP adderess"""
        #ip_address = message.value[0]
        #print(ip_address)
        
        ip = {'recommendation'}
        producer.send('test', value=json.dumps({'ip':'123498213798479123879'}).encode('utf-8'))
        producer.flush()
        print('send')
                    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--save_dir', type = str, default = "./data/", help = 'Save directory')
    parser.add_argument('-m', '--save_movie', type = int, default=False , help= 'If want to save {movieID}.csv, True')
    parser.add_argument('-u', '--save_user', type = int, default=False, help= 'If want to save {userID}.csv, True')
    parser.add_argument('-r', '--save_request', type=bool, default=True, help= 'If want to save {request}.csv, True')
    
    args = parser.parse_args()
    
    run(args)
    ##
