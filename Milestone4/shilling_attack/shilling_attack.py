#-*- coding: utf-8 -*-
import os, json
import os.path as osp
import random

import numpy as np
import string

random_seed =  42
movie_dir_path = "/home/yoonseoh/group-project-s22-k-avengers/Milestone3/Model_pipeline/DB/RAW_DATA/20220415_0139/movie"
sample_dir_path = "/home/team24/group-project-s22-k-avengers/Milestone4/shilling_attack/data"
original_filename = "originals.json"
original_data_info = "original_distribution.json"
attacked_filename = "attacked.json"
verified_filename = "verified.json"
num_samples = 30
num_adversarial_samples = 30
ratings_size_threshold = 20
one_movie_ratings_threshold = 20
one_movie_avg_rate_threshold = 0.4

filelist = os.listdir(movie_dir_path)
file_idx = np.arange(len(filelist))
np.random.shuffle(file_idx)
samples_list = []
"""
# Step 1: Choice of random samples
for i in file_idx:
    filename = filelist[i]
    with open(osp.join(movie_dir_path, filename), "r") as f:
        sample = json.load(f)
    try:
        ratings = sample["ratingUserList"]
        movie_name = sample["movieQuery"]["id"]

    except:
        continue

    if len(ratings) <= rating_threshold:
        continue

    samples_list.append(sample)

    if len(samples_list) == num_samples:
        break

with open(osp.join(sample_dir_path, "originals.json"), "w") as f:
    json.dump(samples_list, f, indent=4)
"""

# Step 2: Record the distribution of pure dataset 
def ratings_information(ratings):
    weighted_sum = 0
    score_dict = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    for user, score in ratings.items():
        if score in score_dict.keys():
            score_dict[score] += 1
        else:
            continue
    ratings_cnt = np.array(list(score_dict.values()))
    for i, value in enumerate(ratings_cnt):
        weighted_sum += (i + 1) * value
    #weighted_sum += ((i+1) * value for i, value in enumerate(ratings_cnt))
    avg_rate = weighted_sum / (ratings_cnt.sum())
    ratings_nums = ratings_cnt.sum()
    return score_dict, avg_rate, ratings_nums

def _get_sample_information(sample):
    """
    :param sample: one movie data
    :return:
    # score_dict: # of ratings per rate
    # avg_ratings: avg rate of this movie
    # ratings_num: # of ratings
    """
    movie_id = sample["movieQuery"]["id"]
    ratings = sample["ratingUserList"]

    score_dict, avg_rate, ratings_num = ratings_information(ratings)
    all_dict = {"movie_name": movie_id,
                "score_dict": score_dict,
                "avg_rate"  : avg_rate,
                "ratings_num": ratings_num}
    return all_dict

def get_data_distributions(samples_list):
    ratings_num = 0
    ratings_sum = 0.0
    total_list = []
    movie_id_list = []
    for sample in samples_list:
        info_dict = _get_sample_information(sample)
        ratings_num += info_dict["ratings_num"]
        ratings_sum += info_dict["avg_rate"] * info_dict["ratings_num"]
        movie_id_list.append(info_dict["movie_name"])
        total_list.append(info_dict)
    ratings_avg = ratings_sum / ratings_num
    total_dict = {"all_ratings": ratings_num,
                  "avg_ratings": ratings_avg,
                  "movie_name_list": movie_id_list,
                  "total_info": total_list}

    return total_dict, ratings_num, ratings_avg

#"""

# Step 2: Get original data distributions
dataset_path = osp.join(sample_dir_path, original_filename)
with open(dataset_path, "r") as f:
    samples_list = json.load(f)

total_dict, ratings_num, ratings_avg = get_data_distributions(samples_list)


original_data_info_path = osp.join(sample_dir_path, original_data_info)
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

with open(original_data_info_path, "w") as f:
    json.dump(total_dict, f, indent="\t", cls=NpEncoder)

print("  >> Save the information of original dataset: {}".format(original_data_info_path))
print("  >> # of current ratings: {}".format(ratings_num))
print("  >> # of average ratings: {}".format(ratings_avg))
print("")
#"""

# Step 3: Adversarial Attack
target_movie = "dark+passage+1947"
attack_movie = "a+shot+in+the+dark+1964"

def get_random_id_with_score(num_size, good_flag=True):
    _LENGTH = 6
    string_pool = string.digits
    adversarial_data = []
    for idx in range(num_size):
        results = ""
        for i in range(_LENGTH):
            results += random.choice(string_pool)

        if good_flag is True:
            score = 5
        else:
            score = 1

        adversarial_data.append((results, score))

    return adversarial_data

