# -*- coding: utf-8 -*-
#This script get videos from Zoom and makes the backup into a vimeo account using pull approach

import os
import sys
import requests
import urllib
import json
from utils import Utils

def delete_zoom_files(records):
	query = {"action":"trash"}
	headers = {'authorization': 'Bearer '+utils.zoom_token}

	print('\n'+' Moving to trash files '.center(100,':'))
	for record in records:
		url = "https://api.zoom.us/v2/meetings/{meeting_id}/recordings/{record_id}"
		url=url.format( meeting_id=urllib.parse.quote(record['meeting_uuid']),record_id=urllib.parse.quote(record['record_id']) )

		#if utils.input_type == 2 and (record['status']=='downloaded' or record['vimeo_status']=='available'):
		response = requests.request("DELETE", url, headers=headers, params=query)
		if response.status_code != 204:
			json_response = json.loads(response.content)
			print(json_response)
		else:
			print(' Deleting file {filename} in meeting {meetingid} '.format(filename=record['file_name'], meetingid=record['meeting_id']).center(100,':'))
			record['status']='deleted'

	return records

if __name__ == "__main__":
	utils = Utils()
	files = utils.get_records(sys.argv, 'zoom_files_delete.py')
	files = delete_zoom_files(files)
	utils.save_csv(files, utils.output_file)
