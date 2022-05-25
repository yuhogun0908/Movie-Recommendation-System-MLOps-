import sys
#sys.path.append("/home/yoonseoh/group-project-s22-k-avengers/Milestone2/exercise/")

from Data_Management import Process_RawData
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    # Process_RawData
    parser.add_argument("--kafka_dir_path", type=str, required=True,
                        help="A directory path containing Kafka streaming data")

    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    RawData = Process_RawData.Process_RawData(kafka_dir_path= args.kafka_dir_path)
    RawData.data_save()
    latest_dir_name = RawData.get_latest_path()
    if latest_dir_name == str(-1):
        RawData.del_prev_save_dir(dir_name = latest_dir_name)
    RawData.set_latest_path()
    
    # latest 폴더에 있는거 안에 다 지우고, 새로운거 복사 넣기
    #RawData.del_prev_save_dir(dir_name = "latest")
    #RawData.copy_latest_directory()


if __name__ == "__main__":
    main()