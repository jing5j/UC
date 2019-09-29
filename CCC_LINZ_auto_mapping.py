#！/usr/bin/env/python
# -*- coding:utf-8 -*-

"""
Run CCC_gdb_to_geometry.py firstly
This python script is for mapping CCC metadata standard to LINZ metadata standard
1. asset mapping (manually)
2. attributes mapping (manually)
3. codelists mapping (automatically)
4. codelist values mapping (automatically)
"""

import pandas as pd
import os
import numpy as np
import difflib


def max_similarity(x,Y):
    """Get the highest similarity item
    Args:
    x (str) : item 
    Y (list) : list
    """
    max_sim = 0
    max_match = ''
    for y in Y:
        similarity = difflib.SequenceMatcher(None, x, y).ratio()
        if similarity >= max_sim:
            max_sim = similarity
            max_match = y
    return similarity, max_match


def auto_mapping(CCC_List,LINZ_List):
    """Map the two lists automatically and create a dataframe
    Args:
    CCC_List (list): list of CCC (attributes, codelist values)
    LINZ_List (list): list of LINZ (attributes, codelist values)
    """
    mapping_dict = {}
    similarity_mapping_dict = {}
    for item in CCC_List:
        similarity, max_match = max_similarity(item.upper(), LINZ_List)
        if similarity > 0.1:
            mapping_dict[item] = max_match
            similarity_mapping_dict[item] = similarity
    data = pd.DataFrame({'CCC':CCC_List},index = range(len(CCC_List)))
    data['LINZ'] = data['CCC'].map(mapping_dict)
    data['Similarity'] = data['CCC'].map(similarity_mapping_dict)
    values = mapping_dict.values()
    notinCCC = set(LINZ_List)^set(values)
    for item in notinCCC:
        data = data.append([{'LINZ':item}],ignore_index=True)
    return data  

   
def content(CCC,LINZ):
    """add content"""
    if CCC is np.nan and LINZ is not np.nan:
        return "Not in CCC"
    elif CCC is not np.nan and LINZ is np.nan:
        return "Not in LINZ"
    elif CCC == LINZ:
        return "Match"
    else:
        return "Rename"

def mapping_analyze(CCC_List,LINZ_List,mapping_dict):
    """create dataframe for mapping result
    Args:
    CCC_List (list): CCC item list
    LINZ_List (list): LINZ item list
    mapping_dict (dict): item mapping dictionary
    """
    data = pd.DataFrame({'CCC':CCC_List},index = range(len(CCC_List)))
    data['LINZ'] = data['CCC'].map(mapping_dict)
    values = list(mapping_dict.values())
    notinCCC = list(set(LINZ_List)^set(values))
    for item in notinCCC:
        data = data.append([{'LINZ':item}],ignore_index=True)
    data['Content'] = data.apply(lambda x: content(x.CCC, x.LINZ), axis = 1)
    return data      
                

