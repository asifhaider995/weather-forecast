import os
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import json
from datetime import datetime, timedelta

from api.utils import download_district_locations

# Load district locations from JSON file
FILE_PATH = os.path.join("api", "data", "district_locations.json")
if not os.path.exists(FILE_PATH):
    download_district_locations()
with open(FILE_PATH, "r") as file:
    DATA = json.load(file)
    # DISTRICT_NAMES = [district["name"] for district in DATA.get("districts")]

# Load district locations from JSON file
class TravelRequestSerializer(serializers.Serializer):
    location = serializers.CharField()
    destination = serializers.CharField()
    date_of_travel = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])

    def validate_location(self, value):
        for data in DATA.get("districts"):
            if data.get("name") == value:
                return data
        raise ValidationError("District name does not exist.")
        
    def validate_destination(self, value):
        for data in DATA.get("districts"):
            if data.get("name") == value:
                return data
        raise ValidationError("District name does not exist.")

    def validate_date_of_travel(self, value):
        today = datetime.now().date()
        max_date = today + timedelta(days=7)
        if value < today:
            raise ValidationError("Date of travel must be today or in the future.")
        if value > max_date:
            raise ValidationError("Date of travel must be within the next 7 days.")
        return value