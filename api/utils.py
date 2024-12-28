import asyncio
import os
import requests
import json
import aiohttp


def download_district_locations():
    # Define the URL for the data
    url = "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json"  # Replace with the actual URL
    
    # Define the directory and file path
    directory = os.path.join("api", "data")
    file_path = os.path.join(directory, "district_locations.json")
    
    try:
        # Create the directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Fetch data from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the response as JSON
        data = response.json()
        
        # Save the data to a JSON file
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        
        print(f"Data successfully downloaded and saved to {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"Error saving data: {e}")


async def fetch_temperature_data(session, url, district_name):
    """
    Fetch temperature data for a district asynchronously.
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                # Find indices of times that end with "T14:00"
                times = data["hourly"]["time"]
                temperatures = data["hourly"]["temperature_2m"]
                
                # Get indices where time ends with "T14:00"
                indices = [i for i, time in enumerate(times) if time.endswith("T14:00")]
                
                # Extract the corresponding temperatures and calculate the average
                if indices:
                    temperatures_at_2pm = [temperatures[i] for i in indices]
                    average_temp = sum(temperatures_at_2pm) / len(temperatures_at_2pm)
                    return {"district": district_name, "average_temp": round(average_temp)}
                else:
                    print(f"No 2 PM temperature data found for {district_name}.")
                    return {"district": district_name, "average_temp": None}
            else:
                print(f"Error fetching data for {district_name}: HTTP {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching data for {district_name}: {e}")
        return None

async def get_top_ten_districts(data):
    """
    Get the top ten districts with the highest average temperatures.
    """
    base_url = "https://api.open-meteo.com/v1/forecast"
    tasks = []
    async with aiohttp.ClientSession() as session:
        data = data.get("districts", [])
        for district_data in data:
            lat = district_data.get("lat")
            lng = district_data.get("long")
            district_name = district_data.get("name")
            url = f"{base_url}?latitude={lat}&longitude={lng}&forecast_days=7&timezone=Asia/Dacca&hourly=temperature_2m"
            tasks.append(fetch_temperature_data(session, url, district_name))

        # Gather all responses
        results = await asyncio.gather(*tasks)

    # Filter out None responses and sort by average temperature
    filtered_results = [res for res in results if res is not None]
    top_ten_districts = sorted(filtered_results, key=lambda x: x["average_temp"])[:10]

    return top_ten_districts

async def fetch_temperature_data(url, params):
    """
    Fetch temperature data from the API.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise RuntimeError(f"Failed to fetch data: HTTP {response.status}")

async def determine_travel(validated_data):
    location = validated_data.get("location")
    destination = validated_data.get("destination")
    date_of_travel = validated_data.get("date_of_travel")
    
    location_lat, location_lng = location["lat"], location["long"]
    destination_lat, destination_lng = destination["lat"], destination["long"]
    
    # API URL and parameters
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "hourly": "temperature_2m",
        "timezone": "Asia/Dacca"
    }
    
    # Construct URLs
    location_url = f"{base_url}?latitude={location_lat}&longitude={location_lng}&forecast_days=7"
    destination_url = f"{base_url}?latitude={destination_lat}&longitude={destination_lng}&forecast_days=7"
    
    try:
        # Fetch data asynchronously for both location and destination
        location_task = fetch_temperature_data(location_url, params)
        destination_task = fetch_temperature_data(destination_url, params)
        location_data, destination_data = await asyncio.gather(location_task, destination_task)
        
        # Filter temperature for date_of_travel at 2PM
        location_temp = get_temp_at_2pm(location_data, date_of_travel)
        destination_temp = get_temp_at_2pm(destination_data, date_of_travel)
        
        if location_temp is None or destination_temp is None:
            return "Temperature data not available for the given date."
        
        # Compare temperatures
        return "Can Travel" if destination_temp < location_temp else "Cannot Travel"
    
    except Exception as e:
        raise RuntimeError(f"Error fetching temperature data: {e}")
    
def get_temp_at_2pm(data, date):
    times = data["hourly"]["time"]
    temperatures = data["hourly"]["temperature_2m"]
    temp_at_2pm = [
        temperatures[i]
        for i, time in enumerate(times)
        if time.startswith(date.strftime("%Y-%m-%d")) and time.endswith("T14:00")
    ]
    return temp_at_2pm[0] if temp_at_2pm else None