import requests

def Weather(city): 
    api_address='http://api.openweathermap.org/data/2.5/weather?appid=0c42f7f6b53b244c78a418f4f181282a&q='

    url = api_address + city 
    json_data = requests.get(url).json() 
    format_add = json_data['main'] 
    return format_add

def Version(): 
    data = requests.get('http://localhost:5005/version')
    temp = data.json()
    print(temp['version'])
    return temp['version']