import os
import sys
import json
import csv
import requests
from datetime import datetime
from datetime import timedelta

class Utils:
	CSV_HEADER = ["EMAIL","RECORD ID", "MEETING ID","MEETING UUID", "TOPIC","FILE NAME", "STATUS", "DOWNLOAD URL","PLAY URL", "RECORDING START", "RECORDING END","FILE PATH", "FILE SIZE", "FILE EXTENSION", "VIMEO ID", "VIMEO STATUS", "VIMEO URI", "VIMEO TRANSCODE STATUS", "VIMEO EMBEDDED", "VIMEO FOLDER"]

	def __init__(self):
		self.files = []
		self.load_config()


	def load_config(self):
		with open("config.json") as json_data_file:
		    data = json.load(json_data_file)

		self.zoom_token = data['zoom-token']
		self.vimeo_token = data['vimeo-token']
		self.vimeo_userid = data['vimeo-user-id']
		self.vimeo_preset_id = data["vimeo-preset-id"]

	def get_start_date(self):
		return self.start_date

	def get_end_date(self):
		return self.end_date

	def get_zoom_token(self):
		return self.zoom_token

	def get_vimeo_token(self):
		return self.vimeo_token

	def get_vimeo_userid(self):
		return self.vimeo_userid

	def get_vimeo_preset_id(self):
		return self.vimeo_preset_id

	def get_CSV_HEADER(self):
		return self.CSV_HEADER

	def get_files(self):
		return self.files

	def get_zoom_users(self):
		print(' Fetching user ids '.center(100,':'))

		url = "https://api.zoom.us/v2/users"
		query = {"page_size":"30","status":"active"}
		headers = headers = {'authorization': 'Bearer '+self.zoom_token}

		response = requests.request("GET", url, headers=headers, params=query)
		users = json.loads(response.text)
		return users

	def load_videos_data(self, filename):
		print(' Loading meetings files'.center(100,':'))
		records = []
		csvfile = open(filename, 'r')
		reader = csv.DictReader( csvfile, self.CSV_HEADER)
		for index, row in enumerate(reader):
			if index > 0:
				item = {}
				for record_name in self.CSV_HEADER:
					item[record_name.lower().replace(' ','_')] = row[record_name]
				records.append(item)
		return records

	def get_zoom_files(self, users, start_date, end_date):
		print(' Getting meetings list '.center(100,':'))

		url = "https://api.zoom.us/v2/users/"
		query = {"trash_type":"meeting_recordings","mc":"false","page_size":"100"}
		headers = {'Authorization': 'Bearer '+self.zoom_token}

		end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
		records_list = []
		index = 0

		for user in users['users']:
			_url = url + user['id']+'/recordings'
			from_date = datetime.strptime(start_date, '%Y-%m-%d').date()  #date(2020, 01, 01)
			to_date = from_date + timedelta(days=30)
			if to_date > end_date:
				to_date = end_date

			print('\n'+user['email'].center(100,':'))
			while to_date < end_date+timedelta(days=1):
				query["from"] = str(from_date)
				query["to"] = str(to_date)

				print(' [{start_date}] - [{end_date}] '.format(start_date=start_date, end_date=end_date).center(100,':'))
				# print(' ['+str(from_date)+'] - ['+str(to_date)+'] ')

				response = requests.request("GET", _url, headers=headers, params=query)
				json_response = json.loads(response.content)

				if json_response['total_records'] > 0:
					for meeting in json_response['meetings']:
						if meeting['duration'] < 2:
							continue
						if meeting['recording_count'] > 0:
							for recording in meeting['recording_files']:
								try:
									item = {}
									item['username'] = user['first_name']
									item['email'] = user['email']
									item['recording_start'] = recording['recording_start']
									item['recording_end'] = recording['recording_end']
									item['download_url'] = recording['download_url'] #urllib.parse.quote(recording['download_url'])
									try:
										item['play_url'] = recording['play_url']
									except KeyError:
										item['play_url'] = ""
									item['topic'] = meeting['topic']
									item['record_id'] = recording['id']
									item['meeting_id'] = meeting['id']
									item['meeting_uuid']=recording['meeting_id']
									item['status'] = 'listed'
									item['file_size'] = recording['file_size']
									item['file_extension'] = recording['file_extension']
									item['vimeo_id']=''
									item['vimeo_uri']=''
									item['vimeo_status']='pending'
									item['vimeo_transcode_status']='pending'
									item['vimeo_embedded'] = False
									item['vimeo_folder']=item['topic'][0:31]
									filename = datetime.strptime(item['recording_start'], '%Y-%m-%dT%H:%M:%SZ').strftime("GMT%Y%m%d-%H%M%S")+str(index) +'.'+str(item['file_extension'])
									item['file_name']=str(filename)
									filepath = './meetings/{username}/{topic}/'.format(username=item['username'],topic=item['topic'])
									item['file_path']=str(filepath)
									index += 1
									records_list.append(item)
								except:
									print("Something went wrong...")

				from_date = to_date + timedelta(days=1)
				to_date = to_date + timedelta(days=30)

				if (to_date > end_date) and ((to_date - timedelta(days=30)) != end_date):
					to_date = end_date

		return records_list

	def get_records(self, argv, scriptname):
		self.files = []
		params = ['--inputfile', '--daterange', '--outputfile']
		if len(argv) < 2:
			print('You must use: python {scriptname} --inputfile inputfile.csv --ouputfile outputfile.csv or python {scriptname} --rangedates yyyy-mm-dd yyyy-mm-dd --ouputfile ouputfile.csv'.format(scriptname=scriptname))
			exit()
		if argv[1] == params[0]:
			if len(argv) < 5:
				print('You must use: python {scriptname} --inputfile inputfile.csv --ouputfile outputfile.csv'.format(scriptname=scriptname))
				exit()
			else:
				if argv[3] != params[2]:
					print('Unknown parameter: ' + argv[3])
					exit()
				if not os.path.isfile(argv[2]):
					print('File does not exists: {inputfile}'.format(inputfile=argv[2]))
					exit()
				else:
					self.input_type = 1
					self.input_file = argv[2]
					self.output_file = argv[4]
					self.files = self.load_videos_data(argv[2])
		elif argv[1] == params[1]:
			if len(argv) < 6:
				print('You must use: python {scriptname} --rangedates yyyy-mm-dd yyyy-mm-dd --ouputfile ouputfile.csv'.format(scriptname=scriptname))
				exit()
			else:
				self.input_type = 2
				self.output_file = argv[5]
				self.start_date = argv[2]
				self.end_date = argv[3]
				self.users = self.get_zoom_users()
				self.files = self.get_zoom_files(self.users, self.start_date, self.end_date)
		else:
			print('Unknown parameter: '+argv[1])

		return self.files

	def get_record_row(self, record):
		row = []
		for record_name in self.CSV_HEADER:
			row.append(record[record_name.lower().replace(' ','_')])
		return row

	def save_csv(self, fileobject, filename):
		print('\n'+' Saving report {filename} '.format(filename=filename).center(100,':'))

		# if not os.path.exists('./reports'):
		# 	os.makedirs(str('./reports'))

		file_exists = os.path.isfile(filename)
		with open(filename, 'w') as f: #'a'
			writer = csv.writer(f)
			#if not file_exists:
			writer.writerow(self.CSV_HEADER)

			for record in fileobject:
				writer.writerow(self.get_record_row(record))
