import arrow
from splitio import get_factory
from splitio.exceptions import TimeoutException
import sys
import time

from flask import Flask
import model_SVD
import model_KNN

TOPIC_NAME = "movielog24"
KAFKA_SERVER = "localhost:9092"
VM_SERVER = "128.2.205.125:8082"

model_svd = model_SVD.model_class()
model_knn = model_KNN.model_class()

factory = get_factory('cgaj8soepi94hme6sdl07pf83kpkud4o42h3')
try:
    factory.block_until_ready(5)
except TimeoutException:
    # The SDK failed to initialize in 5 seconds. Abort!
    sys.exit()
split = factory.client()

app = Flask(__name__)
@app.route('/')
@app.route('/home')
def home():
    return 'Hello, World!'

@app.route('/recommend/<userid>') 
def recommend(userid):
    request_userid = userid #type of userid is 'str'
    #print('request_userid',request_userid)
    attributes = dict()
    attributes['user_id'] = request_userid

    #service should respond with an ordered comma separated list of up to 20 movie IDs in a single line
    treatment = split.get_treatment(request_userid, "minwooc_split", attributes)
    #print('treatment',treatment)
    if treatment == "SVD":
        start_time = time.time() 
        rec_movies = model_svd.model_func(request_userid)
        end_time = time.time() 
        #print('treatment is SVD')
        
    elif treatment == "KNN":
        start_time = time.time() 
        rec_movies = model_knn.model_func(request_userid)
        end_time = time.time() 
        #print('treatment is KNN')
        
    else:
        # insert control code here
        print('treatment is control mode')
        pass

    #track_event = split.track(request_userid,"user","page_load_time",end_time-start_time)
    track_event = split.track(request_userid,"user","inference_time",end_time-start_time)
    #print('track_event',track_event)
    
    return ','.join(rec_movies)


### destory 안해도 review period 되면은 자동으로 metric impact

@app.route('/destroy')
def destroy():
    factory.destroy()
    return 'Connection with split.io is destoryed'

# @app.route('/restart')
# def restart():
#     factory = get_factory('cgaj8soepi94hme6sdl07pf83kpkud4o42h3')
#     try:
#         factory.block_until_ready(5)
#     except TimeoutException:
#         # The SDK failed to initialize in 5 seconds. Abort!
#         sys.exit()
#     split = factory.client()
#     return 'Connection with split.io is restarted'

if __name__ == '__main__':
    #app.run(debug=True)
    #app.run(host="0.0.0.0", port=8082, debug=True)
    app.run(host="128.2.205.125", port=8082, debug=True)
    