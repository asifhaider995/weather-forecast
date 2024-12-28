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


# def get_top_ten_districts(data):
#     top_ten_districts = []
#     for district_data in data:
#         lat=data.get("lat")
#         lng = data.get("long")
#         url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&forecast_days=7&timezone=Asia/Dacca&hourly=temperature_2m"


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
    top_ten_districts = sorted(filtered_results, key=lambda x: x["average_temp"], reverse=True)[:10]

    return top_ten_districts