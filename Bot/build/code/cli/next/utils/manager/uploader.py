# utils\manager\uploader.py
import os
import subprocess
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST')
PSWD = os.getenv('PSWD')
USER = os.getenv('USER')


class FTPClient:
    def __init__(self, host, username, password):
        self.ftp = FTP(host)
        self.ftp.login(username, password)

    def list_files(self, path='.'):
        """List files in the given directory on the FTP server."""
        return self.ftp.nlst(path)

    def upload_file(self, local_file_path, remote_file_path):
        """Upload a file to the FTP server."""
        with open(local_file_path, 'rb') as local_file:
            self.ftp.storbinary(f'STOR {remote_file_path}', local_file)

    def download_file(self, remote_file_path, local_file_path):
        """Download a file from the FTP server."""
        with open(local_file_path, 'wb') as local_file:
            self.ftp.retrbinary(f'RETR {remote_file_path}', local_file.write)

    def delete_file(self, remote_file_path):
        """Delete a file on the FTP server."""
        self.ftp.delete(remote_file_path)

    def close(self):
        """Close the FTP connection."""
        self.ftp.quit()

    def create_directory(self, directory_name):
        self.ftp.mkd(directory_name)

    def remove_directory(self, directory_name):
        self.ftp.rmd(directory_name)

    def change_directory(self, directory_path):
        self.ftp.cwd(directory_path)

    def upload_directory(self, local_path, remote_path):
        if not os.path.isdir(local_path):
            raise ValueError(f"{local_path} is not a directory")

        if remote_path not in self.list_files():
            self.create_directory(remote_path)
        self.change_directory(remote_path)

        for item in os.listdir(local_path):
            local_item = os.path.join(local_path, item)
            if os.path.isfile(local_item):
                self.upload_file(local_item, item)
            elif os.path.isdir(local_item):
                self.upload_directory(local_item, item)

    def delete_directory(self, remote_path):
        # Ensure we are not trying to delete special directory references
        if remote_path in [".", ".."]:
            print("Skipping special directory:", remote_path)
            return

        try:
            # Change to the directory to check its contents
            self.change_directory(remote_path)

            # List all items in the directory
            items = self.list_files()

            for item in items:
                if item not in [".", ".."]:  # Skip special references
                    try:
                        # Try deleting the item as a file
                        self.delete_file(item)
                    except Exception as e:
                        # If it fails, it might be a directory, attempt recursive delete
                        try:
                            self.delete_directory(item)
                        except Exception as e:
                            print(f"Failed to delete {item}: {e}")

            # Change back to the parent directory to remove the now-empty directory
            self.change_directory("..")
            self.remove_directory(remote_path)

        except Exception as e:
            print(f"Failed to delete {remote_path}: {e}")


def main():
    ftp_client = FTPClient(host=HOST, username=USER, password=PSWD)

    while True:
        print("\nOptions:")
        # Removed option 1 for executing commands
        print("1. List Files")
        print("2. Upload File")
        print("3. Download File")
        print("4. Delete File")
        print("5. Create Directory")
        print("6. Remove Directory")
        print("7. Change Directory")
        print("8. Upload Directory")
        print("9. Delete Directory")
        print("10. Exit")  # Renumbered from 11 to 10

        choice = input("Enter your choice: ")

        # Adjusted choice numbers accordingly
        if choice == "1":
            files = ftp_client.list_files()
            print("\nFiles:")
            for file in files:
                print(file)
        elif choice == "2":
            local_path = input("Enter local file path: ")
            remote_path = input("Enter remote file path: ")
            ftp_client.upload_file(local_path, remote_path)
        elif choice == "3":
            remote_path = input("Enter remote file path: ")
            local_path = input("Enter local file path: ")
            ftp_client.download_file(remote_path, local_path)
        elif choice == "4":
            remote_path = input("Enter remote file path to delete: ")
            ftp_client.delete_file(remote_path)
        elif choice == "5":
            directory_name = input("Enter directory name to create: ")
            ftp_client.create_directory(directory_name)
        elif choice == "6":
            directory_name = input("Enter directory name to remove: ")
            ftp_client.remove_directory(directory_name)
        elif choice == "7":
            directory_path = input("Enter directory path to change to: ")
            ftp_client.change_directory(directory_path)
        elif choice == "8":
            local_path = input("Enter local directory path: ")
            remote_path = input("Enter remote directory path: ")
            ftp_client.upload_directory(local_path, remote_path)
        elif choice == "9":
            remote_path = input("Enter remote directory path to delete: ")
            ftp_client.delete_directory(remote_path)
        elif choice == "10":
            ftp_client.close()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
