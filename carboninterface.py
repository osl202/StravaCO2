import requests

class Emissions:

    def __init__(self):
        self.api_calls = 0
        
    def emissions(self, distance):

        url = "https://www.carboninterface.com/api/v1/estimates"

        headers = {
            "Authorization": "Bearer API_KEY",
            "Content-Type": "application/json"
        }

        self.api_calls += 1
        print(self.api_calls)
        if self.api_calls > 50:
            print("No more calls!")
    
        data = {
        "type": "vehicle",
        "distance_unit": "km",
        "distance_value": distance,
        "vehicle_model_id": "7268a9b7-17e8-4c8d-acca-57059252afe9"   # Toyota Corolla  
        }

        response = requests.post(url, headers=headers, json=data)

        return response.json()['data']['attributes']['carbon_kg']

