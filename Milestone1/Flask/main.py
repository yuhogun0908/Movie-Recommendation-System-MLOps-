# -*- coding: utf-8 -*-
# Final Debugged by ysHeo at 220209_2126

import os
from utils import *
from pprint import pprint
from knn import KNN
import random  
import pandas as pd
import numpy as np
#from mf import MatrixFactorization
from utils import train_test_split, get_examples, most_popular, user_id2idx, item_idx2id, read_Json
from flask import Flask

import json
import requests
from trained_MF.src.MF_deploy import deployment_process
"""""
K-Avengers Movie Recommendations
    1. Choose the model :
            Matrix Factorization : model = 0
            K-Nearest Neightbors : model = 1 
"""""
TOPIC_NAME = "movielog24"
KAFKA_SERVER = "localhost:9092"
VM_HOST = "128.2.205.125"
Request_PORT = 8082

data_dir = './large_data'  #large datasets
# data_dir = '/small_data'  #small datasets
model_mode = 0
KNN_Train_Flag = False

R = np.load(os.path.join(data_dir,'rating.npy'))
m, n = R.shape
#================================================SVD============================================#
if model_mode == 0:

    CSR_data_path = data_dir
    trained_MF_path = "/home/team24/milestone1/Flask/trained_MF/model_save"

    Deployed_MF = deployment_process(CSR_data_path = CSR_data_path, 
                                     trained_model_path = trained_MF_path)

#================================================KNN============================================#
if model_mode == 1:
    movie_idx2id_path = os.path.join(data_dir ,'movie_idx2id.json')
    
    MYKNN = KNN(KNN_Train_Flag, movie_idx2id_path, os.path.join(data_dir, 'rating_csr.npy'), test_path=None)
    # MYKNN = KNN(movie_idx2id_path, os.path.join(data_dir ,'/data_split/train_idx.json'), test_path=None)
    MYKNN.train()

#============================================Cold Starter========================================#
coldstarter_rootpath = './coldstarter_metadata'


app = Flask(__name__)
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
            response = requests.get('http://128.2.204.215:8080/user/{}'.format(userid))
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
            if model_mode == 0:
                preds = Deployed_MF.recommend(test_userID=int(user_idx), top_n=20)
                #A = input()
                top_items = [k for k, v in preds]
                print('successively recommend using model')
            if model_mode == 1:
                recommend_movies = MYKNN.recommend(user_id=int(user_idx))
                top_items = [int(v) for k, v in recommend_movies['itemid'].items()]
                top_items = item_idx2id(top_items, PATH=data_dir)
                top_items = top_items[:20]
                
                print('##Before Length## : ', len(top_items))    
                
                if len(top_items) < 20:
                    num_adds = 20 - len(top_items)
                    response = requests.get('http://128.2.204.215:8080/user/{}'.format(userid))
                    Query = response.json()
                    occupation = str(Query['occupation'])
                    recommend_usingOccupation = read_Json(os.path.join(coldstarter_rootpath,'occupation',occupation.replace('/','_')+'.json'))
                    top_items += random.sample(recommend_usingOccupation,k=num_adds) 
                
                print('##After Length## : ', len(top_items))    
                print('successively recommend using model')
                
    except:
        # recoomend most popular N movies
        top_idx = most_popular(R,N=20)
        # tranform item index to movie name
        #print(" @@@@@@@@@@@@@@@@@@@@@@")
        top_items = item_idx2id(top_idx, PATH = data_dir)
        #pprint(top_items)
        #print(" ############################## ")

    #service should respond with an ordered comma separated list of up to 20 movie IDs in a single line
    #return ','.join(str(top_items))
    return ','.join(top_items)      # Yoon-edited at 0209_2100

if __name__ == '__main__':
    #app.run(debug=True)
    #app.run(host="0.0.0.0", port=8082, debug=True)
    app.run(host=VM_HOST, port=Request_PORT, debug=True)