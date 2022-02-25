import json
import requests


def get_vimeo_folders():
	print('\n'+' Getting video folders '.center(100,':'))
	headers = headers = {'authorization': 'Bearer '+"d287c2575ecf5ba949efe3eaa4a98b64"}
	url = 'https://api.vimeo.com/users/{user_id}/projects'.format(user_id="133815660")
	folders = {}
	folders_set = set()
	folders_counter = 0
	counter = 1

	while True:
		query = {'per_page':50, 'page':counter}

		response = requests.get(url, headers=headers, params=query)
		json_response = json.loads(response.content)

		if (json_response['total'] > 0):
			for record in json_response['data']:
				folders[record['name']] = record['uri'][record['uri'].rindex('/')+1:len(record['uri'])]
				folders_set.add(record['name'])


		folders_counter += len(json_response['data'])
		print('IN PROGRESS !! {folders} folders fetched out of {total_folders}'.format(folders=folders_counter, total_folders=json_response['total']))
		counter += 1

		if (folders_counter >=  json_response['total']):
			break

	return folders,folders_set

if __name__ == "__main__":
	folders,folders_set = get_vimeo_folders()
	print(len(folders))
	print(len(folders_set))
	videos_list = {"Shikha Soni (shikhasoni225@gmail.com)":["/videos/662763093"]}
	for record in videos_list:
		if record not in folders:
			print("Error")
		else: print("Success")