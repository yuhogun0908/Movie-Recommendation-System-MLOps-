import pandas as pd
import numpy as np
from utils import train_test_split, get_examples, most_popular, user_id2idx, item_idx2id, load_data
import time
import os
import json
import pdb
import wandb
import random
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import sys
import pdb
from sklearn.model_selection import train_test_split as sklearn_train_test_split
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import csr_matrix
from time import perf_counter
import wandb
from preprocessing import ids_encoder
from time import perf_counter

def evaluate(x_test, y_test):
    print('Evaluate the model on {} test data ...'.format(x_test.shape[0]))
    preds = list(predict(u,i) for (u,i) in x_test)
    mae = np.sum(np.absolute(y_test - np.array(preds))) / x_test.shape[0]
    rmse = np.sqrt(np.sum(np.power((y_test - np.array(preds)),2)) / x_test.shape[0])
    print('\nMAE :', mae)
    print('\nRMSE :', rmse)
    wandb.log({"Prediction accuracy (RMSE)": rmse})
    return rmse

def ratings_matrix(ratings):    
    return csr_matrix(pd.crosstab(ratings.userid, ratings.itemid, ratings.rating, aggfunc=sum).fillna(0).values)    

def create_model(rating_matrix, metric):
    """
    - create the nearest neighbors model with the corresponding similarity metric
    - fit the model
    """
    model = NearestNeighbors(metric=metric, n_neighbors=21, algorithm='brute')
    model.fit(rating_matrix)
    print("########", (sys.getsizeof(model)))    
    return model

def nearest_neighbors(rating_matrix, model):
    """    
    :param rating_matrix : rating matrix of shape (nb_users, nb_items)
    :param model : nearest neighbors model    
    :return
        - similarities : distances of the neighbors from the referenced user
        - neighbors : neighbors of the referenced user in decreasing order of similarities
    """    
    similarities, neighbors = model.kneighbors(rating_matrix)        
    return similarities[:, 1:], neighbors[:, 1:]


def find_candidate_items(userid):
    """
    Find candidate items for an active user
    
    :param userid : active user
    :param neighbors : users similar to the active user        
    :return candidates : top 30 of candidate items
    """
    user_neighbors = neighbors[userid]
    activities = ratings.loc[ratings.userid.isin(user_neighbors)]
    
    # sort items in decreasing order of frequency
    frequency = activities.groupby('itemid')['rating'].count().reset_index(name='count').sort_values(['count'],ascending=False)
    Gu_items = frequency.itemid
    active_items = ratings.loc[ratings.userid == userid].itemid.to_list()
    candidates = np.setdiff1d(Gu_items, active_items, assume_unique=True)[:30]
        
    return candidates

def predict(userid, itemid):
    """
    predict what score userid would have given to itemid.
    
    :param
        - userid : user id for which we want to make prediction
        - itemid : item id on which we want to make prediction
        
    :return
        - r_hat : predicted rating of user userid on item itemid
    """
    user_similarities = similarities[userid]
    user_neighbors = neighbors[userid]
    # get mean rating of user userid
    user_mean = mean[userid]
    
    # find users who rated item 'itemid'
    iratings = np_ratings[np_ratings[:, 1].astype('int') == itemid]
    
    # find similar users to 'userid' who rated item 'itemid'
    suri = iratings[np.isin(iratings[:, 0], user_neighbors)]
    
    # similar users who rated current item (surci)
    normalized_ratings = suri[:,4]
    indexes = [np.where(user_neighbors == uid)[0][0] for uid in suri[:, 0].astype('int')]
    sims = user_similarities[indexes]
    
    num = np.dot(normalized_ratings, sims)
    den = np.sum(np.abs(sims))
    
    if num == 0 or den == 0:
        return user_mean
    
    r_hat = user_mean + np.dot(normalized_ratings, sims) / np.sum(np.abs(sims))
    
    return r_hat

def user2userPredictions(userid, pred_path):
    """
    Make rating prediction for the active user on each candidate item and save in file prediction.csv
    
    :param
        - userid : id of the active user
        - pred_path : where to save predictions
    """    

    # find candidate items for the active user
    candidates = find_candidate_items(userid)
    
    # loop over candidates items to make predictions
    for itemid in candidates:
        
        # prediction for userid on itemid
        r_hat = predict(userid, itemid)
        
        # save predictions
        with open(pred_path, 'a+') as file:
            line = '{},{},{}\n'.format(userid, itemid, r_hat)
            file.write(line)

def user2userCF(scale_factor):
    """
    Make predictions for each user in the database.    
    """
    # get list of users in the database
    users = ratings.userid.unique()
    
    def _progress(count):
        sys.stdout.write('\rRating predictions. Progress status : %.1f%%' % (float(count/len(users))*100.0))
        sys.stdout.flush()
    
    saved_predictions = 'predictions{}.csv'.format(scale_factor)
    if os.path.exists(saved_predictions):
        os.remove(saved_predictions)
    
    for count, userid in enumerate(users):        
        # make rating predictions for the current user
        user2userPredictions(userid, saved_predictions)
        _progress(count)


