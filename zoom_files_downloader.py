# -*- coding: utf-8 -*-
import os
import sys
import requests
import csv
import json
import wget
import os.path
import urllib.parse
from os import path
from utils import Utils

def download_zoom_files(records_list, filename):
	print('\n'+' Downloading meetings files '.center(100,':')+'\n')

	for index, record in enumerate(records_list):
		if not os.path.exists(str(record['file_path'])):
			os.makedirs(str(record['file_path']))

		print(record['file_path']+record['file_name'])

		if (path.exists(record['file_path']+record['file_name'])):
			print(' File already downloaded! '.center(100,':')+'\n')
			record["status"]="downloaded"
			continue
		try:
			print('Lets download: {download_url}'.format(download_url=str(record['download_url'])))
			wget.download(str(record['download_url']),str(record['file_path']+record['file_name']))
			record["status"]="downloaded"
		except Exception as e:
			print('Exception '+e)
			if record["status"] != "downloaded":
				record["status"]="listed"
		print('\n')
	return records_list

if __name__ == "__main__":
	utils = Utils()
	files = utils.get_records(sys.argv, 'zoom_files_downloader.py')

	downloaded_files = download_zoom_files(files, utils.output_file)
	utils.save_csv(downloaded_files, utils.output_file)

	print(' Script finished! '.center(100,':'))
