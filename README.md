# Weather Forecast Application

This is a weather forcast application using APIs from (Open Meteo)[https://open-meteo.com/en/docs]

## Setup

### Virtual Environment

- Clone project
- Setup Virtual Environment

```
cd forecast/
python3 -m virtualenv venv
source venv/bin/activate
```
- Install dependencies
```
source venv/bin/activate
pip3 install -r requirements.txt
```
- Run Project 
```
python3 manage.py runserver
```

## Usage

- Pre-requisite: Start server 
```
python3 manage.py runserver
```
### Top 10 coolest districts

- Method: `GET`
- Endpoint: `api/v1/coolest-locations`
- Returns a list of names of districts that have the lowest average temperatures for the next 7 days at 2PM (T14:00)

- Curl Request (Assumes server is running at 127.0.0.1, Port 8000)
```
curl -H "Content-Type: application/json" -X GET http://127.0.0.1:8000/api/v1/coolest-locations
```

### Determine if Friend can travel

- Method: `POST`
- Endpoint: `api/v1/determine-travel`
- Request Body
```
{
  "location": "Dhaka",
  "destination": "Faridpur",
  "date_of_travel": "2025-01-02"
}
```
   - `location` is the current location of the friend, the location must exist in the given list of districts (case-sensitive)
   - `destination` is the current destination friend wants to travel, the location must exist in the given list of districts (case-sensitive)
   - `date_of_travel` is the date friend wants to travel, in the format `YYYY-MM-DD` (must be with in the next 7 days)

- Returns a single string `Can travel` if the destination temperature at 2 PM is lower than location temperature, else it returns `Cannot travel`

- Curl Request (Assumes server is running at 127.0.0.1 (localhost), Port 8000)
```
curl -X POST http://127.0.0.1:8000/api/v1/determine-travel \
-H "Content-Type: application/json" \
-d '{
  "location": "Dhaka",
  "destination": "Faridpur",
  "date_of_travel": "2025-01-02"
}'
```