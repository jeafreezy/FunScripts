"""
Author: Emmanuel Jolaiya
Date created: September 10,2020.
Requirements: area >>>  " pip install area " before usage!

"""

#importing the required libraries
from area import area
import json
import requests

class area_calculator():

    def __init__(self,osm_id:str,data_type:str):
        self.osm_id=osm_id
        self.data_type=data_type
        DATA_TYPES=['R','W']

        #Validation of user arguments during class invoking 

        assert isinstance(self.osm_id,str),'OSM ID must be of type [str]'

        assert self.data_type in DATA_TYPES,"DATA_TYPE must either be 'R' for Relation or 'W' for Ways"

    def __repr__(self):
        return ("This class calculates the area of a polygon retrieved from openstreetmap API")
    
    def _get_data(self)->list:

        """
            helper function to get geojson data from OSM API

            Args:
                id (str): The OSM ID for the feature to be retrieved
                type (str): The OSM DATA TYPE for the feature to be retrieved. R for Relation or W for Ways
                
            Returns:
                    coordinates[list]:List of coordinates of the polygon feature boundary
        """

        OSM_ID=self.osm_id

        DATA_TYPE=self.data_type

        data_request = requests.get("https://nominatim.openstreetmap.org/reverse?format=json&osm_id=" + OSM_ID + "&osm_type=" + DATA_TYPE + "&polygon_geojson=1")
        data_response = json.loads(data_request.text)
        data_coordinates=[element for element in data_response["geojson"]['coordinates']]

        return data_coordinates[0][:]

    def get_area(self)->int:

        """ This function calculates the area using the area library

            Returns:

                area[int]: The calculated area in square meters         
                    
        """
        coordinates=self._get_data()

        geoJSON_object = {
        
            'type': 'Polygon',

            'coordinates': [

                coordinates
            ]
        }  
        
        return area(geoJSON_object)



# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Invoking, tests and validation<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# Theresienwiese, Munich, Germany
# https://www.openstreetmap.org/way/23655360 

germany_area=area_calculator('23655360','W').get_area()

print(f'Germany area is 420,000 square meters from wikipedia and {int(germany_area)} square meters using this script ')

#Pakistan 
#https://www.openstreetmap.org/relation/307573

pakistan_area=area_calculator('2334933','R').get_area()

#divided by 1000000 to convert to square kilometers
print(f'Pakistan area is 881,913 square kilometres from wikipedia and {int(pakistan_area)} square kilometers using this script ')
