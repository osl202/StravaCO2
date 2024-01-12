
import requests

url = "https://www.carboninterface.com/api/v1/estimates"
headers = {
    "Authorization": "Bearer API_KEY",
    "Content-Type": "application/json"
}

data = {
      "type": "vehicle",
      "distance_unit": "mi",
      "distance_value": STRAVA_DISTANCE,
      "vehicle_model_id": "7268a9b7-17e8-4c8d-acca-57059252afe9"   # Toyota Corolla  
}

response = requests.post(url, headers=headers, json=data)

print(response.status_code)
print(response.json())