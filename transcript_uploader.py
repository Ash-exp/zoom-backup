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


	def find_transcript_record(self, records, meeting):
		sub_str = "?type=cc"
		transcript = {}
		for record in records:
			if record['meeting_uuid'] == meeting and record['file_extension'] == 'VTT' and sub_str in record['download_url']:
				return record
			elif record['meeting_uuid'] == meeting and record['file_extension'] == 'VTT' and not sub_str in record['download_url']:
				transcript = record
		return transcript


	def get_transcript(self, url, filename):
		query = {"access_token" : self.utils.zoom_token}
		response = requests.request("GET", url, params=query)
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
		failed_list = []
		for record in records:
			if record['file_extension'] == 'MP4' and record['vimeo_status'] != 'pending' and record['vimeo_status'] != 'error':
				transcript_record = self.find_transcript_record(records, record['meeting_uuid'])
				if transcript_record :
					if transcript_record['vimeo_status'] != 'active':
						transcript = self.get_transcript(transcript_record['download_url'], transcript_record['file_name'])
						if (transcript):
							if (record['vimeo_id']):
								_url = url+"/videos/"+record['vimeo_id']
								response = requests.request("GET", _url, headers=headers)
								json_response = json.loads(response.text)
								texttracks_uri = json_response["metadata"]["connections"]["texttracks"]["uri"]

								print('\n'+' Uploading {filename} '.format(filename=transcript_record['file_name']).center(100, ':'))
								body = {}

								body['type'] = "subtitles"
								body['language'] = "en"
								body['name'] = transcript_record['file_name']

								_url = url+texttracks_uri
								response = requests.request("POST", _url, headers=headers, data=json.dumps(body))
								json_response = json.loads(response.text)

								if response.status_code == 201:

									upload_link = json_response["link"]
									patch_link = url+json_response["uri"]
									response = requests.request("PUT", upload_link, headers=headers, data=transcript)

									if response.status_code == 200:
										response = requests.request("PATCH", patch_link, headers=headers, data=json.dumps({"active": True}))
										if response.status_code == 200:
											transcript_record['vimeo_status'] = "active"
											print(' Successfully Uploaded {filename}'.format(filename=transcript_record['file_name']))
										else:
											transcript_record['vimeo_status'] = "not active"
											print('\n'+' Failed to Activate {filename}. Response Status Code : {status}'.format(filename=transcript_record['file_name'], status=response.status_code).center(100, ':'))

									else: print('\n'+' Failed to Upload {filename}. Response Status Code : {status}'.format(filename=transcript_record['file_name'], status=response.status_code).center(100, ':'))

								else: print('\n'+' Failed Post request to texttracks_uri {filename}. Response Status Code : {status}'.format(filename=transcript_record['file_name'], status=response.status_code).center(100, ':'))

							else: print('\n'+'Record {filename} needs to be uploaded first! '.format(filename=record['file_name']))

					else: print('\n'+'Transcript {filename} is already uploaded! '.format(filename=transcript_record['file_name']))
				else:
					failed_list.append({'folder':record['vimeo_folder'], 'file': record['file_name']})
					print('\n'+'No Transcript to upload for {filename} ! '.format(filename=record['file_name']))

		if failed_list:
			with open("No_Subtitle_Videos.txt", 'w') as f: 
				for line in failed_list
					f.write(line['folder']+"\t"+line['file']+"\n")

		return records

