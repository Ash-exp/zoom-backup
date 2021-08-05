# -*- coding: utf-8 -*-
#This script get videos from Zoom and makes the backup into a vimeo account using pull approach

import os
import sys
import requests
import csv
import json
import os.path
import time
from os import path
from datetime import date
from datetime import timedelta
from time import time
from time import sleep
from utils import Utils
from s3util import S3backup
from transcript_uploader import Transcript
from zoom_files_delete import Zoom
from report_mailer import Mailer

#constants
START_WAIT = 7
VIDEO_DESCRIPTION = 'Practee Zoom Session: {topic} on {start_date}'

def fibo(n):
	if n <= 1:
		return n
	else:
		return(fibo(n-1) + fibo(n-2))

def create_vimeo_folder(foldername):
	print('\n'+' Create Vimeo Folder {foldername} '.format(foldername=foldername).center(100,':'))
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}
	url = 'https://api.vimeo.com/users/{user_id}/projects'.format(user_id=utils.vimeo_userid)
	body = {}
	body['name']=foldername

	response = requests.post(url, headers=headers, json=body)
	folder = {}

	if response.status_code == 201:
		json_response = json.loads(response.content)
		print('Folder {foldername} created!'.format(foldername=foldername))
		folder[foldername] = json_response['uri'][json_response['uri'].rindex('/')+1:len(json_response['uri'])]

	return folder

def get_vimeo_folders():
	print('\n'+' Getting video folders '.center(100,':'))
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}
	url = 'https://api.vimeo.com/users/{user_id}/projects'.format(user_id=utils.vimeo_userid)
	folders = {}
	folders_counter = 0
	counter = 1

	while True:
		query = {'per_page':50, 'page':counter}

		response = requests.get(url, headers=headers, params=query)
		json_response = json.loads(response.content)

		if (json_response['total'] > 0):
			for record in json_response['data']:
				folders[record['name']] = record['uri'][record['uri'].rindex('/')+1:len(record['uri'])]

		folders_counter += len(json_response['data'])
		print('IN PROGRESS !! {folders} folders fetched out of {total_folders}'.format(folders=folders_counter, total_folders=json_response['total']))
		counter += 1

		if (folders_counter >=  json_response['total']):
			break

	return folders

def request_move_videos_to_folder(videos_list, record, folder_id):
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}
	url='https://api.vimeo.com/users/{user_id}/projects/{project_id}/videos'
	videos_str = ','.join(videos_list[record])
	query = {'uris':videos_str}
	url = url.format(user_id=utils.vimeo_userid, project_id=folder_id)
	response = requests.put(url, headers=headers, params=query)

	if response.status_code != 204:
		print('Error trying to move videos videos {videos} to folder {folder}'.format(videos=videos_str, folder=record))
	else:
		print('Moved videos {videos} to folder {folder}'.format(videos=videos_list[record], folder=record))


def move_videos_to_folder(records):
	print('\n'+' Moving videos to folder '.center(100,':'))

	folders = get_vimeo_folders()
	videos_list = {}
	for record in records:
		if record['file_extension'] == 'MP4':
			if record['vimeo_folder'] not in videos_list:
				videos_list[record['vimeo_folder'].rstrip()] = []
			videos_list[record['vimeo_folder'].rstrip()].append(record['vimeo_uri'])

	# Looking for the specified folder in vimeo
	for record in videos_list:
		if record not in folders:
			print (record + ' NOT FOUND in vimeo folders, lets create the folder')
			new_folder = create_vimeo_folder(record)
			if len(new_folder) == 0:
				print('Not created folder')
			else:
				folders[record] = new_folder[record]
				request_move_videos_to_folder(videos_list, record, folders[record])
		else:
			request_move_videos_to_folder(videos_list, record, folders[record])


def set_embeded_presets(record):
	print('\n'+' Setting embedded settings '.center(100,':'))
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}
	url = 'https://api.vimeo.com/videos/{video_id}/presets/{preset_id}'.format(video_id=record['vimeo_id'], preset_id=utils.vimeo_preset_id)

	response = requests.put(url, headers=headers)
	if response.status_code == 204:
		record['vimeo_embedded'] = True

	return record


