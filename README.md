# Movie-Recommendation-System-MLOps



## Table of contents
* [Overall Architecture](#overall-architecture)
* [Continuous Integration](#continuous-integration)
* [Continuous Deployment](#continuous-deployment)
* [Reflection](#reflection)
* [Conclusion](#conclusion)


## Overall architecture
The following architecture shows our deployment movie recommendation system

<img src="https://user-images.githubusercontent.com/67786803/170400718-4b8f8264-a82f-4e92-a93b-6cb6cf1ee3f1.png"
     width="737" height="596">

 ### :gear: Software & Tools
<p align="left">
&emsp;
<a target="_blank" href="https://kafka.apache.org/"><img src="https://user-images.githubusercontent.com/67786803/170406796-54e2d4b0-1158-4dda-8d8c-0cd981a6cd14.png?style=for-the-badge&logo=git&logoColor=white"  width="134" height="123"></img></a>
&emsp;
<a target="_blank" href="https://dvc.org/"><img src="https://user-images.githubusercontent.com/67786803/170407079-b8736cfd-e054-497f-814f-c7c0b85cce0b.png?style=for-the-badge&logo=git&logoColor=white" width="150" height="79"></img></a>
&emsp;
<a target="_blank" href="https://jenkins.io"><img src="https://user-images.githubusercontent.com/67786803/170408471-dcf95828-332a-4a3d-8992-4eeee2516fd2.png?style=for-the-badge&logo=git&logoColor=white" width="100" height="151"></img></a>
&emsp;
<a target="_blank" href="https://flask.palletsprojects.com/en/2.1.x/"><img src="https://user-images.githubusercontent.com/67786803/170408686-e1be3d88-3333-4a42-a657-60c3965146b0.png?style=for-the-badge&logo=git&logoColor=white" width="150" height="58"></img></a>
&emsp;
<a target="_blank" href="https://hub.docker.com/"><img src="https://user-images.githubusercontent.com/67786803/170409481-17d814b9-e06b-4677-a982-b0d075b5e600.png?style=for-the-badge&logo=git&logoColor=white" width="100" height="89"></img></a>
&emsp;
<a target="_blank" href="https://www.split.io/"><img src="https://user-images.githubusercontent.com/67786803/170408885-d08db5c4-0e80-4d20-9d03-2ce38de6a77e.png?style=for-the-badge&logo=git&logoColor=white" width="149" height="60"></img></a>
&emsp;
<a target="_blank" href="https://prometheus.io/"><img src="https://user-images.githubusercontent.com/67786803/170408965-7125eda4-310c-4a29-aa5e-23702cefd956.png?style=for-the-badge&logo=git&logoColor=white" width="150" height="74"></img></a>
&emsp;
<a target="_blank" href="https://grafana.com/"><img src="https://user-images.githubusercontent.com/67786803/170409061-bde198e4-7cca-4d04-afa7-461f78a3a5e3.png?style=for-the-badge&logo=git&logoColor=white" width="150" height="70"></img></a>
&emsp;
<a target="_blank" href="https://kubernetes.io/"><img src="https://user-images.githubusercontent.com/67786803/170409137-8e242cd8-6f3e-4cf8-8d64-fd7425bcc185.png?style=for-the-badge&logo=git&logoColor=white"  width="130" height="114"></img></a>
&emsp;
<a target="_blank" href="https://rancher.com/"><img src="https://user-images.githubusercontent.com/67786803/170409205-75128770-bdbd-4e96-912d-1f3fe4c50d53.png?style=for-the-badge&logo=git&logoColor=white" width="130" height="99"></img></a>
&emsp;
<a target="_blank" href="https://slack.com/"><img src="https://user-images.githubusercontent.com/67786803/170409326-f2a0a772-236a-49a5-8dcc-6b4bf1ea881d.png?style=for-the-badge&logo=git&logoColor=white" width="150" height=61"></img></a>

<br>
</p>





## Continuous Integration
 ### 1. A pipeline for movie recommendation
  ![PipelineforMovie](https://user-images.githubusercontent.com/67786803/170403643-b26c4941-03b6-470b-9efc-3574023279ab.png)
   - Data storage
     -    Apache Kafka is a distributed event store and stream-processing platform
     -    Collect Kafka log data
          -    Data (movies watched by user) --> for (re)training model and for online evaluation
          -    Rate (rating by user) --> for (re)training model and for online evaluation
          -    Request --> for online evaluation
     -    This pipeline, once run, continues to run until it is intentionally stopped.
     -    After online evaluation, expired data is automatically deleted.
   - Data preprocessing
     -    pre-processing the stored raw data
     -    Generate a compresssed sparse row (CSR) matrix
     -    Split it into train/validation sets
   - Model (re)training
     -    Matrix Factorization (MF)
          -    SVD
     <p align="center">
          <img src="https://user-images.githubusercontent.com/67786803/170417471-004c781a-76cd-443b-a956-856faa76f013.png"
     width="375" height="67"> 
     </p>
          -    SVD++
     <p align="center">
          <img src="https://user-images.githubusercontent.com/67786803/170417543-65bd853b-7d4b-4bb6-8861-bbc9172c8ba6.png"
     width="364" height="67">
     </p>
   - Offline evaluation
     -    'RMSE' as metric for offline evaluation
 ### 2. Code integrity checks with uni-test
   - The process is integrated on Jenkins pipeline, which runs automatically.
   - The result can be identified in a coverage report format on Jenkins
     <p align="center">
          <img src="https://user-images.githubusercontent.com/67786803/170418435-3edc2273-40ad-4ea7-a5e5-a188cb8197f9.png"
     width="426" height="140">
     </p

###  3. Automatic integration pipeline with Jenkins
   - Continuous integration
     - Jenkins
          - Unit test 1 to 5 --> model management & offline evaluation (model) --> online evaluation
     - Using Blue Ocean plugin
          - A more visualized dashboard than ever before
          - Commit occurs in master branch of github --> Autorun the entire pipeline
          - Save after pipeline build --> Jenkinsfile for pipeline is committed to master branch on github
     - Using freestyle project
          - Automatically run once in a specific period of time
          - Setting the "build periodically" option

## Continuous Deployment
### 1. Containerization with Rancher
### 2. Automatic Continuous Deployment with Jenkins
### 3. Monitoring
### 4. Versioning and tracking provenance

## Reflection
     
## Conclusion
