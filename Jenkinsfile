pipeline {
  agent any
  stages {
    stage('unit-1') {
      steps {
        sh '''pwd
pip3 install matplotlib
pip3 install numpy

echo \'unit 1\'

coverage run --omit=\'/usr/lib*\' /home/team24/group-project-s22-k-avengers/Milestone2/utils/test_data_quality.py

coverage report

echo \'Finished coverage report\''''
      }
    }

    stage('unit-2') {
      steps {
        sh '''echo \'unit 2\'

pwd

#PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline coverage run --omit=\'/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline/Data_Management/*, /home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline/path/*\' /home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline/For_Jenkins/test_step1.py

#coverage report

echo \'Finished coverage report\''''
      }
    }

    stage('unit-3') {
      steps {
        sh '''echo \'unit 3\'
#PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline coverage run --omit=\'/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline/Data_Management/*, /home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline/path/*, /usr/lib/*\' /home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline/For_Jenkins/test_step2.py

#coverage report

echo \'Finished coverage report\''''
      }
    }

    stage('unit-4') {
      steps {
        sh '''echo \'unit 4\'

#PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline coverage run --omit=\'/usr/lib/*, /home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline/RecSys_Management/*, /home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline/path/*, /usr/lib/*\' /home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline/For_Jenkins/test_step3.py --dataset_dir_path /home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline/DB/CORPUS/unittest/data_split

#coverage report

echo \'Finished coverage report\''''
      }
    }

    stage('unit-5') {
      steps {
        sh '''echo \'unit 5\'

#coverage run --omit=\'/usr/lib*\' /home/team24/group-project-s22-k-avengers/Milestone2/utils/test_online_eval.py
#coverage report

echo \'Finished coverage report\''''
      }
    }

    stage('Data Preprocessing') {
      steps {
        sh '''echo \'######   Data Preprocessing    #######\'

echo \'STEP1: Fetch Dataset from Kafka Storage\'
#PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline     python3 /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Model_pipeline/For_Jenkins/step1_fetch_dataset.py --kafka_dir_path /home/yoonseoh/Development/tmp_data
#PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline     python3 /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Model_pipeline/For_Jenkins/step1_fetch_dataset.py --kafka_dir_path /home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data


echo \'STEP2: Build Corpus\'
#PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline     python3 /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Model_pipeline/For_Jenkins/step2_build_corpus.py
'''
      }
    }

    stage('Model Retraining') {
      steps {
        sh '''echo \'######   Model Retraining    #######\'

echo \'STEP3: Model Training...\'
echo \'  STEP3-1: SVD Model Training\'
#PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline     python3 /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Model_pipeline/For_Jenkins/step3_model_training.py --model_name svd --n_epoch 17


echo \'  STEP3-2: SVDPP Model Training\'
#PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline    python3 /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Model_pipeline/For_Jenkins/step3_model_training.py --model_name svdpp --n_epochs 25


echo \'STEP4: Offline Evaluation...\'
echo \'   STEP4-1: SVD Model Offline Evaluation\'
#PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline    python3 /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Model_pipeline/For_Jenkins/step4_offline_evaluation.py --model_name svd --off_eval_save_path /home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/results_offline_svd.json

echo \'   STEP4-2: SVDPP Model Offline Evaluation\'
#PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline    python3 /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Model_pipeline/For_Jenkins/step4_offline_evaluation.py --model_name svdpp --off_eval_save_path /home/team24/group-project-s22-k-avengers/Milestone2/Kafka/data/results_offline_svdpp.json
'''
      }
    }

    stage('Containerization') {
      steps {
        sh '''echo \'######   Containerization    #######\'

echo \'STEP5: Prepare for Containeriztion\'

echo "   * Yoon\'s Docker Hub Login*"
docker login -u yoonseokheo -p Dbstjr419@ https://registry.hub.docker.com

echo \'   STEP5-1: SVD RecSys Containerization...\'
PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline    python3 /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Model_pipeline/For_Jenkins/step5_copy_for_docker.py --model_name svd

cd /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Deployment/Docker_SVD
echo "		>> Current Location"
pwd

echo "		>> SVD image build"
docker build -t m3:svd .
docker tag m3:svd registry.hub.docker.com/yoonseokheo/m3:svd

echo "		>> Check Dockerhub yoonseokheo/m3:svd"
docker push registry.hub.docker.com/yoonseokheo/m3:svd

echo ""
echo \'   STEP5-2: SVDPP...\'
PYTHONPATH=/home/team24/group-project-s22-k-avengers/Milestone3/Model_pipeline    python3 /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Model_pipeline/For_Jenkins/step5_copy_for_docker.py --model_name svdpp

cd /var/lib/jenkins/workspace/M3_Master_Pipeline_master/Milestone3/Deployment/Docker_SVDPP
echo "		>> Current Location"
pwd

echo "		>> SVDPP image build"
docker build -t m3:svdpp .
docker tag m3:svdpp registry.hub.docker.com/yoonseokheo/m3:svdpp

echo "		>> Check Dockerhub yoonseokheo/m3:svdpp"
docker push registry.hub.docker.com/yoonseokheo/m3:svdpp'''
      }
    }

    stage('Deployment') {
      steps {
        sh '''echo \'######   Deployment    #######\'

echo "   Step6-1: Rancher:m3svd"
kubectl rollout restart deployment m3svd

echo "   Step6-2: Rancher:m3svdpp"
kubectl rollout restart deployment m3svdpp'''
      }
    }

    stage('Online Evaluation') {
      steps {
        sh '''chmod -R 777 .

python3 /home/team24/group-project-s22-k-avengers/Milestone2/utils/online_eval.py
'''
      }
    }

  }
}