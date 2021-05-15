import boto3
import urllib3
from s3config import AccessKeyID, SecretAccessKey

# def lambda_handler():  # event, context
url='https://practee.zoom.us/rec/download/7XnZ7XB7n-G18fg116G9O58LJ4BFK1GwcY4mzSF-wzhnBGnzEftWGwx6FlvdKaDYLXHSFhyFXHZOEW9M.jAzCe7jdoBxpg8SR?access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOm51bGwsImlzcyI6IlJIUUhDZkRpUkp1QTZhdWczT0xiVGciLCJleHAiOjI1MzQ2NTM4MDAsImlhdCI6MTYxOTQ3ODMxMn0.Lf_3TmayahoiinSwAXBj-qAKq7hu2sq-6AjTDPa-Oh4' # put your url here
bucket = 'zoom-vimeo-back-up' #your s3 bucket
key = 'May-15-2021/mentor-student/tisra-vedio.mp4' #your desired s3 path or filename
s3=boto3.client('s3', aws_access_key_id = AccessKeyID, aws_secret_access_key = SecretAccessKey)
http=urllib3.PoolManager()
s3.upload_fileobj(http.request('GET', url,preload_content=False), bucket, key)
