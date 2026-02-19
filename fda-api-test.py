import requests
import json


#  As a user, I want to be able to see if the drug I am looking for is in
#  shortage, so that I can make informed decisions about my healthcare.

response = requests.get("https://api.fda.gov/drug/shortages.json?limit=100")


if response.status_code == 200:
    data = response.json()
    print(data)
    with open('data.json', 'w') as outf:
        json.dump(data, outf, indent=4)
else:
    print(f"Error: {response.status_code}")