# Movie-Recommendation-System-MLOps



## Table of contents
* [Overall Architecture](#overall-architecture)
* [Continuous Integration](#continuous-integration)
* [Continuous Deployment](#continuous-deployment)
* [Conclusion](#conclusion)


## Overall architecture
The following architecture shows our deployment movie recommendation system

<img src="https://user-images.githubusercontent.com/67786803/170400718-4b8f8264-a82f-4e92-a93b-6cb6cf1ee3f1.png"
     width="737" height="596">

 ### :gear: Software & Tools
<p align="left">
&emsp;
<a target="_blank" href="https://kafka.apache.org/"><img src="https://user-images.githubusercontent.com/67786803/170406796-54e2d4b0-1158-4dda-8d8c-0cd981a6cd14.png?style=for-the-badge&logo=git&logoColor=white"  width="100" height="91"></img></a>
&emsp;
<a target="_blank" href="https://dvc.org/"><img src="https://user-images.githubusercontent.com/67786803/170407079-b8736cfd-e054-497f-814f-c7c0b85cce0b.png?style=for-the-badge&logo=git&logoColor=white" width="130" height="68"></img></a>
&emsp;
<a target="_blank" href="https://jenkins.io"><img src="https://user-images.githubusercontent.com/67786803/170408471-dcf95828-332a-4a3d-8992-4eeee2516fd2.png?style=for-the-badge&logo=git&logoColor=white" width="100" height="151"></img></a>
&emsp;
<a target="_blank" href="https://flask.palletsprojects.com/en/2.1.x/"><img src="https://user-images.githubusercontent.com/67786803/170408686-e1be3d88-3333-4a42-a657-60c3965146b0.png?style=for-the-badge&logo=git&logoColor=white" width="130" height="50"></img></a>
&emsp;
<a target="_blank" href="https://hub.docker.com/"><img src="https://user-images.githubusercontent.com/67786803/170409481-17d814b9-e06b-4677-a982-b0d075b5e600.png?style=for-the-badge&logo=git&logoColor=white" width="100" height="89"></img></a>
&emsp;
<a target="_blank" href="https://www.split.io/"><img src="https://user-images.githubusercontent.com/67786803/170408885-d08db5c4-0e80-4d20-9d03-2ce38de6a77e.png?style=for-the-badge&logo=git&logoColor=white" width="120" height="48"></img></a>
&emsp;
<a target="_blank" href="https://prometheus.io/"><img src="https://user-images.githubusercontent.com/67786803/170408965-7125eda4-310c-4a29-aa5e-23702cefd956.png?style=for-the-badge&logo=git&logoColor=white" width="140" height="48"></img></a>
&emsp;
<a target="_blank" href="https://grafana.com/"><img src="https://user-images.githubusercontent.com/67786803/170409061-bde198e4-7cca-4d04-afa7-461f78a3a5e3.png?style=for-the-badge&logo=git&logoColor=white" width="130" height="60"></img></a>
&emsp;
<a target="_blank" href="https://kubernetes.io/"><img src="https://user-images.githubusercontent.com/67786803/170409137-8e242cd8-6f3e-4cf8-8d64-fd7425bcc185.png?style=for-the-badge&logo=git&logoColor=white"  width="110" height="96"></img></a>
&emsp;
<a target="_blank" href="https://rancher.com/"><img src="https://user-images.githubusercontent.com/67786803/170409205-75128770-bdbd-4e96-912d-1f3fe4c50d53.png?style=for-the-badge&logo=git&logoColor=white" width="110" height="83"></img></a>
&emsp;
<a target="_blank" href="https://slack.com/"><img src="https://user-images.githubusercontent.com/67786803/170409326-f2a0a772-236a-49a5-8dcc-6b4bf1ea881d.png?style=for-the-badge&logo=git&logoColor=white" width="130" height=52"></img></a>

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
     #### Matrix Factorization (MF)
     -    SVD
     <p align="center">
          <img src="https://user-images.githubusercontent.com/67786803/170715796-d86de28e-5502-43b5-be38-96b666e866bc.png"
     width="300" height="47"> 
     </p>

     -    SVD++
     <p align="center">
          <img src="https://user-images.githubusercontent.com/67786803/170715850-0508b57c-d55b-47e5-b2a2-e1ea5ca6567f.png"
     width="516" height="101">
     </p>
   - Offline evaluation
     -    'RMSE' as metric for offline evaluation
 ### 2. Code integrity checks with uni-test
   - The process is integrated on Jenkins pipeline, which runs automatically.
   - The result can be identified in a coverage report format on Jenkins
     <p align="center">
          <img src="https://user-images.githubusercontent.com/67786803/170418435-3edc2273-40ad-4ea7-a5e5-a188cb8197f9.png"
     width="426" height="140">
     </p>

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
<p align="right">
<img src="https://user-images.githubusercontent.com/67786803/170708922-6194593d-fae8-4c5d-8d2e-99b4357d9195.png" width="300" height="233" align="right">
</p>

   - Rancher
        - A complete container management platform that includes everything necessary for container management during the production process
   - Deploymeny components
        - Our system manages two recommendation models as different deployments in one cluster
        - Each deployment consists of two pods, one replica of the ohter, which distributes and processes tasks
     
### 2. Automatic Continuous Deployment with Jenkins
   - Automatic Continuous Deployment with Jenkins
        - Extending our integration pipeline to model deployment
        - We leverage jenkins to transmit the deployment signal to the Rancher
        - Whenever committed to Github, the pipeline is executed:
             - Continuous Integration : Data fetching, Data preprocessing, Model retraining
             - Continuous Deployment : Build docker images, Push images to docker repo
             - Model deployment : Pull docker images for retrained models and redeploy it through Rancher
<p align="center">
<img src="https://user-images.githubusercontent.com/67786803/170709744-b2dfa2f5-370e-42fe-b0b4-1e1a65fab8b3.png" width="600" height="173" align="center">
</p>
     
   - Zero downtime for model redeployment
<p align="right">
<img src="https://user-images.githubusercontent.com/67786803/170711032-e538c269-8bd4-45aa-826c-75b5ffb5328a.png" width="200" height="152" align="right">
</p>
    
        - The new redeployment also has 2 pods with replica
        - After one new pod is deployment, one existing pod is terminated
        - After a new pod is deployed again, the remaining existing pod is also terminated --> ZERO DWONTIME in the process of deploying the retrained models
   - All these process are stable controlled under the Rancher platform
     
### 3. Monitoring
   - Monitoring infrastructure
        - Prometheus, Grafana and Node Exporter to monitor our infrastructure
          - Memory usage
          - CPU usage
          - Latency time in flask
          - Model quality
     
<p align="center">
<img src="https://user-images.githubusercontent.com/67786803/170711375-067be272-02ab-40dc-8c23-3076e5b5006c.png" width="600" height="134" align="center">
</p> 
        - Sending alerts to our slack #alert channel
<p align="center">
<img src="https://user-images.githubusercontent.com/67786803/170711522-12029884-5f45-4c65-93ad-bf9016fbe021.png" width="450" height="214" align="center">
</p> 
     
### 4. Versioning and tracking provenance
   - Provenance
     - DVC
        - An open-source version control system
        - DVC stores the information of dataset and the model in .dvc format
     - Process
        - Track modification --> Add changes to git --> push git tag
<p align="center">
<img src="https://user-images.githubusercontent.com/67786803/170713168-f51748a0-5976-4fcf-b632-3936e4bef8cb.png" width="450" height="248" align="center">
</p> 

## Conclusion
   - Collect data from Kafka Streaming and data preprocessing for movie recommendation model training
   - Deploy and measure a model inference service
   - Build and operate infrastructures
     - A continuous integration infrastructure for evaluate a model in production
     - A monitoring infrastructure for the system health and model quality
     - A continuous deployment infrasturcture for automatic periodic retraining and versioning
   - Design and implement a monitoring strategy to detect possible issues in ML systems
