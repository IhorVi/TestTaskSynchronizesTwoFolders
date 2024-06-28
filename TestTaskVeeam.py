import os
import time
import shutil
import argparse
import hashlib

def synch_folders(source, replica, log):
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        replica_root = os.path.join(replica, relative_path)

        os.makedirs(replica_root, exist_ok=True)
        log_message(log, f"Created directory: {os.path.relpath(replica_root, replica)}")

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)

            if md5(source_file) != md5(replica_file):
                copy_file(source_file, replica_file, log)

    for root, dirs, files in os.walk(replica, topdown=False):
        relative_path = os.path.relpath(root, replica)
        source_root = os.path.join(source, relative_path)

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_root, file)
            if not os.path.exists(source_file):
                os.remove(replica_file)
                log_message(log, f"Removed file: {os.path.relpath(replica_file, replica)}")

        for dir in dirs:
            replica_dir = os.path.join(root, dir)
            source_dir = os.path.join(source_root, dir)
            if not os.path.exists(source_dir):
                shutil.rmtree(replica_dir)
                log_message(log, f"Removed directory: {os.path.relpath(replica_dir, replica)}")

def log_message(log, message):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    log.write(f"[{current_time}] {message}\n")
    log.flush()
    print(message)

def md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def copy_file(source_file, replica_file, log):
    shutil.copy2(source_file, replica_file)
    log_message(log, f"Copied file: {os.path.basename(source_file)} to {os.path.basename(replica_file)}")

def main():
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("--source", required=True, help="C:/Users/TestUserPC/Desktop/source)")
    parser.add_argument("--replica", required=True, help="C:/Users/TestUserPC/Desktop/replica)")
    parser.add_argument("--interval", type=int, default=600, help="Synchronization interval in seconds")
    parser.add_argument("--log", required=True, help="C:/Users/TestUserPC/Desktop/logfile.txt")
    args = parser.parse_args()

    source_folder = args.source
    replica_folder = args.replica
    log_file_path = args.log

if __name__ == "__main__":
    main()








