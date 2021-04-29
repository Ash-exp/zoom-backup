import requests
import csv
import json
from utils import Utils


class Transcript:

	def __init__(self):
		self.utils = Utils()
   
	def update_outputfile(self, records, filename):
		print('\n'+' Checking video status from Vimeo '.center(100, ':'))

		with open(filename, mode='w') as f:
			writer = csv.writer(f)
			writer.writerow(self.utils.CSV_HEADER)

			for record in records:
				writer.writerow(self.utils.get_record_row(record))

		return records


	def find_video_ID(self, records, meeting):
		for record in records:
			if record['meeting_uuid'] == meeting and record['file_extension'] == 'MP4':
				return record['vimeo_id'], record['file_name'],record['vimeo_status']
		return 0, 0, 0


	def get_transcript(self, url, filename):
		response = requests.request("GET", url)
		if response.status_code == 200:
			return response.content
		else:
			print('\n'+' Failed to Download {filename}. Response Status Code : {status}'.format(filename=filename, status=response.status_code).center(100, ':'))
			return 0


	def upload_zoom_transcript(self, records):
		print('\n'+' Backup transcript files from Zoom '.center(100, ':'))
		url = "https://api.vimeo.com"
		headers = {
			'Authorization': 'Bearer '+self.utils.vimeo_token,
			'Content-Type': 'application/json',
			'Accept': '*/*'
		}

		for record in records:
			if record['file_extension'] == 'VTT' and not "?type=cc" in record['download_url']:
				if record['vimeo_status'] != 'active':
					download_url = record['download_url'] + '?access_token=' + self.utils.zoom_token
					transcript = self.get_transcript(download_url, record['file_name'])
					if (transcript):
						print('\n'+' Getting the text track URI of {filename} '.format(filename=record['file_name']).center(100, ':'))
						video_id, video_name, status = self.find_video_ID(records, record['meeting_uuid'])
						if (video_id):
							_url = url+"/videos/"+video_id
							response = requests.request("GET", _url, headers=headers)
							json_response = json.loads(response.text)
							texttracks_uri = json_response["metadata"]["connections"]["texttracks"]["uri"]

							print('\n'+' Uploading {filename} '.format(filename=record['file_name']).center(100, ':'))
							body = {}

							body['type'] = "subtitles"
							body['language'] = "en"
							body['name'] = record['file_name']

							_url = url+texttracks_uri
							response = requests.request("POST", _url, headers=headers, data=json.dumps(body))
							json_response = json.loads(response.text)

							if response.status_code == 201:

								upload_link = json_response["link"]
								patch_link = url+json_response["uri"]
								response = requests.request(
									"PUT", upload_link, headers=headers, data=transcript)

								if response.status_code == 200:
									response = requests.request(
										"PATCH", patch_link, headers=headers, data=json.dumps({"active": True}))
									if response.status_code == 200:
										record['vimeo_status'] = "active"
										print('\n'+' Successfully Uploaded {filename}'.format(filename=record['file_name']))
									else:
										record['vimeo_status'] = "not active"
										print('\n'+' Failed to Activate {filename}. Response Status Code : {status}'.format(filename=record['file_name'], status=response.status_code).center(100, ':'))

								else: print('\n'+' Failed to Upload {filename}. Response Status Code : {status}'.format(filename=record['file_name'], status=response.status_code).center(100, ':'))

							else: print('\n'+' Failed Post request to texttracks_uri {filename}. Response Status Code : {status}'.format(filename=record['file_name'], status=response.status_code).center(100, ':'))

						else: print('\n'+'Record {filename} needs to be uploaded first! '.format(filename=video_name))

				else: print('\n'+'Transcript {filename} is already uploaded! '.format(filename=record['file_name']))

		return records

