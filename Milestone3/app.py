import arrow
from splitio import get_factory
from splitio.exceptions import TimeoutException
import sys
import time
from flask import Flask, jsonify, request, make_response
import os
import pickle
import json
import requests
import random

TOPIC_NAME = "movielog24"
KAFKA_SERVER = "localhost:9092"
VM_SERVER = "128.2.205.125:8082"

factory = get_factory('cgaj8soepi94hme6sdl07pf83kpkud4o42h3')
try:
    factory.block_until_ready(5)
except TimeoutException:
    # The SDK failed to initialize in 5 seconds. Abort!
    sys.exit()
split = factory.client()

def checkHealth(ip_addr):
    return os.system('nc -vz '+ip_addr) == 0

#app = Flask(__name__)
app = Flask('load-balancer-server')
@app.route('/')
@app.route('/home')
def home():
    return 'Hello, World!'

@app.route('/det')
def det():
    factory.destroy()
    return 'The factory has been destoryed'

@app.route('/upload_json/<model_name>')
def upload_json(model_name):
    if model_name == "svd":
        with open('/home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/results_offline_svd.json','r') as read_file:
            off_results = json.load(read_file)
        read_file.close()
    if model_name == "svdpp":
        with open('/home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/results_offline_svdpp.json','r') as read_file:
            off_results = json.load(read_file)
        read_file.close()
    return off_results

@app.route('/recommend/<userid>') 
def recommend(userid):
    request_userid = userid #type of userid is 'str'
    #print('request_userid',request_userid)
    attributes = dict()
    attributes['user_id'] = request_userid

    # add health check
    A_server_up = checkHealth('172.17.0.3 30010')
    B_server_up = checkHealth('172.17.0.3 30011')

    # A_server_up = checkHealth('172.17.0.1 7004')
    # B_server_up = checkHealth('172.17.0.1 7005')

    if not B_server_up and A_server_up:
        #print('1')
        response_a = requests.get('http://172.17.0.3:30010/recommend/{}'.format(request_userid))
        response = response_a.text
    elif B_server_up and not A_server_up:
        #print('2')
        response_a = requests.get('http://172.17.0.3:30011/recommend/{}'.format(request_userid))
        response = response_a.text
    elif A_server_up and B_server_up:
        #print('3')
        
        #service should respond with an ordered comma separated list of up to 20 movie IDs in a single line
        treatment = split.get_treatment(request_userid, "main_split", attributes)
        #print('treatment',treatment)
        if treatment == "SVD":
            print('split to SVD')
            start_time = time.time() 
            response_a = requests.get('http://172.17.0.3:30010/recommend/{}'.format(request_userid))
            response = response_a.text
            #print('treatment is SVD')
            end_time = time.time() 
            #inference_time = end_time-start_time 
            track_event = split.track(request_userid,"user","inference_cost",end_time-start_time)
        elif treatment == "SVDpp":
            print('split to SVDpp')
            start_time = time.time()
            response_a = requests.get('http://172.17.0.3:30011/recommend/{}'.format(request_userid))
            response = response_a.text
            #print('treatment is SVDPP')
            end_time = time.time()
            #inference_time = end_time-start_time 
            track_event = split.track(request_userid,"user","inference_cost",end_time-start_time)
        else:
            # insert control code here
            print('treatment is control mode')
            pass

    else:
        #print('4')
        print('Not connected with Docker')
        rec_movies = []
        for i in range(20):
            rec_movies.append('harry+potter+and+the+deathly+hallows+part+1+2010')
        response = ','.join(rec_movies)
        #response = 'sorry we are fixing smthing'
        #inference_cost = inference_time

    return response

if __name__ == '__main__':
    app.run(host="128.2.205.125", port=8082, debug=True)