from sklearn.model_selection import train_test_split as sklearn_train_test_split
import numpy as np
import pandas as pd
import json
import os

def get_examples(dataframe, labels_column="rating"):
    examples = dataframe[['userid', 'itemid']].values
    labels = dataframe[f'{labels_column}'].values
    return examples, labels

def load_data(filename, PATH):
    # load rating matrix
    R = pd.read_csv(os.path.join(PATH, 'split_rating.csv'))

    file = open(os.path.join(PATH, '{}_idx.json'.format(filename)))
    data = np.array(json.load(file))
    X = data[:,:2]
    y = data[:,-1]
    print("x: ", X.shape, " y: ", y.shape)
    return X, y


def read_Json(path):
    file = open(path)
    json_data = json.load(file)
    file.close()
    return json_data




def user_id2idx(user_id, PATH):
    file = open(os.path.join(PATH, 'user_id2idx.json'))
    user_data = json.load(file)
    try:
        user_idx = user_data[user_id]
    except:
        return None, True
    return user_idx, False

def item_idx2id(idx_lst, PATH):
    item_lst = []
    with open(os.path.join(PATH, "movie_idx2id.json")) as f:
        movie_data = json.load(f)
    for idx in idx_lst:
        item_lst.append(movie_data[idx])
    return item_lst

def train_test_split(examples, labels, test_size=0.2):
    # split data into train and test sets
    train_examples, test_examples, train_labels, test_labels = sklearn_train_test_split(
        examples, 
        labels, 
        test_size=test_size, 
        random_state=42, 
        shuffle=True
    )

    # transform train and test examples to their corresponding one-hot representations
    train_users = train_examples[:, 0]
    test_users = test_examples[:, 0]

    train_items = train_examples[:, 1]
    test_items = test_examples[:, 1]

    # Final training and test set
    x_train = np.array(list(zip(train_users, train_items)))
    x_test = np.array(list(zip(test_users, test_items)))

    y_train = train_labels
    y_test = test_labels

    return (x_train, x_test), (y_train, y_test)


def mean_ratings(dataframe):
    means = dataframe.groupby(by='userid', as_index=False)['rating'].mean()
    return means

def most_popular(R, N):
    """
    Return index of N most popular movies
    """
    if N > R.shape[1]:
        return np.argsort(np.mean(R, axis=0))
    else:
        return np.argsort(np.mean(R, axis=0))[::-1][:N]