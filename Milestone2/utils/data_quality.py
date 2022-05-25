import numpy as np

from datetime import datetime

def check_time(time,data_type):
    try:
        time_input = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
        if len(str(time_input.year)) != 4:
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
                status = check_time(time, 0)
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
                if len(messageValue.split(',')) != 26:
                    status = 5
            elif 'GET' in messageValue:
                if len(messageValue.split(',')) != 3:
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
