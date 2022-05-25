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
    #RawData.data_save()

    RawData.del_prev_save_dir()
    RawData.data_save()
    RawData.set_latest_path()
    print(RawData.get_latest_path())

if __name__ == "__main__":
    main()