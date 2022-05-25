import subprocess
import json
import os
from datetime import datetime

now = datetime.now().strftime('%Y%m%d_%H%M')
# process1
print('process 1...')
path = "./Milestone2/Kafka/data/movie"
command = ["dvc","add",path]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

command = ["git","add",os.path.join('/'.join(path.split(os.path.sep)[:-1]), 'movie.dvc')]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

# process2
print('process 2...')
path = "./Milestone3/Model_pipeline/DB/RAW_DATA/latest_info.json"
command = ["dvc","add",path]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

command = ["git","add",path+'.dvc']
print(' '.join(command))
result = subprocess.run(command)
print(result.stdout)

# process3
print('process 3...')
json_path =  "./Milestone3/Model_pipeline/DB/RAW_DATA/latest_info.json"

with open(json_path, 'rb') as f:
    json_dict = json.load(f)
f.close()

value = json_dict['latest_path']
path = "./Milestone3/Model_pipeline/DB/RAW_DATA/{}".format(value)
command = ["dvc","add",path]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

command = ["git","add",os.path.join('/'.join(path.split(os.path.sep)[:-1]), '{}.dvc'.format(value)), os.path.join('/'.join(path.split(os.path.sep)[:-1]), '.gitignore')]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

# process4
print('process 4...')
path = "./Milestone3/Model_pipeline/DB/CORPUS/latest_info.json"
command = ["dvc","add",path]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

command = ["git","add",path+'.dvc']
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

# process5
print('process 5...')
json_path = "./Milestone3/Model_pipeline/DB/CORPUS/latest_info.json"

with open(json_path, 'rb') as f:
    json_dict = json.load(f)
f.close()

value = json_dict['latest_path']
path = "./Milestone3/Model_pipeline/DB/CORPUS/{}".format(value)
command = ["dvc","add", path]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

command= ["git","add",os.path.join('/'.join(path.split(os.path.sep)[:-1]), '{}.dvc'.format(value)), os.path.join('/'.join(path.split(os.path.sep)[:-1]), '.gitignore')]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

# process6
print('process 6...')
path = "./Milestone3/Deployment/Docker_SVD/trained_model"
command = ["dvc", "add", path]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

command = ["git","add",os.path.join('/'.join(path.split(os.path.sep)[:-1]), 'trained_model.dvc'), os.path.join('/'.join(path.split(os.path.sep)[:-1]), '.gitignore')]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

# process7
print('process 7...')
path = "./Milestone3/Deployment/Docker_SVDPP/trained_model"
command =["dvc", "add", path]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

# # commit
command = ['git', 'status']
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)


command = ["git","add",os.path.join('/'.join(path.split(os.path.sep)[:-1]), 'trained_model.dvc'), os.path.join('/'.join(path.split(os.path.sep)[:-1]), '.gitignore')]
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)


# # commit
command = ['git', 'status']
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)


command = ['git', 'commit', '-m', 'new_version!']
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

#result = subprocess.run(['git', 'push', 'origin', 'master'])
#print(result.stdout)


# # tagging
command = ['git', 'tag', '-a', now+'_new_version', '-m', 'data_versioning']
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

command = ['git', 'push', 'origin', now+'_new_version']
print(" ".join(command))
result = subprocess.run(command)
print(result.stdout)

# save to remote storage
#command = ['dvc', 'push']
#print(" ".join(command))
#result = subprocess.run(command)
#print(result.stdout)