import json
import requests
url = "http://api.travelpayouts.com/v2/prices/latest"
def search(origin,destination,date):
    date = date.split(".")
    beginning_of_period = f"{date[2]}-{date[1]}-{date[0]}"
    data = {
    "currency": "rub",
    "origin": origin,
    "destination": destination,
    "beginning_of_period": beginning_of_period,
    "one_way": True,
    "limit": 1000,
    "sorting": "price" ,
    "token":"85962c655097d646b4d2e690453b148f"
    }
    #print(url + f'?{"&".join([f"{i}={j}" for i, j in data.items()])}')
    response = requests.get(url + f'?{"&".join([f"{i}={j}" for i, j in data.items()])}')
  
    response = json.loads(response.text)
    if response["success"]:
        for line in response["data"]:
            if line["depart_date"] == data["beginning_of_period"]:
                return line
    return False
 