import asyncio
import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.serializers import TravelRequestSerializer
from api.utils import determine_travel, download_district_locations, get_top_ten_districts
# Create your views here.


class TopCoolestView(APIView):
    def get(self, request, **kwargs):
        file_path = os.path.join("api", "data", "district_locations.json")
        
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                # If not, download the file
                download_district_locations()
            
            # Read the JSON file
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
                filtered_data = asyncio.run(get_top_ten_districts(data))
            # Return the JSON data as the response payload
            return Response(filtered_data, status=status.HTTP_200_OK)
        
        except RuntimeError as e:
            # Handle errors during the download process
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Handle any other errors
            return Response({"error": f"Unexpected error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DetermineTravel(APIView):
    def post(self, request, **kwargs):
        serializer = TravelRequestSerializer(data=request.data)
        if serializer.is_valid():
            value = asyncio.run(determine_travel(validated_data=serializer.validated_data))
            return Response(value, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)