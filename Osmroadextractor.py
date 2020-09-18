# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 21:10:22 2020

@author: Emmanuel Jolaiya
"""

#Importing the libraries

import geopandas as gpd
from geopy import distance
import osmnx as ox
import os
import pandas as pd

#Creating the class

class RoadLenghtExtractor():
    
    """ This class reads a geojson file
        retieves intersecting roads from OSM and
        exports their lenghts to csv
        
        **How to use**
        1) Instantiate: var=RoadLenghtExtractor(path/to/geojson/file)
        2) Save: var.save() =>Exported csv would be save in the present working directory
    
    """
    
    def __init__(self,path):
        
        self.path=path
        
        
        #Handling likely user errors with assertion
        
        assert os.path.exists(self.path),"Input a valid file path"
        
        assert self.path.endswith(".txt") or self.path.endswith(".geojson"),"Input a valid geojson file path"
    
        assert isinstance(self.path,str),"File path must be of type(str)"
        
    def __read_file(self):
        
        """ Private method to read the geojson file
        
            args:
                
                >>path(str): Path to the geojson file
        
            returns:
                
                >>A geodataframe object of the read file
        
        """
        
        try:
            
            return gpd.read_file(self.path,encoding='utf-8')
        
        
        except FileNotFoundError as err:
            
            print("File could not be found,ensure you enter a valid geojson file")
            
            raise err
    
    def __get(self)->list:
        
        """
            A private method that retrieves the graphs from OSM using osmnx API
            
            args:

                >>Geojson Polygons
            
            returns:
                
                >>list of graphs with their informations
        
        """
        
        dataframe=self.__read_file()
       
        #Empty list to store all the graph informations of each layers
        
        graphs_info_list=[]
    
        
        for index,row in dataframe.iterrows():
            
            tonka_id,name,country,polygon=row
            
            #Try block to catch regions without roads and avoid errors
            
            try:
                
                print(f"Currently getting the roads for {name} polygon")
                
                graph=ox.graph_from_polygon(polygon)
                
                graphs_info_list.append([tonka_id,name,country,graph])
                
                print("Graph found!...")
                
            except Exception:
                
                print("Could not find graph for ", name)
                
                #append with empty list if no graph is found
                
                graphs_info_list.append([])
                
                
        
        return graphs_info_list
       
           
    def __clean_and_calculate_distance(self):
        
        """A private method to clean the graphs,convert to dataframe and calculate distance"""
        
        
        #Getting the returned list from the get method
        
        graphs_info_list=self.__get()
        
        print("Completed getting the road graphs")
        
        print("Processing the graphs...")
        
        #removing empty lists as a result of polygons with no intersecting roads
        
        graphs_info_list=[cleaned_list for cleaned_list in graphs_info_list if len(cleaned_list) > 1 ]
        
        
        #instantiating an empty dictionary to store the data
        
        result_dict={'NAME':[],"highway_type":[],'Distance(KM)':[],'Distance(Miles)':[]}
        
        #<<<<<<<<<<<<<<<<<<<<Data cleaning and manipulation block>>>>>>>>>>>>>>>>>
        
        for graphs in graphs_info_list:
            
            graph=graphs[-1]
            
            print("Converting graphs to GeoDataFrame...")
            
            graph_nodes,graph_dataframe=ox.graph_to_gdfs(graph)
            
            print("Completed converting graphs to GeoDataFrame ...")
            
            #>>>>Calculating distance block<<<<
            
            #Loop through the geometry column to create a list of coordinate tuples from the geometry
            
            print('Computing distances in kilometers and miles...')
            
            for layer,highwaytype in zip(graph_dataframe['geometry'],graph_dataframe["highway"]):
                
                geometry=list(layer.coords)
                
                #transforming the coordinate pairs to support geopy distance function
                
                start_long,start_lat=geometry[0]
                
                stop_long,stop_lat=geometry[1]
                
                start=(start_lat,start_long)
                
                stop=(stop_lat,stop_long)
                
                d=distance.distance
            
                distance_km=d(start,stop).km
            
                distance_miles=d(start,stop).miles
                
                result_dict['NAME'].append(graphs[1])
                
                result_dict["highway_type"].append(highwaytype)
                
                result_dict['Distance(KM)'].append(distance_km)
            
                result_dict['Distance(Miles)'].append(distance_miles)
                
               
                
            print('Completed computing distances...')
    
    
        
        print("Aggregating results in a dataframe...")
        
        result_dataframe=pd.DataFrame(dict([ (column,pd.Series(row)) for column,row in result_dict.items() ]))
        
        print("Completed aggregating results...")
        
        #>>>>>>>>>>>grouping DataFrame by highway_type<<<<<<<<<<<<<
        
        #First we fill missing value because not all roads are classified
        
        print("Filling missing values...")
        
        result_dataframe=result_dataframe.fillna("No highway category")
        
        print("Missing values filled...")
        
        #summing up each road distances
        
        print("Grouping DataFrame...")
        
        #converting keys to tuples to avoid unhashable errors because I figures some highways categories are lists types
        
        result_dataframe['highway_type']=result_dataframe['highway_type'].apply(lambda x: tuple(x) if type(x)==list else x)
        
        grouped_dataframe=result_dataframe.groupby(['NAME','highway_type'],as_index=False).sum()
        
        print("Completed grouping DataFrame...")
        
        return grouped_dataframe 
    
    def save(self):
        
        """Method to save the file to disk"""
        
        #Get the file name from the input path and replace extension with csv
        
        print("Operation begins!...")
        
        filename=os.path.basename(self.path).replace('txt','csv')
        
        path=os.path.join(os.path.dirname(self.path),filename)
        
        dataframe=self.__clean_and_calculate_distance()
    
        print(f"Success! Operation completed and file saved here>>>{path}!")
        
        try:
            
            return dataframe.to_csv(filename,index=False,encoding='utf-8')
        
        
        except Exception as err:
            
            print("Could not save file,ensure there is no error in the dataframe")
            
            raise err
        
         
         
       
       
           
 
       
#invoking the function

#Denver
#path1="C:\\Clientworks\\2020clientworks\\fiver\\OSMROADS\\Denver_HP_tasks.txt"
#data=RoadLenghtExtractor(path1).save()

#Detriot
path2="C:\\Clientworks\\2020clientworks\\fiver\\OSMROADS\\Detroit_HP_tasks.txt"
data=RoadLenghtExtractor(path2).save()
        
