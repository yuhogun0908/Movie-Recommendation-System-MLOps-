# -*- coding: utf-8 -*-
# Final Debugged by ysHeo at 220209_2126

import os
from pprint import pprint
import random  
import pandas as pd
import numpy as np
#from mf import MatrixFactorization
from flask import Flask

import svd

import json
import requests
from utils import train_test_split, get_examples, most_popular, user_id2idx, item_idx2id, read_Json
from trained_MF.src.MF_deploy import deployment_process

VM_HOST = "128.2.205.125"
Request_PORT_for_Docker = 7004

data_dir = './large_data'  #large datasets
# data_dir = '/small_data'  #small datasets

R = np.load(os.path.join(data_dir,'rating.npy'))
m, n = R.shape
#================================================SVD============================================#

CSR_data_path = data_dir
trained_MF_path = "/home/team24/milestone1/Flask/trained_MF/model_save"

Deployed_MF = deployment_process(CSR_data_path = CSR_data_path, 
                                    trained_model_path = trained_MF_path)

coldstarter_rootpath = './coldstarter_metadata'

app = Flask('docker-flask-server-1')
@app.route('/')
@app.route('/home')
def home():
    return 'Welcome to the K-Avengers Movie Recommendation Service!. As out model, We recommend movies that you may find interesting :)'

@app.route('/recommend/<userid>') 
def recommend(userid):
    #request_userid = int(userid) #type of userid is 'str'
    user_idx, newuser_flag = user_id2idx(userid, PATH = data_dir)

    try:
        # if user is a new user:
        if newuser_flag:

            num_gender = 6;num_occupation=8; num_age = 6
            response = requests.get('http://128.2.204.215:8080  /user/{}'.format(userid))
            Query = response.json()
            gender = str(Query['gender'])
            age = int(Query['age'])
            age = str((age//10)*10)
            occupation = str(Query['occupation'])

            recommend_usingGender   = read_Json(os.path.join(coldstarter_rootpath,'gender',gender+'.json'))
            recommend_usingOccupation = read_Json(os.path.join(coldstarter_rootpath,'occupation',occupation.replace('/','_')+'.json'))
            recommend_usingAge = read_Json(os.path.join(coldstarter_rootpath,'age',age+'.json'))
            if len(recommend_usingAge) < 6:
                num_age = len(recommend_usingAge)
                num_occupation += (6-num_age)
            
            top_items  = random.sample(recommend_usingGender, num_gender)+random.sample(recommend_usingOccupation,num_occupation) + random.sample(recommend_usingAge,num_age)
            random.shuffle(top_items )

            # recommend most popular N movies
            # top_idx = most_popular(R, N=20)

        #if user is not a new user:
        if not newuser_flag:
            preds = Deployed_MF.recommend(test_userID=int(user_idx), top_n=20)
            #A = input()
            top_items = [k for k, v in preds]
            print('successively recommend using model')
                
    except:
        # recoomend most popular N movies
        top_idx = most_popular(R,N=20)
        # tranform item index to movie name
        top_items = item_idx2id(top_idx, PATH = data_dir)

    #service should respond with an ordered comma separated list of up to 20 movie IDs in a single line
    return ','.join(top_items)      # Yoon-edited at 0209_2100

if __name__ == '__main__':
    app.run(host=VM_HOST, port=Request_PORT_for_Docker, debug=True)