def user2userRecommendation(userid):
    """
    """
    # encode the userid
    uid = uencoder.transform([userid])[0]
    saved_predictions = 'predictions.csv'
    
    predictions = pd.read_csv(saved_predictions, sep=',', names=['userid', 'itemid', 'predicted_rating'])
    predictions = predictions[predictions.userid==uid]
    List = predictions.sort_values(by=['predicted_rating'], ascending=False)
    
    List.userid = uencoder.inverse_transform(List.userid.tolist())
    List.itemid = iencoder.inverse_transform(List.itemid.tolist())
    
    # List = pd.merge(List, movies, on='itemid', how='inner')
    # print(List)
    return List


def load_data(filename):
    PATH = '/home/yoonseoh/Development/splited_data/data_split'
    # load rating matrix
    # R = pd.read_csv(os.path.join(PATH, 'split_rating.csv'))
    file = open(os.path.join(PATH, '{}_idx.json'.format(filename)))
    data = np.array(json.load(file))
    return data


def readJson(path):
    file = open(path)
    json_data = json.load(file)
    file.close()
    return json_data



random.seed(100)


def read_json(filename, PATH):
    # load rating matrix
    file = open(os.path.join(PATH, '{}_idx.json'.format(filename)))
    data = np.array(json.load(file))
    return data

if __name__ == "__main__":

    scale_arr = list(range(1, 6, 1))
    N_smp = 5000
    t_time_cost_lst = []
    i_time_cost_lst = []
    req_drop_lst = []
    for scale_factor in scale_arr:
        wandb.init(project="KNN scalabiltiy @"+str(int(scale_factor*10)), reinit=True)
        print('scale_factor[%]:',int(scale_factor*10))
        if int(scale_factor) != 10:
            #data_dir = '/home/yoonseoh/Development/Build_Dataset/save_ratings/20220207_2254/scalable_data/20220208_2352/' + str(scale_factor)
            data_dir = '/home/yoonseoh/Development/Build_Dataset/save_ratings/20220209_1329/scalable_data/20220209_1350/' + str(scale_factor)
        else:
            #data_dir = '/home/yoonseoh/Development/Build_Dataset/save_ratings/20220207_2254'#100% of small scale
            #data_dir = '/home/yoonseoh/Development/Build_Dataset/save_ratings/20220208_2316' #100% of large scale
            data_dir = '/home/yoonseoh/Development/Build_Dataset/save_ratings/20220209_1329' #100% of preprocessed large scale

        train_path = os.path.join(data_dir,'rating_csr.npy')
        #train_path = os.path.join(data_dir,'data_split','train_idx.json')
        valid_path = os.path.join(data_dir,'data_split','valid_idx.json')
        test_path = os.path.join(data_dir,'data_split','test_idx.json')


        movie_idx2id_path = data_dir + '/movie_idx2id.json'
        file = open(    movie_idx2id_path)
        movie_data = json.load(file)

        movie_df = pd.DataFrame(movie_data, columns=['title'])
        movie_df['itemid'] = np.arange(len(movie_data))
        movies = movie_df
        #train_data = readJson(train_path)
        train_data = np.load(train_path)
        train_data = np.array(train_data) # to numpy
        
        ratings = pd.DataFrame(train_data, columns=['userid','itemid','rating'])
        ratings, uencoder, iencoder = ids_encoder(ratings)   
        R = ratings_matrix(ratings) 

        model = create_model(rating_matrix=R, metric='cosine') # we can also use the 'euclidian' distance
        similarities, neighbors = nearest_neighbors(R, model)
        mean = ratings.groupby(by='userid', as_index=False)['rating'].mean()
        mean_ratings = pd.merge(ratings, mean, suffixes=('','_mean'), on='userid')
        mean_ratings['norm_rating'] = mean_ratings['rating'] - mean_ratings['rating_mean']
        mean = mean.to_numpy()[:, 1]
        np_ratings = mean_ratings.to_numpy()
        t1 = perf_counter()
        user2userCF(scale_factor)
        t2 = perf_counter()
        print('-'*80)
        print('[KNN] Training Latency=%.2f )'%((t2-t1)))
        wandb.log({"training time_cost[sec]": (t2-t1)})
        print('-'*80)


        file = open(test_path)
        data_test= np.array(json.load(file))
        ratings_test = pd.DataFrame(data_test,columns=['userid','itemid','rating'])
        ratings_test, _, _= ids_encoder(ratings_test)
        raw_examples, raw_labels = get_examples(ratings_test, labels_column='rating')
        evaluate(raw_examples, raw_labels)

        tmp = 0
        time_cost = 0
        request_drop = 0
        
        user_lst = [v for _ , v in ratings_test['userid'].items()]
        user_lst = list(set(user_lst))

        
        for user_id in random.choices(user_lst, k=50):
            
            try:
                start_time = time.time()
                user2userRecommendation(int(user_id))
                end_time = time.time()
                tmp += 1
                time_cost += ((end_time - start_time) * 1000)
                if time_cost > 600:
                    request_drop += 1
            except:
                pass
        avg_i_time_cost = time_cost / tmp
        wandb.log({"avg. inference time_cost[ms]": avg_i_time_cost})
        print('avg. inference time_cost[ms]:', avg_i_time_cost)
        print('# request_drop out of %d: %d' % (N_smp,request_drop))
        

        i_time_cost_lst.append(avg_i_time_cost)
        req_drop_lst.append(request_drop)

    print('i_time_cost_lst',i_time_cost_lst)
    print('req_drop_lst',req_drop_lst)