def update_adversarial_data(sample_dict, adversarial_data):

    for new_id, score in adversarial_data:
        sample_dict["ratingUserList"][new_id] = str(score)

    return sample_dict

def get_ratings_joojak(target_movie_name, original_data, good_flag=True):
    for target_idx, sample_dict in enumerate(original_data):
        if sample_dict["movieQuery"]["id"] == target_movie_name:
            adversarial_data = get_random_id_with_score(
                num_size=num_adversarial_samples,
                good_flag=good_flag)
            res = update_adversarial_data(sample_dict, adversarial_data)
            original_data[target_idx] = res

    return original_data

original_dataset_path = osp.join(sample_dir_path, original_filename)
with open(original_dataset_path, "r") as f:
    original_data = json.load(f)

attacked_data = get_ratings_joojak(target_movie_name=target_movie,
                                   original_data=original_data,
                                   good_flag=True)

attacked_data = get_ratings_joojak(target_movie_name=attack_movie,
                                   original_data=attacked_data,
                                   good_flag=False)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

attacked_data_path = osp.join(sample_dir_path, attacked_filename)
with open(attacked_data_path, "w" ) as f:
    json.dump(attacked_data, f, indent="\t", cls=NpEncoder)

print("  >> Finish adversarial attack on movie-rating data")

def find_attacked_data(original_distribution_dict, current_data_dict):
    attacked_data_list= []
    original_list = original_distribution_dict["total_info"]
    current_dict_list = current_data_dict["total_info"]
    for idx, sample in enumerate(current_dict_list):
        cur_movie_name = sample["movie_name"]
        cur_ratings_num = sample["ratings_num"]
        cur_avg_rate = sample["avg_rate"]
        for elem in original_list:
            if elem["movie_name"] == cur_movie_name:
                prev_ratings_num = elem["ratings_num"]
                prev_avg_rate = elem["avg_rate"]

                if (cur_ratings_num - prev_ratings_num > one_movie_ratings_threshold) and \
                        (cur_avg_rate - prev_avg_rate) >= one_movie_avg_rate_threshold:
                    attacked_data_list.append((idx, "good"))
                    break

                if (cur_ratings_num - prev_ratings_num > one_movie_ratings_threshold) and \
                        (cur_avg_rate - prev_avg_rate) <= -one_movie_avg_rate_threshold:
                    attacked_data_list.append((idx, "terror"))
                    break

    return attacked_data_list

def printout_results(attacked_data, attacked_data_idx_list):
    def printout(attacked_data, state="good"):
        print("  *******************\n")
        print("  >> movie_name: {}".format(attacked_data["movieQuery"]["id"]))
        if state == "good":
            print("  >> adversarial method: {}".format("Add 5 points intentionally"))
        else:
            print("  >> adversarial method: {}".format("Add 1 points intentionally"))
        print("  *******************\n")
        return

    print("  >> There are {} attacked data ".format(len(attacked_data_idx_list)))
    for idx, state in attacked_data_idx_list:
        attacked_elem = attacked_data[idx]
        printout(attacked_elem, state)

# Step 4: Detect Adversarial Attack
check_data_path = osp.join(sample_dir_path, attacked_filename)
with open(check_data_path, "r") as f:
    check_data_list = json.load(f)

checked_total_dict, checked_ratings_num, checked_ratings_avg = get_data_distributions(check_data_list)

original_distribution_file_path = osp.join(sample_dir_path, original_data_info)
with open(original_distribution_file_path, "r") as f:
    original_distribution_dict = json.load(f)

verified_data = check_data_list
if checked_ratings_num - original_distribution_dict["all_ratings"] > ratings_size_threshold:
    print("  >> WARNING: The number of ratings are significantly increased for a short period of time..")
    print("  >> Inspectation....")
    attacked_data_idx_list = find_attacked_data(original_distribution_dict, checked_total_dict)

    print("  >> Here is a list of adversarial data:")
    printout_results(check_data_list, attacked_data_idx_list)

    verified_data = []
    for idx, elem in enumerate(check_data_list):
        flag = False
        for target_idx, state in attacked_data_idx_list:
            if idx == target_idx:
                flag = True
                break
        if flag is False:
            verified_data.append(elem)

verified_data_path = osp.join(sample_dir_path, verified_filename)
with open(verified_data_path, "w") as f:
    json.dump(verified_data, f, indent="\t", cls=NpEncoder)

print("  >> Verified Dataset Path: {}".format(verified_data_path))
print("  >> # of deleted data: {}".format(len(check_data_list) - len(verified_data)))
print("  >> # of verified data: {}".format(len(verified_data)))
