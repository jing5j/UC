#!/usr/bin/env python

"""
This python script extracts the data from the gdb file and performs statistical analysis on each layer. 
Finally, the coordinate data of the pipe and access chamber is converted to WGS84.
"""

from osgeo import ogr
import pandas as pd
import os
import datetime
import math
from dateutil import parser
import numpy as np
import re


multiline_geometry_regex = re.compile("([0-9.]+).*?([0-9.]+).*?([0-9.]+).*?([0-9.]+)") 


def print_progress(x, y, i, j):
    """Writes progress message every power of 2.
    Args:
        x (int): number of layers
        y (int): number of features
        i (int): layer counter
        j (int): feature counter
    """
    if (j & (j - 1)) == 0 or j == y:
        now = datetime.datetime.now().isoformat()
        print(f"Layer {i:2d} / {x:2d}, Feature {j:8d} / {y:8d}, Timestamp {now}")

def get_feature_dictionary(layer, feature):
    """Get feature dictionary
    Args:
        layer (osgeo.ogr.Layer): current layer
        feature (osgeo.ogr.Feature): current feature
    """
    # Base properties
    d = {
        'layer': layer.GetName(),
        'id': feature.GetFID()
    }
    d.update(feature.items())
    # Attempt to extract feature geometry
    try:
        geometry = feature.GetGeometryRef()
        d['geometry_type'] = geometry.GetGeometryType()
        d['geometry_name'] = geometry.GetGeometryName()       
    except:
        d['geometry_type'] = None
        d['geometry_name'] = None

    if geometry.GetGeometryName() == 'POINT':
        d['GeoXLO'] = geometry.GetX()
        d['GeoYLO'] = geometry.GetY()
        d['GeoXHI'] = geometry.GetX()
        d['GeoYHI'] = geometry.GetY()
        
    elif geometry.GetGeometryName() == 'MULTILINESTRING':
        
        try:
            XLO, YLO, XHI, YHI = multiline_geometry_regex.findall(str(geometry.Boundary()))[0]
            d['GeoXLO'] = XLO
            d['GeoYLO'] = YLO
            d['GeoXHI'] = XHI
            d['GeoYHI'] = YHI

        except:
            d['GeoXLO'] = None
            d['GeoYLO'] = None
            d['GeoXHI'] = None
            d['GeoYHI'] = None
            
    return d


