import requests

def make_api_request(path, access_token):
	base_url = "https://www.strava.com/api/v3/"
	return requests.get(base_url + path, headers={'Authorization': f'Bearer {access_token}'})

def athlete(access_token):
	req = make_api_request('/athlete', access_token)
	return req.json()
