import boto3
import botocore
import os
import sys
import zipfile

S3_BUCKET = os.environ.get('NONA_S3_BUCKET', None)
STAGE = os.environ.get('NONA_STAGE', 'development')
VERSION = os.environ.get('NONA_BACKUP_VERSION', 'latest')
DATA_PATH = os.environ.get('NONA_DATA_PATH', '/data')

if not S3_BUCKET:
    sys.exit(1)

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file),
                    os.path.join(path, '..'))
            )


def zipit(dir_list, zip_name):
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for dir in dir_list:
        zipdir(dir, zipf)
    zipf.close()

def get_backup(source, destination):
    try:
        s3 = boto3.resource('s3')
        s3.Bucket(S3_BUCKET).download_file(source, destination)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("File s3://{}/{} is missing".format(S3_BUCKET,source))
            return
        else:
            raise

def main():
    source = 'backup/{}/{}.zip'.format(STAGE, VERSION)
    destination = '/tmp/minecraft_data.zip'
    get_backup(source, destination)
    print('Downloaded latest server archive')

    zip_ref = zipfile.ZipFile('/tmp/minecraft_data.zip', 'r')
    zip_ref.extractall('/data')
    zip_ref.close()

    print('Extracted file to minecraft home')

if __name__ == "__main__":
    main()