if __name__ == '__main__':
    
    in_path = "/Users/wujing/Desktop/Inputs"
    out_path = "/Users/wujing/Desktop/Outputs"
    
    #assets needs to get geometry data
    assets = set(['vwOpenDataSwPipe','vwOpenDataSwAccess','vwOpenDataWwPipe','vwOpenDataWwAccess'])
    
      
    networks = [
        
        {
            'council': 'Christchurch City Council',
            'network': 'Stormwater',
            'path': os.path.join(in_path, 'Christchurch City Council', 'Stormwater.gdb'),
            'type': 'gdb'
        },
        {
            'council': 'Christchurch City Council',
            'network': 'Wastewater',
            'path': os.path.join(in_path, 'Christchurch City Council', 'Wastewater.gdb'),
            'type': 'gdb'
        },
        {
            'council': 'Christchurch City Council',
            'network': 'Watersupply',
            'path': os.path.join(in_path, 'Christchurch City Council', 'Watersupply.gdb'),
            'type': 'gdb'
        }
    ]
     
    
    for network in networks:

        
        if network['type'] == 'gdb':
            driver = ogr.GetDriverByName('OpenFileGDB')
            data = driver.Open(network['path'], 0)
        else:
            data = ogr.Open(network['path'])
            
        data_size = data.GetLayerCount()

       
        
        #Create file path 
        council_path = os.path.join(out_path, network['council'], network['network'])
        layer_path = os.path.join(council_path,'layers')
        os.makedirs(layer_path, exist_ok=True)
        statistics_path = os.path.join(council_path, 'Statistics')
        os.makedirs(statistics_path,exist_ok=True)
        FH_path = os.path.join(council_path,'Bruce')
        os.makedirs(FH_path, exist_ok=True)
        
        
        #layer
        i = 0
        for layer in data:
            i = i + 1
            
            #get layer name and size
            layer_name = layer.GetName()
            layer_size = layer.GetFeatureCount()
            
            
            if layer_size == 0:

                j = 0
                print_progress(data_size, layer_size, i, j)

            else:

                features = []
                
                j = 1
                print_progress(data_size, layer_size, i, j)
        
        
                feature = next(layer)
                attributes = feature.items()
                keys = [k for k in attributes.keys()]
                
                names = [
                    'layer',
                    'id',
                    'geometry_type',
                    'geometry_name',
                    'GeoXLO',
                    'GeoYLO',
                    'GeoXHI',
                    'GeoYHI'
                ] + [
                    k for k in keys
                ]
                features.append(get_feature_dictionary(layer, feature))
                
                
                for feature in layer:
                    j = j + 1
                    print_progress(data_size, layer_size, i, j)
                    features.append(get_feature_dictionary(layer, feature))
                    
                #save features data from gdb file
                df = pd.DataFrame.from_records(features, columns = names)
                df.to_csv(os.path.join(layer_path,f'{layer_name}(layer).csv'), index=False, header=True)
                
            
                #statistics
                columns = [
                    'Count',
                    'Not Empty',
                    'Empty',
                    'Unique',
                    'Data Type',
                    'Negative',
                    'Zeros',
                    'Positive',
                    'Min',
                    'Max',
                    'Min Length',
                    'Max Length',
                    'Commas',
                    'Date String',
                ]
                statistics = pd.DataFrame(index=names, columns=columns)
                statistics.index.name = 'Attribute'

                statistics['Count'] = df.shape[0]

                def check_empty(x):
                    return x.isnull() | x.isin(["", " ", "NA", "None"])

                def check_zero(x):
                    return x == 0

                statistics['Empty'] = df.apply(check_empty).sum()
                statistics['Not Empty'] = statistics['Count'] - statistics['Empty']

                def count_unique(x):
                    return x.value_counts().shape[0]

                statistics['Unique'] = df.apply(count_unique)

                def isdate(s):
                    """Check if string can be parsed as a valid datetime object by dateutils.
                    Args:
                        s (str): string to be checked
                    Returns:
                        bool: if string can be parsed 
                    """
                    try: 
                        parser.parse(s)
                        return True
                    except ValueError:
                        return False

                def check_type(x):
                    i = x.first_valid_index()
                    if i is None:
                        return 'NaN'
                    v = x[i]
                    if np.issubdtype(type(v), int):
                        return 'Integer'
                    if np.issubdtype(type(v), float):
                        return 'Decimal'
                    if isinstance(v, str) and isdate(v):
                        return 'Date'
                    if isinstance(v, str):
                        return 'Alpha / Numeric'
                    return ''

                statistics['Data Type'] = df.apply(check_type)

                x = statistics['Data Type'].isin(['Integer', 'Decimal'])
                columns = x[x].index
                statistics['Min'] = df[columns].min()
                statistics['Max'] = df[columns].max()
                statistics['Negative'] = df[columns].apply(lambda x: x < 0).sum()
                statistics['Zeros'] = df[columns].apply(lambda x: x == 0).sum()
                statistics['Positive'] = df[columns].apply(lambda x: x > 0).sum()

                x = statistics['Data Type'] == 'Alpha / Numeric'
                columns = x[x].index
                for column in columns:
                    lengths = df[column].str.len()
                    statistics.loc[column, 'Min Length'] = lengths.min()
                    statistics.loc[column, 'Max Length'] = lengths.max()
                    statistics.loc[column, 'Commas'] = df[column].str.contains(',').sum()

                x = statistics['Data Type'] == 'Date'
                columns = x[x].index
                for column in columns:
                    statistics.loc[column, 'Date String'] = df.loc[df[column].first_valid_index(), column]

                # Save statistics

                statistics = statistics.reset_index()
                statistics.to_csv(os.path.join(statistics_path, f"{layer_name}(statistics).csv"), index=False, header=True)
                
    
                #create CSV file with geometry column
                if layer_name in assets:
                    
                    print(f"{layer_name} is converting.")
                    
                    def calculate_lat_lone(nztm_e, nztm_n):
                        """Convert NZTM to WGS84
                        Args:
                            nztm_e(str):longitude of NZTM
                            nztm_n(str):latitude of NZTM
                        """
                        #Common variables for NZTM2000
                        a = 6378137
                        f = 1 / 298.257222101
                        lambdazero = 173
                        Nzero = 10000000
                        Ezero = 1600000
                        kzero = 0.9996   
                          
                        #input Northing(Y); Easting(X) variables
                        try:
                            N  = float(nztm_n)
                            E  = float(nztm_e)
                       
                          
                            #Calculation: From NZTM to lat/Long
                            b = a * (1 - f)
                            esq = 2 * f - f ** 2
                                
                            Nprime = N - Nzero
                            mprime = Nprime / kzero
                            smn = (a - b) / (a + b)
                            G = a * (1 - smn) * (1 - (smn ** 2)) * (1 + 9 * (smn ** 2) / 4 + 225 * (smn ** 4) / 64) * math.pi/ 180.0
                            sigma = mprime * math.pi / (180 * G)
                            phiprime = sigma + (3 * smn / 2 - 27 * (smn ** 3) / 32) * math.sin(2 * sigma) + (21 * (smn ** 2) / 16 - 55 * (smn ** 4) / 32) * math.sin(4 * sigma) + (151 * (smn ** 3) / 96) * math.sin(6 * sigma) + (1097 * (smn ** 4) / 512) *math.sin(8 * sigma)
                            rhoprime = a * (1 - esq) / ((1 - esq * ((math.sin(phiprime)) ** 2)) ** 1.5)
                            upsilonprime = a / math.sqrt(1 - esq * ((math.sin(phiprime)) ** 2))
                              
                            psiprime = upsilonprime / rhoprime
                            tprime = math.tan(phiprime)
                            Eprime = E - Ezero;
                            chi = Eprime / (kzero * upsilonprime)
                            term_1 = tprime * Eprime * chi / (kzero * rhoprime * 2)
                            term_2 = term_1 * (chi ** 2) / 12 * (-4 * (psiprime ** 2) + 9 * psiprime * (1 - (tprime ** 2)) + 12 * (tprime ** 2))
                            term_3 = tprime * Eprime * (chi ** 5) / (kzero * rhoprime * 720) * (8 * (psiprime ** 4) * (11 - 24 * (tprime ** 2)) - 12 * (psiprime ** 3) * (21 - 71 * (tprime ** 2)) + 15 * (psiprime ** 2) * (15 - 98 * (tprime ** 2) + 15 * (tprime ** 4)) + 180 * psiprime * (5 * (tprime ** 2) - 3 * (tprime ** 4)) + 360 * (tprime ** 4))
                            term_4 = tprime * Eprime * (chi ** 7) / (kzero * rhoprime * 40320) * (1385 + 3633 * (tprime ** 2) + 4095 * (tprime ** 4) + 1575 * (tprime ** 6))
                            term1 = chi * (1 / math.cos(phiprime))
                            term2 = (chi ** 3) * (1 / math.cos(phiprime)) / 6 * (psiprime + 2 * (tprime ** 2))
                            term3 = (chi ** 5) * (1 / math.cos(phiprime)) / 120 * (-4 * (psiprime ** 3) * (1 - 6 * (tprime ** 2)) + (psiprime ** 2) * (9 - 68 * (tprime ** 2)) + 72 * psiprime * (tprime ** 2) + 24 * (tprime ** 4))
                            term4 = (chi ** 7) * (1 / math.cos(phiprime)) / 5040 * (61 + 662 * (tprime ** 2) + 1320 * (tprime ** 4) + 720 * (tprime ** 6))
                              
                            latitude = (phiprime - term_1 + term_2 - term_3 + term_4) * 180 / math.pi
                            longitude = lambdazero + 180 / math.pi * (term1 - term2 + term3 - term4)
                        
                        except:
                            
                            latitude = None
                            longitude = None
                        
                        return latitude, longitude
                    
                    
                    def nztm_to_lat_long(dataframe, geo_x, geo_y):
                        '''Create converted longitude and latitude lists
                        Args:
                            dataframe(pd.DataFrame):DataFrame of layer
                            geo_x: column name of longitude
                            geo_y: column name of latitude
                        '''
                        
                        infile = dataframe.loc[:,[geo_x, geo_y]]
                        long_list = []
                        lat_list = [] 
                    
                        for index in set(infile.index):
                            line = str(infile.loc[index].values[:]).replace("[","").replace("]","") 
                            try:
                                nztm_e, nztm_n = line.replace("'","").split()
                            except:
                                nztm_e, nztm_n = line.split()
                            latitude, longitude = calculate_lat_lone(nztm_e, nztm_n)
                            
                            lat_list.append(latitude)
                            long_list.append(longitude)
                            
                            
                        return lat_list, long_list       
                    
                         
                    def create_geometry(long_min, lat_min, long_max, lat_max, df):
                        '''
                        Add column geometry in the format [Lat,Long,Altitude_ Lat,Long,Altitude]
                        Example “172.74424244,-43.54612293,0 172.74397566,-43.54619336,0”
                        Args:
                            long_min(list): low longitude
                            lat_min(list): low latitude
                            long_max(list): high longitude
                            lat_max(list): high latitude
                            df(pd.DataFrame): dataframe to add geometry column
                        '''
                        
                        geo_dict = {"long_min": long_min,
                                    "lat_min": lat_min,
                                    "long_max": long_max,
                                    "lat_max": lat_max}
                        geo_dataframe = pd.DataFrame(geo_dict)
                        
                        geo_dataframe["long_min"] = geo_dataframe["long_min"].map(lambda x:str(x))
                        geo_dataframe["lat_min"] = geo_dataframe["lat_min"].map(lambda x:str(x))
                        geo_dataframe["long_max"] = geo_dataframe["long_max"].map(lambda x:str(x))
                        geo_dataframe["lat_max"] = geo_dataframe["lat_max"].map(lambda x:str(x))
                        
                        geo_dataframe['geometry'] = geo_dataframe['long_min'] + "," +geo_dataframe['lat_min'] + ",0 " + geo_dataframe['long_max']+ "," +geo_dataframe['lat_max']+ ",0"
                        
                        df['geometry'] = geo_dataframe['geometry']
                        
                        return df
                    
                    
                    #convert NZTM to WGS84 and add geomatry column
                    lat_min, long_min = nztm_to_lat_long(df,'GeoXLO','GeoYLO')
                    lat_max, long_max = nztm_to_lat_long(df,'GeoXHI','GeoYHI')
                    FHfile = create_geometry(long_min, lat_min, long_max, lat_max, df)
                    
                    #save FH file with geomatry column
                    FHfile.to_csv(os.path.join(FH_path,f'{layer_name}(Bruce).csv'),index=False, header=True)
                        
                          
        
