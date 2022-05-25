import os
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import pandas as pd
import numpy as np
import json
import sys
import zipfile
import pdb
from sklearn.model_selection import train_test_split as sklearn_train_test_split
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import csr_matrix
from time import perf_counter
import numpy as np
import pandas as pd



def readJson(path):
    file = open(path)
    json_data = json.load(file)
    file.close()
    return json_data

class KNN():
    def __init__(self,train_flag,movie_idx2id_path, train_path, test_path=None):
        # movie_idx2id_path : .json
        # train_path : .npy
        # test_path : .json
        self.train_flag = train_flag

        movie_idx2id = readJson(movie_idx2id_path) 
        movie_idx2id = pd.DataFrame(movie_idx2id, columns=['title'])
        movie_idx2id['itemid'] = np.arange(len(movie_idx2id))
        self.movie_idx2id = movie_idx2id


        train_data = np.load(train_path) # [user#id, movie#id, rating]

        # train_data = readJson(train_path)
        # train_data  = np.array(train_data) # to numpy
        self.train_ratings = pd.DataFrame(train_data, columns=['userid','itemid','rating'])

        if test_path is not None:
            self.test_path = test_path
        
    def train(self):
        self.train_ratings, self.train_uencoder, self.train_iencoder = self.ids_encoder(self.train_ratings)
        
        if self.train_flag :
            R = self.ratings_matrix(self.train_ratings)
            model = self.create_model(rating_matrix=R, metric='cosine') # we can also use the 'euclidian' distance
            self.similarities, self.neighbors = self.nearest_neighbors(R, model)
            # mean ratings for each user
            mean = self.train_ratings.groupby(by='userid', as_index=False)['rating'].mean()
            mean_ratings = pd.merge(self.train_ratings, mean, suffixes=('','_mean'), on='userid')
            # normalized ratings for each items
            mean_ratings['norm_rating'] = mean_ratings['rating'] - mean_ratings['rating_mean']
            self.mean = mean.to_numpy()[:, 1]
            self.np_ratings = mean_ratings.to_numpy()
            
            self.user2userCF()
            t1 = perf_counter()
            self.user2userRecommendation(3)
            t2 = perf_counter()
            print('-'*80)
            print(' Content Based =%.2f ms)'%((t2-t1)*1000))
            print('-'*80)

    def eval(self,user_id,test_path=None):
        evaluation = False
        if evaluation == True and test_path is not None:
            test_data = readJson(test_path)
            test_data = np.array(test_data)
            test_data = pd.DataFrame(test_data, columns=['userid','itemid','rating'])
            rating_test, _, _ = self.ids_encoder(test_data)
            
            raw_examples = rating_test[['userid', 'itemid']].values
            raw_labels = rating_test[f'{"rating"}'].values
            self.evaluate(raw_examples, raw_labels)
        
        return self.user2userRecommendation(user_id)
    
    def recommend(self,user_id):
        
        return self.user2userRecommendation(user_id)
        

    def evaluate(self,x_test, y_test):
        print('Evaluate the model on {} test data ...'.format(x_test.shape[0]))
        preds = list(self.predict(u,i) for (u,i) in x_test)
        mae = np.sum(np.absolute(y_test - np.array(preds))) / x_test.shape[0]
        print('\nMAE :', mae)
        return mae

    def user2userRecommendation(self,userid):
        """
        """
        # encode the userid
        uid = self.train_uencoder.transform([userid])[0]
        saved_predictions = './trained_KNN/predictions.csv'
        
        predictions = pd.read_csv(saved_predictions, sep=',', names=['userid', 'itemid', 'predicted_rating'])
        predictions = predictions[predictions.userid==uid]
        List = predictions.sort_values(by=['predicted_rating'], ascending=False)
        
        List.userid = self.train_uencoder.inverse_transform(List.userid.tolist())
        List.itemid = self.train_iencoder.inverse_transform(List.itemid.tolist())

        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@")
        # print(List)
        # ########
        List = pd.merge(List, self.movie_idx2id, on='itemid', how='inner')
        # ########
        # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # print(List)

        # print(List)
        return List


    def user2userCF(self):
        """
        Make predictions for each user in the database.    
        """
        # get list of users in the database
        users = self.train_ratings.userid.unique()
        
        def _progress(count):
            sys.stdout.write('\rRating predictions. Progress status : %.1f%%' % (float(count/len(users))*100.0))
            sys.stdout.flush()
        
        saved_predictions = 'predictions.csv'    
        if os.path.exists(saved_predictions):
            os.remove(saved_predictions)
        
        for count, userid in enumerate(users):        
            # make rating predictions for the current user
            self.user2userPredictions(userid, saved_predictions)
            _progress(count)


    def find_candidate_items(self,userid):
        """
        Find candidate items for an active user
        
        :param userid : active user
        :param neighbors : users similar to the active user        
        :return candidates : top 30 of candidate items
        """
        user_neighbors = self.neighbors[userid]
        activities = self.train_ratings.loc[self.train_ratings.userid.isin(user_neighbors)]
        
        # sort items in decreasing order of frequency
        frequency = activities.groupby('itemid')['rating'].count().reset_index(name='count').sort_values(['count'],ascending=False)
        Gu_items = frequency.itemid
        active_items = self.train_ratings.loc[self.train_ratings.userid == userid].itemid.to_list()
        candidates = np.setdiff1d(Gu_items, active_items, assume_unique=True)[:30]
            
        return candidates

    def user2userPredictions(self,userid, pred_path):
        """
        Make rating prediction for the active user on each candidate item and save in file prediction.csv
        
        :param
            - userid : id of the active user
            - pred_path : where to save predictions
        """    

        # find candidate items for the active user
        candidates = self.find_candidate_items(userid)
        
        # loop over candidates items to make predictions
        for itemid in candidates:
            
            # prediction for userid on itemid
            r_hat = self.predict(userid, itemid)
            
            # save predictions
            with open(pred_path, 'a+') as file:
                line = '{},{},{}\n'.format(userid, itemid, r_hat)
                file.write(line)

    def predict(self, userid, itemid):
        """
        predict what score userid would have given to itemid.
        
        :param
            - userid : user id for which we want to make prediction
            - itemid : item id on which we want to make prediction
            
        :return
            - r_hat : predicted rating of user userid on item itemid
        """
        user_similarities = self.similarities[userid]
        user_neighbors = self.neighbors[userid]
        # get mean rating of user userid
        user_mean = self.mean[userid]
        
        # find users who rated item 'itemid'
        iratings = self.np_ratings[self.np_ratings[:, 1].astype('int') == itemid]
        
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

    def ids_encoder(self,ratings):
        users = sorted(ratings['userid'].unique())
        items = sorted(ratings['itemid'].unique())

        # create users and items encoders
        uencoder = LabelEncoder()
        iencoder = LabelEncoder()

        # fit users and items ids to the corresponding encoder
        uencoder.fit(users)
        iencoder.fit(items)

        # encode userids and itemids
        ratings.userid = uencoder.transform(ratings.userid.tolist())
        ratings.itemid = iencoder.transform(ratings.itemid.tolist())

        return ratings, uencoder, iencoder


    def ratings_matrix(self,ratings):    
        return csr_matrix(pd.crosstab(ratings.userid, ratings.itemid, ratings.rating, aggfunc=sum).fillna(0).values)    

    def create_model(self,rating_matrix, metric):
        """
        - create the nearest neighbors model with the corresponding similarity metric
        - fit the model
        """
        model = NearestNeighbors(metric=metric, n_neighbors=21, algorithm='brute')
        model.fit(rating_matrix)    
        return model

    def nearest_neighbors(self,rating_matrix, model):
        """    
        :param rating_matrix : rating matrix of shape (nb_users, nb_items)
        :param model : nearest neighbors model    
        :return
            - similarities : distances of the neighbors from the referenced user
            - neighbors : neighbors of the referenced user in decreasing order of similarities
        """    
        similarities, neighbors = model.kneighbors(rating_matrix)        
        return similarities[:, 1:], neighbors[:, 1:]
        # if doTest:




if __name__ == "__main__":

    movie_idx2id_path = os.path.join('/home/yoonseoh/Development/splited_data','movie_idx2id.json')
    train_path = os.path.join( './', 'rating_csr.npy')
    test_path = os.path.join( '/home/yoonseoh/Development/splited_data/data_split', 'test_idx.json')
    
    MYKNN = KNN(movie_idx2id_path, train_path, test_path)
    MYKNN.train()

    MYKNN.eval(test_path)