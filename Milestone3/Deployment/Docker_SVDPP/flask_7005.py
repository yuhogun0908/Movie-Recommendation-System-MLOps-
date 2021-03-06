# -*- coding: utf-8 -*-
# Final Debugged by ysHeo at 220413

import os.path as osp
import numpy as np
from flask import Flask
from utils import user_id2idx, item_idx2id
from trained_MF.src.MF_deploy import deployment_process

#VM_HOST = "128.2.205.125"
#Request_PORT_for_Docker = 7004

VM_HOST = "0.0.0.0"
Request_PORT_for_Docker = 8081
# TODO: Docker에 Data 저장 경로로 수정
# data_dir: Docker에 Data 저장한 곳
data_dir = '/workspace/data_for_deployment'  #large datasets

#R = np.load(os.path.join(data_dir,'rating.npy'))
#m, n = R.shape
#================================================SVD============================================#

CSR_data_path = data_dir
trained_model_path = "/workspace/trained_model"
#trained_model_path = "/home/yoonseoh/group-project-s22-k-avengers/Milestone3/Deployment/Docker_SVD/trained_model"
most_popular_path = "/workspace/most_popular"

Deployed_MF = deployment_process(CSR_data_path = CSR_data_path,
                                 trained_model_path = trained_model_path)

most_popular_idx_list = np.load(osp.join(most_popular_path, "most_popular.npy"))

app = Flask('docker-flask-server-SVDPP')
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
            top_idx = most_popular_idx_list
            # tranform item index to movie name
            top_items = item_idx2id(top_idx, PATH=data_dir)

        #if user is not a new user:
        if not newuser_flag:
            preds = Deployed_MF.recommend(test_userID=int(user_idx), top_n=20)
            #A = input()
            top_items = [k for k, v in preds]
            print('successively recommend using model')
                
    except:
        # recoomend most popular N movies
        #top_idx = most_popular(R,N=20)
        top_idx = most_popular_idx_list
        # tranform item index to movie name
        top_items = item_idx2id(top_idx, PATH = data_dir)

    #service should respond with an ordered comma separated list of up to 20 movie IDs in a single line
    return ','.join(top_items)      # Yoon-edited at 0209_2100

if __name__ == '__main__':
    app.run(host=VM_HOST, port=Request_PORT_for_Docker, debug=True)