import boto3
import urllib3
import botocore
from utils import Utils

class S3backup:

	def __init__(self):
		self.utils = Utils()
	
	def upload(self, records):

		print('\n'+' Backup files from Zoom to AWS S3 '.center(100, ':'))
		query = {"access_token" : self.utils.zoom_token}
		failed_list = []

		for record in records:
			url = record['download_url'] # put your url here
			key = record['recording_start'].split("T")[0]+'/'+record['topic']+'/'+record['file_name'] #your desired s3 path or filename
			s3=boto3.client('s3', aws_access_key_id = self.utils.s3_integrate["AccessKeyID"], aws_secret_access_key = self.utils.s3_integrate["SecretAccessKey"])
			http=urllib3.PoolManager()
			try:
				s3.upload_fileobj(http.request('GET', url,fields=query,preload_content=False), self.utils.s3_integrate["bucket"], key)
				print ('Successfully uploaded %s file!' %record['file_name'])
			except botocore.exceptions.ClientError as e:
				if e.response['Error']['Code'] == "404":
					print("The object does not exist.")
				else:
					failed_list.append({'folder':record['vimeo_folder'], 'file': record['file_name']})
					print('\n'+'Failed to upload for {filename} ! '.format(filename=record['file_name']))

		if failed_list:
			with open("error.txt", 'w') as f: 
				f.write(' S3 Back-up Failed !! '.center(100, ':')+"\n")
				for line in failed_list:
					f.write(line['folder']+"\t"+line['file']+"\n")

		return records