if __name__ == '__main__':
    
    
    in_path = '/Users/wujing/Desktop/Inputs'
    out_path = "/Users/wujing/Desktop/Outputs" 
    
    networks = [
        {
            'council': 'Christchurch City Council',
            'network': 'Stormwater',
            'Asset_Class_mapping': {'SwPipe':'Pipe',
                                    'SwAccess':'Chamber',
                                    'SwFitting':'Fittings',
                                    'SwValve':'Valve',
                                    'SwPump':'Pump'},
            'attributes_mapping':{'SwPipe':{'SwPipeID':'Unique_ID',
                                            'SwPipeType':'Purpose',
                                            'SwPipeServiceStatus':'Status',
                                            'SwPipeOwnership':'Owner',
                                            'CommissionDate':'Const_Date',
                                            'SwPipeManufacturer':'Manu',
                                            'SwPipeNominalDiameter':'Nom_Dia',
                                            'InsideDiameter':'Int_Dia',
                                            'SwPipeConstruction':'Material',
                                            'SwPipePressureClass':'Class_Pn',
                                            'SwPipeStiffnessClass':'Class_Sn',
                                            'SwPipeLoadClass':'Class_Load',
                                            'SwPipeShape':'PShape',
                                            'NominalHeight':'P_Height',
                                            'NominalWidth':'P_Width',
                                            'SwPipeInstallationMethod':'Instl_Mthd',
                                            'UpstreamInvert':'From_IL',
                                            'DownstreamInvert':'To_IL',
                                            'UpstreamFeatureID':'From_Node',
                                            'DownstreamFeatureID':'To_Node',
                                            'SwPipeTreatment':'Rl_Rn_Mtd',
                                            'SwPipeTreatmentConstruction':'Rl_Rn_Mat',
                                            'drvLength':'Length_m',
                                            'Comment':'Comments'},
                                  'SwAccess':{'SwAccessID':'Unique_ID',
                                              'SwAccessType':'Type_Chamb', 
                                              'SwAccessServiceStatus':'Status', 
                                              'SwAccessOwnership':'Owner',
                                              'CommissionDate':'Const_Date', 
                                              'LidLevel':'Lid_RL', 
                                              'BaseLevel':'RL',
                                              'PitWidth':'AC_Width', 
                                              'PitLength':'AC_Length',
                                              'SwAccessConstruction':'Material',
                                              'SwAccessLidStyle':'Lid_Type', 
                                              'SwAccessSecurity':'Seal_Type',
                                              'Comment':'Comments'},
                                  'SwFitting':{'SwFittingID':'Unique_ID', 
                                               'SwFittingType':'Type_Fit', 
                                               'SwFittingServiceStatus':'Status', 
                                               'SwFittingOwnership':'Owner',
                                               'CommissionDate':'Const_Date', 
                                               'DecommissionDate':'Manu_W',
                                               'Comment':'Comments'},
                                  'SwValve':{'SwValveID':'Unique_ID', 
                                             'SwValveType':'Type_Valve', 
                                             'SwValveServiceStatus':'Status', 
                                             'SwValveOwnership':'Owner',
                                             'SwValveLocationCertainty':'Open_Shut',
                                             'CommissionDate':'Const_Date', 
                                             'SwValveInstallationCompany':'Installer', 
                                             'SwValveManufacturer':'Manu', 
                                             'ManufacturerWarrantyEndDate':'Manu_W', 
                                             'LidLevel':'Valve_RL', 
                                             'SwValveNominalDiameter':'Size', 
                                             'SwValveConstruction':'Material', 
                                             'SwValveFunction':'Purpose', 
                                             'SwValveClosureRotation':'Close_Dir',
                                             'SwValveControlPoint':'Bel_Grnd',
                                             'SwValveActuation':'Op_Mode',
                                             'Comment':'Comments'},
                                  'SwPump':{'SwPumpID':'Unique_ID', 
                                            'SwPumpType':'Pump_Type',  
                                            'SwPumpServiceStatus':'Status',  
                                            'SwPumpOwnership':'Owner', 
                                            'CommissionDate':'Const_Date',  
                                            'SwPumpManufacturer':'P_Manu', 
                                            'ManufacturerWarrantyEndDate':'Manu_W',  
                                            'PumpSerialNumber':'P_Serial',  
                                            'PumpCapacity':'P_Rate', 
                                            'Comment':'Comments'}}
        },
        {
            'council': 'Christchurch City Council',
            'network': 'Wastewater',
            'Asset_Class_mapping': {'WwPipe':'Pipe',
                                    'WwAccess':'Chamber',
                                    'WwFitting':'Fittings',
                                    'WwValve':'Valve',
                                    'WwPump':'Pump'},
            'attributes_mapping':{'WwPipe':{'WwPipeID':'Unique_ID',
                                            'WwPipeType':'Purpose',
                                            'WwPipeServiceStatus':'Status',
                                            'WwPipeOwnership':'Owner',
                                            'CommissionDate':'Const_Date',
                                            'WwPipeManufacturer':'Manu',
                                            'WwPipeNominalDiameter':'Nom_Dia',
                                            'InsideDiameter':'Int_Dia',
                                            'WwPipeConstruction':'Material',
                                            'WwPipePressureClass':'Class_Pn',
                                            'WwPipeStiffnessClass':'Class_Sn',
                                            'WwPipeLoadClass':'Class_Load',
                                            'WwPipeShape':'PShape',
                                            'NominalHeight':'P_Height',
                                            'NominalWidth':'P_Width',
                                            'WwPipeInstallationMethod':'Instl_Mthd',
                                            'UpstreamInvert':'From_IL',
                                            'DownstreamInvert':'To_IL',
                                            'UpstreamFeatureID':'From_Node',
                                            'DownstreamFeatureID':'To_Node',
                                            'WwPipeTreatment':'Rl_Rn_Mtd',
                                            'WwPipeTreatmentConstruction':'Rl_Rn_Mat',
                                            'drvLength':'Length_m',
                                            'Comment':'Comments'},
                                  'WwAccess':{'WwAccessID':'Unique_ID',
                                              'WwAccessType':'Type_Chamb', 
                                              'WwAccessServiceStatus':'Status', 
                                              'WwAccessOwnership':'Owner',
                                              'CommissionDate':'Const_Date', 
                                              'LidLevel':'Lid_RL', 
                                              'BaseLevel':'RL',
                                              'PitWidth':'AC_Width', 
                                              'PitLength':'AC_Length',
                                              'WwAccessConstruction':'Material',
                                              'WwAccessLidStyle':'Lid_Type', 
                                              'WwAccessSecurity':'Seal_Type',
                                              'Comment':'Comments'},
                                  'WwFitting':{'WwFittingID':'Unique_ID', 
                                               'WwFittingType':'Type_Fit', 
                                               'WwFittingServiceStatus':'Status', 
                                               'WwFittingOwnership':'Owner',
                                               'CommissionDate':'Const_Date', 
                                               'DecommissionDate':'Manu_W',
                                               'Comment':'Comments'},
                                  'WwValve':{'WwValveID':'Unique_ID', 
                                             'WwValveType':'Type_Valve', 
                                             'WwValveServiceStatus':'Status', 
                                             'WwValveOwnership':'Owner',
                                             'CommissionDate':'Const_Date', 
                                             'WwValveInstallationCompany':'Installer', 
                                             'WwValveManufacturer':'Manu', 
                                             'ManufacturerWarrantyEndDate':'Manu_W', 
                                             'LidLevel':'Valve_RL', 
                                             'WwValveNominalDiameter':'Size', 
                                             'WwValveConstruction':'Material', 
                                             'WwValveFunction':'Purpose', 
                                             'WwValveClosureRotation':'Close_Dir',
                                             'WwValveControlPoint':'Bel_Grnd',
                                             'WwValveActuation':'Op_Mode',
                                             'Comment':'Comments'},
                                  'WwPump':{'WwPumpID':'Unique_ID', 
                                            'WwPumpType':'Pump_Type',  
                                            'WwPumpServiceStatus':'Status',  
                                            'WwPumpOwnership':'Owner', 
                                            'CommissionDate':'Const_Date',  
                                            'WwPumpManufacturer':'P_Manu', 
                                            'ManufacturerWarrantyEndDate':'Manu_W',  
                                            'PumpSerialNumber':'P_Serial',  
                                            'PumpCapacity':'P_Rate', 
                                            'Comment':'Comments'}}                                       
        },
        {
            'council': 'Christchurch City Council',
            'network': 'Watersupply',
            'Asset_Class_mapping': {'WsPipe':'Pipe',
                            'WsFitting':'Fittings',
                            'WsValve':'Valve',
                            'WsPump':'Pump'},    
            'attributes_mapping':{'WsPipe':{'WsPipeID':'Unique_ID',
                                            'WsPipeType':'Purpose',
                                            'WsPipeServiceStatus':'Status',
                                            'WsPipeOwnership':'Owner',
                                            'CommissionDate':'Const_Date',
                                            'WsPipeManufacturer':'Manu',
                                            'WsPipeNominalDiameter':'Nom_Dia',
                                            'InsideDiameter':'Int_Dia',
                                            'WsPipeConstruction':'Material',
                                            'WsPipePressureClass':'Class_Pn',
                                            'WsPipeStiffnessClass':'Class_Sn',
                                            'WsPipeLoadClass':'Class_Load',
                                            'WsPipeInstallationMethod':'Instl_Mthd',
                                            'WsPipeTreatment':'Rl_Rn_Mtd',
                                            'WsPipeTreatmentConstruction':'Rl_Rn_Mat',
                                            'drvLength':'Length_m',
                                            'Comment':'Comments'},
                                  'WsFitting':{'WsFittingID':'Unique_ID', 
                                               'WsFittingType':'Type_Fit', 
                                               'WsFittingServiceStatus':'Status', 
                                               'WsFittingOwnership':'Owner',
                                               'CommissionDate':'Const_Date', 
                                               'DecommissionDate':'Manu_W',
                                               'Comment':'Comments'},
                                  'WsValve':{'WsValveID':'Unique_ID', 
                                             'WsValveType':'Type_Valve', 
                                             'WsValveServiceStatus':'Status', 
                                             'WsValveOwnership':'Owner',
                                             'CommissionDate':'Const_Date', 
                                             'WsValveInstallationCompany':'Installer', 
                                             'WsValveManufacturer':'Manu', 
                                             'ManufacturerWarrantyEndDate':'Manu_W', 
                                             'LidLevel':'Valve_RL', 
                                             'WsValveNominalDiameter':'Size', 
                                             'WsValveConstruction':'Material', 
                                             'WsValveFunction':'Purpose', 
                                             'WsValveClosureRotation':'Close_Dir',
                                             'WsValveControlPoint':'Bel_Grnd',
                                             'WsValveActuation':'Op_Mode',
                                             'Comment':'Comments'},
                                  'WsPump':{'WsPumpID':'Unique_ID', 
                                            'WsPumpType':'Pump_Type',  
                                            'WsPumpServiceStatus':'Status',  
                                            'WsPumpOwnership':'Owner', 
                                            'CommissionDate':'Const_Date',  
                                            'WsPumpManufacturer':'P_Manu', 
                                            'ManufacturerWarrantyEndDate':'Manu_W',  
                                            'PumpSerialNumber':'P_Serial',  
                                            'PumpCapacity':'P_Rate', 
                                            'Comment':'Comments'}}
        }        
                ]
    
    #load CCC metadata standard and LINZ metadata standard
    CCC_attributes_data = pd.read_excel(os.path.join(in_path,'GISAssetModels.xlsx'),sheet_name='Asset Attributes')
    CCC_codelist_data = pd.read_excel(os.path.join(in_path,'GISAssetModels.xlsx'),sheet_name='Asset Domain Tables (full)')
    LINZ_attributes_data = pd.read_excel(os.path.join(in_path,'LINZStandards_3Waters.xlsx'),sheet_name='Data')
    LINZ_codelist_data = pd.read_excel(os.path.join(in_path,'LINZStandards_3Waters.xlsx'),sheet_name='Codes')
    
    
    
    for network in networks:
        
        #create path
        linz_path = os.path.join(out_path, network['council'], 'LINZ', 'LINZ mapping')
        os.makedirs(linz_path, exist_ok=True)
    
        #get the layer file name
        csv_path = os.path.join(out_path,network['council'],network['network'],'layers')
        CCC_asset_file_list = os.listdir(csv_path)



        for item, linz_asset in network['Asset_Class_mapping'].items():
        
            #analysis for Asset Class
            asset = [item]
            LINZ_asset = [network['Asset_Class_mapping'][item]]
            asset_mapping_dict = dict([(key, network['Asset_Class_mapping'][key]) for key in asset])
            data_asset = pd.DataFrame({'CCC':asset},index = range(len(asset)))
            data_asset['LINZ'] = data_asset['CCC'].map(asset_mapping_dict)
            values = list(asset_mapping_dict.values())
            notinCCC = list(set(LINZ_asset)^set(values))
            for item in notinCCC:
                data_asset = data_asset.append([{'LINZ':item}],ignore_index=True)
            data_asset['Content'] = data_asset.apply(lambda x: content(x.CCC, x.LINZ), axis = 1)
            
            
            
            #get CCC Attributes and Data type dictionary
            CCC_attri_type = CCC_attributes_data[['GISModelName','GISAttributeName','GISAttributeDataType']].dropna(axis=0, how='any')
            CCC_attributes_TYPE = list(CCC_attri_type.loc[CCC_attri_type['GISModelName'] == item]['GISAttributeName'])
            CCCtypedict = {}
            for attri in CCC_attributes_TYPE:
                attri_type = CCC_attri_type.loc[(CCC_attri_type['GISModelName'] == item)& (CCC_attri_type['GISAttributeName'] == attri),'GISAttributeDataType'].values[0]
                CCCtypedict[attri]=attri_type 
            
            
            #get LINZ Attributes and Data type dictionary
            LINZ_attri_type = LINZ_attributes_data[['Asset Class','Attribute Name - Abbreviated','Data Type']].dropna(axis=0, how='any')
            LINZ_attributes_TYPE = list(LINZ_attri_type.loc[LINZ_attri_type['Asset Class'] == linz_asset]['Attribute Name - Abbreviated'])
            LINZtypedict = {}
            for attri in LINZ_attributes_TYPE:
                attri_type = LINZ_attri_type.loc[(LINZ_attri_type['Asset Class'] == linz_asset)& (LINZ_attri_type['Attribute Name - Abbreviated'] == attri),'Data Type'].values[0]
                LINZtypedict[attri]=attri_type 
            
                  
            #analysis for attributes
            attributes = list(CCC_attributes_data.loc[CCC_attributes_data['GISModelName'] == item]['GISAttributeName'])
            LINZ_attributes = list(LINZ_attributes_data.loc[LINZ_attributes_data['Asset Class'] == linz_asset]['Attribute Name - Abbreviated'])
            attributes_mapping_dict = network['attributes_mapping'][item]
            data_attributes = mapping_analyze(attributes,LINZ_attributes,attributes_mapping_dict)
            data_attributes['CCC Attribute Data Type'] = data_attributes['CCC'].map(CCCtypedict)
            data_attributes['LINZ Attribute Data Type'] = data_attributes['LINZ'].map(LINZtypedict)
            
            
            data_attributes = data_attributes.fillna({'CCC':'Attribute Not in CCC.','LINZ':'Attribute Not in LINZ.'})
            data_attributes.rename(columns={'CCC':'CCC Attribute', 'LINZ':'LINZ Attribute',}, inplace = True)
            data_attributes['CCC Asset Class'] = item
            data_attributes['LINZ Asset Class'] = linz_asset
            data_attributes.rename(columns={'CCC':'CCC Attribute', 'LINZ':'LINZ Attribute'}, inplace = True)
            columns = ['CCC Asset Class','CCC Attribute','Content','LINZ Asset Class','LINZ Attribute','CCC Attribute Data Type','LINZ Attribute Data Type']
            data_attributes = data_attributes[columns]
            
            
            #analysis for codelist
            data_codelist = data_attributes[['CCC Asset Class','CCC Attribute','LINZ Asset Class','LINZ Attribute']]
            
            LINZ_attri_codelist = {}
            for attri in LINZ_attributes:
                LINZ_codelist = LINZ_attributes_data.loc[(LINZ_attributes_data['Asset Class'] == linz_asset) & (LINZ_attributes_data['Attribute Name - Abbreviated'] == attri)]['CODELIST Reference'].values[0]
                if LINZ_codelist is not np.nan:
                    LINZ_attri_codelist[attri]=LINZ_codelist
            
            CCC_attri_codelist = {}
            attributes_codelist = set(CCC_codelist_data.loc[CCC_codelist_data['GISModelName'] == item]['GISAttributeName'])
            for attri in attributes_codelist:
                CCC_codelist = CCC_codelist_data.loc[(CCC_codelist_data['GISModelName'] == item) & (CCC_codelist_data['GISAttributeName'] == attri)]['GISDomainTableName'].values[0]
                CCC_attri_codelist[attri]=CCC_codelist
            
            data_codelist['LINZ Codelist'] = data_codelist['LINZ Attribute'].map(LINZ_attri_codelist)
            data_codelist['CCC Codelist'] = data_codelist['CCC Attribute'].map(CCC_attri_codelist)
            data_codelist = data_codelist.dropna(subset=['CCC Codelist', 'LINZ Codelist'],how='all') 
            data_codelist['Content'] = data_codelist.apply(lambda x: content(x['CCC Codelist'], x['LINZ Codelist']), axis = 1)
            data_codelist = data_codelist.fillna({'CCC Codelist':'Code List Not in CCC.','LINZ Codelist':'Code List Not in LINZ.','LINZ Attribute':'Attribute not in LINZ'})
            columns = ['CCC Asset Class','CCC Attribute','CCC Codelist','Content','LINZ Asset Class','LINZ Attribute','LINZ Codelist']
            data_codelist = data_codelist[columns]
            
            
            
            data = data_codelist[['CCC Codelist','LINZ Codelist']]
            codelist_mapping_dict = data.set_index('CCC Codelist').to_dict(orient= 'dict')
            codelist_mapping_dict = list(codelist_mapping_dict.values())[0]
            codelist_mapping = {}
            for key,value in codelist_mapping_dict.items():
                if key != 'Code List Not in CCC.' and value != 'Code List Not in LINZ.':
                    codelist_mapping[key] = value
       

         
            #analysis for codelist value        
            data_codelist_value = pd.DataFrame(columns = [])
            for key,value in codelist_mapping.items():
                codelist_value = list(CCC_codelist_data.loc[CCC_codelist_data['GISDomainTableName'] == key]['GISDomainValue'])
                LINZ_codelist_value = list(LINZ_codelist_data.loc[LINZ_codelist_data['Codelist'] == value]['Code'])
                data = auto_mapping(codelist_value,LINZ_codelist_value)
                data['CCC codelist'] = key
                data['LINZ codelist'] = value
                data_codelist_value = data_codelist_value.append(data,ignore_index=True,sort=True)
           
            #add LINZ codelist values which are not matched to CCC into dataframe 
            LINZ_codelist = LINZ_attributes_data.loc[LINZ_attributes_data['Asset Class'] == linz_asset]['CODELIST Reference'].dropna(axis=0, how='any')
            LINZ_codelist_matched = codelist_mapping.values()
            notmatchCCC = set(LINZ_codelist)^set(LINZ_codelist_matched)
            for codelist in notmatchCCC:
                codelist_value_list = list(LINZ_codelist_data.loc[LINZ_codelist_data['Codelist'] == codelist]['Code'])
                for codelist_value in codelist_value_list:
                    data_codelist_value = data_codelist_value.append([{'LINZ':codelist_value,'LINZ codelist':codelist}],ignore_index=True)
            
            
            #add CCC codelist values which are not matched to LINZ into dataframe
            codelists = CCC_codelist_data.loc[CCC_codelist_data['GISModelName'] == item]['GISDomainTableName']
            CCC_codelist_matched = codelist_mapping.keys()
            notmatchLINZ = set(codelists)^set(CCC_codelist_matched)
            for cl in notmatchLINZ:
                
                cl_va_list = codelist_value = list(CCC_codelist_data.loc[CCC_codelist_data['GISDomainTableName'] == cl]['GISDomainValue'])
                for cl_va in cl_va_list:
                    data_codelist_value = data_codelist_value.append([{'CCC':cl_va,'CCC codelist':cl}],ignore_index=True)
            
            data_codelist_value['Content'] = data_codelist_value.apply(lambda x: content(x.CCC, x.LINZ), axis = 1)
            data_codelist_value['CCC Attribute'] = data_codelist_value['CCC codelist'].map(lambda x: str(x).strip('dom')).replace('nan','Attribute not in CCC')
            #LINZ column and codelist name dictionary  
            LINZ_df = LINZ_attributes_data[['Asset Class','Attribute Name - Abbreviated','CODELIST Reference']].dropna(axis=0, how='any')
            LINZ_attributes_asset = list(LINZ_df.loc[LINZ_df['Asset Class'] == linz_asset]['Attribute Name - Abbreviated'])
            LINZdict = {}
            for attribute in LINZ_attributes_asset:
                codelist = LINZ_df.loc[(LINZ_df['Asset Class'] == linz_asset)& (LINZ_df['Attribute Name - Abbreviated'] == attribute),'CODELIST Reference'].values[0]
                LINZdict[codelist] = attribute
                
            data_codelist_value['LINZ Attribute'] = data_codelist_value['LINZ codelist'].map(LINZdict)
            data_codelist_value['CCC Asset Class'] = item
            data_codelist_value['LINZ Asset Class'] = linz_asset
            data_codelist_value = data_codelist_value.fillna({'CCC':'CodeList Value Not in CCC.','LINZ':'CodeList Value Not in LINZ.','CCC codelist':'CodeList Name Not in CCC','LINZ codelist':'CodeList Name Not in LINZ','LINZ Attribute':'Attribute not in LINZ'})
            data_codelist_value.rename(columns={'CCC':'CCC Codelist value', 'LINZ':'LINZ Codelist value',}, inplace = True)
            columns = ['CCC Asset Class','CCC Attribute','CCC codelist','CCC Codelist value','Content','LINZ Asset Class','LINZ Attribute','LINZ codelist','LINZ Codelist value','Similarity']
            data_codelist_value = data_codelist_value[columns]
            
            
            #load the layer csv file to get the assets data

            similarity,max_match = max_similarity(item,CCC_asset_file_list)
            CCC_data = pd.read_csv(os.path.join(csv_path, max_match),low_memory=False,encoding='cp1252')
            CCC_data_attributes = list(CCC_data.columns)
            
            #count for affected assets
            statistics_mapping = {}

            for cl in codelists:
                
                similarity,CCC_col = max_similarity(cl,CCC_data_attributes)
                
                stat_mapping = dict(CCC_data[CCC_col].value_counts())
             
                statistics_mapping.update(stat_mapping)

            
            data_codelist_value['Statistics'] = data_codelist_value['CCC Codelist value'].map(statistics_mapping)

            
            
            #save dataframe to excel  
            path = os.path.join(linz_path ,f'{item}(gap analysis).xlsx')
            writer = pd.ExcelWriter(path)
            data_asset.to_excel(writer, sheet_name = 'Asset',index = False)
            ws0 = writer.sheets['Asset']
            fheader = writer.book.add_format({'bold': True,})
            ws0.set_row(0, None, cell_format=fheader)
            ws0.set_column(0,3, width=30)      
            data_attributes.to_excel(writer, sheet_name = 'Attributes',index = False)
            ws1 = writer.sheets['Attributes']
            ws1.set_row(0, None, cell_format=fheader)
            ws1.set_column(0,7, width=25)
            data_codelist.to_excel(writer, sheet_name = 'Codelist name',index = False)
            ws2 = writer.sheets['Codelist name']
            ws2.set_row(0, None, cell_format=fheader)  
            ws2.set_column(0,6, width=25)
            data_codelist_value.to_excel(writer, sheet_name = 'Codelist Values',index = False)
            ws3 = writer.sheets['Codelist Values']
            ws3.set_row(0, None, cell_format=fheader)
            ws3.set_column(0,9, width=20)
            writer.save()
