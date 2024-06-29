import os
import time
import shutil
import argparse
from hashlib import md5
import logging

logger = logging.getLogger(__name__)

# Define the logging format as a variable
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def setup_logger(log_file_path):
    # Configure logging to file and console with the specified format
    logging.basicConfig(filename=log_file_path, encoding='utf-8', level=logging.DEBUG, format=LOG_FORMAT)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def sync_folders(source, replica):
    # Walk through the source directory
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        replica_root = os.path.join(replica, relative_path)

        # Create directories in the replica if they don't exist
        if not os.path.exists(replica_root):
            os.makedirs(replica_root)
            logger.info(f"Created directory: {replica_root}")

        # Check and copy files if needed
        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)

            sync_needed = False

            # Check if the file needs to be copied (new or modified)
            if not os.path.exists(replica_file):
                sync_needed = True
            elif get_md5(source_file) != get_md5(replica_file):
                sync_needed = True

            if sync_needed:
                copy_file(source_file, replica_file)

    # Walk through the replica directory to remove files and directories not present in the source
    for root, dirs, files in os.walk(replica, topdown=False):
        relative_path = os.path.relpath(root, replica)
        source_root = os.path.join(source, relative_path)

        # Remove files not in the source
        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_root, file)
            if not os.path.exists(source_file):
                os.remove(replica_file)
                logger.info(f"Removed file: {os.path.relpath(replica_file, replica)}")

        # Remove directories not in the source
        for d in dirs:
            replica_dir = os.path.join(root, d)
            source_dir = os.path.join(source_root, d)
            if not os.path.exists(source_dir):
                shutil.rmtree(replica_dir)
                logger.info(f"Removed directory: {os.path.relpath(replica_dir, replica)}")


def get_md5(file_path):
    # Calculate the MD5 hash of a file
    with open(file_path, "rb") as f:
        return md5(f.read()).hexdigest()


def copy_file(source_file, replica_file):
    # Copy the file and log the operation
    shutil.copy2(source_file, replica_file)
    logger.info(f"Copied file: {source_file} to {replica_file}")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("--source", required=True, help="Path to the source folder")
    parser.add_argument("--replica", required=True, help="Path to the replica folder")
    parser.add_argument("--interval", type=int, default=5, help="Synchronization interval in seconds")
    parser.add_argument("--log", required=True, help="Path to the log file")
    args = parser.parse_args()

    source_folder = args.source
    replica_folder = args.replica
    log_file_path = args.log

    # Setup logging
    setup_logger(log_file_path)

    logger.info("Starting synchronization process")
    while True:
        # Perform folder synchronization
        sync_folders(source_folder, replica_folder)
        # Wait for the specified interval before next synchronization
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
