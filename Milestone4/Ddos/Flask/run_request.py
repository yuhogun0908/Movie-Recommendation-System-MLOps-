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
import logging

# import numpy as np

from datetime import datetime


"""
Kafka data streaming
    
    provided data :    
        #1. <time>,<userid>,recommendation request <server>,status <200 for success>, result: <responsetime>
        #2. <time>,<userid>,GET /data/m/<movieid>/<minute>.mpg
        #3. <time>,<userid>,GET /rate/<movieid>=<rating>
    
    arguments : save directory

"""

def run(args):
    
    """
    Recommend time logging
    """
    
    logging.basicConfig(filename='recommend_time.log', format= '%(asctime)s %(message)s', level=logging.INFO, filemode='w')
    # create an object
    logger = logging.getLogger()
    
    logger.info("System Start")

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
    
    # Prints all messages, again and again!
    requestDir = os.path.join(args.save_dir, 'request.json')
    userJsonDir = os.path.join(args.save_dir, 'user')
    movieJsonDir = os.path.join(args.save_dir, 'movie')
    
    total_time = 0
    consumer_count = 0
    Threshold_time = 800
    
    abnormal_count = 0
    Threshold_counts = 50
    
    for idx, message in enumerate(consumer):
        """ check IP adderess"""
        #ip_address = message.value[0]
        #print(ip_address)
        # Default message.value type is bytes!
        messageValue = message.value.decode('utf-8')
        # print(messageValue)
        
        """
        check ddos by using response time
        """
        if 'recommendation' in messageValue:
            print(message)
            consumer_count += 1
            recommend_time = int(messageValue.split(', ')[-1].split(' ms')[0])
            
            if consumer_count == 1:
              total_time += recommend_time
              Avg_time = int(total_time/consumer_count)
            else:
              Avg_time = Avg_time * 0.9 + recommend_time * 0.1
                           
            sys.stdout.write('\r')
            sys.stdout.write('| Avg recommend time [%3d]ms \t Current recommend time[%3d]ms '%(Avg_time, recommend_time))
            sys.stdout.flush()
            sys.stdout.write('\r')
            
            if Avg_time > Threshold_time:
                abnormal_count += 1
            else:
              abnormal_count = 0
            
            #print(abnormal_count)
            
            if abnormal_count == Threshold_counts :
                logger.info("Ddos Expected : {}ms".format(str(Avg_time)))
                abnormal_count -= 1
          
              

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--save_dir', type = str, default = "./data/", help = 'Save directory')
    parser.add_argument('-m', '--save_movie', type = int, default=False , help= 'If want to save {movieID}.csv, True')
    parser.add_argument('-u', '--save_user', type = int, default=False, help= 'If want to save {userID}.csv, True')
    parser.add_argument('-r', '--save_request', type=bool, default=True, help= 'If want to save {request}.csv, True')
    
    args = parser.parse_args()
    
    run(args)
    ##
