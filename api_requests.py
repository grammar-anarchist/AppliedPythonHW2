import aiohttp

from config import openweather_api_key, nutrition_api_key, nutrition_api_id

openweather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric"

async def curr_temperature(city_name, api_key=openweather_api_key): 
    try:       
        request_url = openweather_url.format(city_name, api_key)
        response = await aiohttp.get(request_url)
        response.raise_for_status()
        data = response.json()
        return data['main']['temp']
    
    except:
        return None

nutrionix_url = f"https://trackapi.nutritionix.com/v2/natural/nutrients"

async def product_calories(product, api_key=nutrition_api_key, api_id=nutrition_api_id):
    try:       
        request_url = nutrionix_url
        headers = {
            "x-app-id": api_id,
            "x-app-key": api_key,
            "Content-Type": "application/json"
        }
        data = {"query": product}
        response = await aiohttp.post(request_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        serving_size = result['foods'][0]['serving_weight_grams']
        calories = result['foods'][0]['nf_calories']
        return int(calories * 100 / serving_size)
    
    except:
        return None

async def calories_goal_func(weight, height, age):
    return (10 * weight) + (6.25 * height) - (5 * age)

async def water_goal_func(weight, city):
    temp = await curr_temperature(city)
    if temp is not None and temp > 25:
        water_increase = min(1000, 500 + (temp - 25) * (1000 - 500) / (35 - 25))
    else:
        water_increase = 0
    
    return 30 * weight + water_increase