def check_upload_videos(records, filename):
	print('\n'+' Checking video status from Vimeo '.center(100,':'))
	global START_WAIT
	unavailablecount = 0
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}

	with open(filename, mode='w') as f:
		writer = csv.writer(f)
		writer.writerow(utils.CSV_HEADER)

		for record in records:
			if record['file_extension'] == 'MP4':
				if record['vimeo_status']!='available' and record['vimeo_status']!='error' and record['vimeo_uri'] !='':
					url = "https://api.vimeo.com/me/"+record['vimeo_uri']
					print('\n'+' Checking {filename} '.format(filename=record['file_name']).center(100,':'))
					response = requests.get(url, headers=headers)
					json_response = json.loads(response.text)

					record['vimeo_status'] = json_response['status']
					if record['vimeo_status'] == 'available' or record['vimeo_status'] == 'transcoding':
						#print(json_response)
						if record['vimeo_embedded'] == 'False':
							record = set_embeded_presets(record)

						if record['vimeo_status'] == 'available':
							print ('Available %s video!' %record['file_name'])
						else:
							print ('Transcoding video %s... almost ready' %record['file_name'])

					elif record['vimeo_status'] != 'error':
						if record['vimeo_embedded'] == 'False':
							record = set_embeded_presets(record)

						print('Not yet available video ' + record['file_name']+' lets try in ' +str(fibo(START_WAIT))+' seconds')
						unavailablecount += 1
					else:
						print('Error status for video %s' %record['file_name'] )
			writer.writerow(utils.get_record_row(record))

		if unavailablecount > 0:
			sleep(fibo(START_WAIT))
			START_WAIT +=1
			check_upload_videos(records, filename)

	return records

def upload_zoom_videos(records):
	print('\n'+' Backup video files from Zoom '.center(100,':'))
	url = "https://api.vimeo.com/me/videos"
	headers = {
		'Authorization': 'Bearer '+utils.vimeo_token,
		'Content-Type': 'application/json',
		'Accept': '*/*'
	}

	for record in records:
		if record['file_extension'] == 'MP4':
			if record['vimeo_status'] != 'available' and record['vimeo_status'] != 'transcoding' and record['vimeo_status'] != 'transcode_starting':
				print('\n'+' Uploading {filename} '.format(filename=record['file_name']).center(100,':'))
				body = {}
				body['name']=record['topic']+record['recording_start'].split("T")[0]+'.'+record['file_extension']
				body['description']=VIDEO_DESCRIPTION.format(topic=record['topic'],start_date=record['recording_start'])

				privacy= {}
				if (utils.vimeo_password["active"]):
					privacy['view']='password'
					privacy['password']=utils.vimeo_password["password"]
				else :
					privacy['view']='nobody'
				privacy['embed']='public'
				privacy['comments']='nobody'
				privacy['download']='false'

				upload = {}
				upload['approach']='pull'
				upload['size'] = record['file_size']
				upload['link']= record['download_url']+"?access_token="+utils.zoom_token

				body['upload']=upload
				body['privacy']=privacy
				response = requests.request("POST",url, headers=headers, data=json.dumps(body))
				if response.status_code == 201:
					json_response = json.loads(response.content)
					record['vimeo_uri'] = json_response['uri']
					record['vimeo_status'] = json_response['upload']['status']
					record['vimeo_transcode_status'] = json_response['transcode']['status']
					record['vimeo_id']= record['vimeo_uri'][8:len(record['vimeo_uri'])]
			else:
				print('\n'+'Record {filename} already or almost uploaded! '.format(filename=record['file_name']))

	return records

if __name__ == "__main__":
	# date = date.today()-timedelta(days=1)
	# arg = ['vimeo_uploader.py', '--daterange', str(date), str(date), '--outputfile', 'outputfile.csv']
	# arg = ['vimeo_uploader.py', '--inputfile', 'inputfile.csv', '--outputfile', 'outputfile.csv']

	utils = Utils()
	files = utils.get_records(sys.argv, 'vimeo_uploader.py')
	# files = utils.get_records(arg, 'vimeo_uploader.py')

	if utils.input_type == 1:
		files = check_upload_videos(files, utils.input_file)

	if (utils.s3_integrate["active"]):
		files = S3backup().upload(files)

	files = upload_zoom_videos(files)
	files = check_upload_videos(files, utils.output_file)

	# utils.output_file = 'outputfile.csv'
	# files = utils.load_videos_data('outputfile.csv')

	files = Transcript().upload_zoom_transcript(files)
	files = Transcript().update_outputfile(files, utils.output_file)
	move_videos_to_folder(files)

	if (utils.zoom_recordings_delete):
		files = Zoom().delete_zoom_files(files)
		utils.save_csv(files, utils.output_file)

	if (utils.report_mailer["active"]):
		try:
			Mailer().send_mail(utils.report_mailer["mail-to"])
		except Exception as e:
			print(' MAIL FAILED '.center(100,':'))
			print(e)

	print('\n'+' Script finished! '.center(100,':'))
