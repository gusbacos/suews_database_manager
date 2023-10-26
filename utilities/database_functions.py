import pandas as pd
import numpy as np
import webbrowser
from pathlib import Path
from time import sleep
from datetime import datetime


def read_DB(db_path):
    '''
    function for reading database and parse it to dictionary of dataframes
    descOrigin is used for indexing and presenting the database entries in a understandable way for the user
    '''

    db_sh = pd.ExcelFile(db_path)
    sheets = db_sh.sheet_names
    db = pd.read_excel(db_path, sheet_name= sheets, index_col= 0)
    # add 
    for col in sheets:
        if col == 'Types':
            db[col]['descOrigin'] = db[col]['Type'].astype(str) + ', ' + db[col]['Origin'].astype(str)
        elif col == 'References': 
            db[col]['authorYear'] = db[col]['Author'].astype(str) + ', ' + db[col]['Publication Year'].astype(str)
        elif col == 'Country':
            db[col]['descOrigin'] = db[col]['Country'].astype(str) + ', ' + db[col]['City'].astype(str)  
        elif col == 'Region':
            pass    
        # Calculate U-values for roof and wall new columns u_value_wall and u_value_roof
        elif col == 'Spartacus Surface':
            db[col]['descOrigin'] = db[col]['Description'].astype(str) + ', ' + db[col]['Origin'].astype(str)
            for row in db['Spartacus Surface'].iterrows():
                id = row[0]
                SS_surf_sel = db['Spartacus Surface'].loc[id]
                resistance_bulk_w = 0
                resistance_bulk_r = 0

                for i in range(1,4):
                    surf_w = SS_surf_sel['w'+str(i)+'Material'].item()
                    thickness_w = SS_surf_sel['w'+str(i)+'Thickness'].item()
                    
                    surf_r = SS_surf_sel['r'+str(i)+'Material'].item()
                    thickness_r = SS_surf_sel['r'+str(i)+'Thickness'].item()

                    try:
                        Tc_w = db['Spartacus Material'].loc[surf_w, 'Thermal Conductivity']
                        resistance_w = thickness_w / Tc_w
                        resistance_bulk_w = resistance_bulk_w + resistance_w
                    except:
                        pass

                    try:
                        Tc_r = db['Spartacus Material'].loc[surf_r, 'Thermal Conductivity']
                        resistance_r = thickness_r / Tc_r
                        resistance_bulk_r = resistance_bulk_r + resistance_r

                    except:
                        print(id, i)
                
                u_value_w = 1/ resistance_bulk_w
                u_value_r = 1/ resistance_bulk_r

                
                db['Spartacus Surface'].loc[id,'u_value_wall'] = u_value_w
                db['Spartacus Surface'].loc[id,'u_value_roof'] = u_value_r

                db['Spartacus Surface'].loc[id,'albedo_roof'] = db['Spartacus Material'].loc[SS_surf_sel['r1Material'], 'Albedo']
                db['Spartacus Surface'].loc[id,'albedo_wall'] = db['Spartacus Material'].loc[SS_surf_sel['w1Material'], 'Albedo']

        else:
            db[col]['descOrigin'] = db[col]['Description'].astype(str) + ', ' + db[col]['Origin'].astype(str)
    return db


def save_to_db(db_path, db_dict):
    for col in list(db_dict.keys()):
        if col == 'References':
            db_dict[col] = db_dict[col].drop(columns = 'authorYear')
        elif col == 'Country' or col == 'Region':
            pass
        else:
            try:
                db_dict[col] = db_dict[col].drop(columns = 'descOrigin')
            except:
                print('ERROR IN SAVE TO DB IN: ' + col)

    with pd.ExcelWriter(db_path) as writer: 
        db_dict['Region'].to_excel(writer, sheet_name='Region')
        db_dict['Country'].to_excel(writer, sheet_name='Country')
        db_dict['Types'].to_excel(writer, sheet_name='Types')
        db_dict['Veg'].to_excel(writer, sheet_name='Veg')
        db_dict['NonVeg'].to_excel(writer, sheet_name='NonVeg')
        db_dict['Water'].to_excel(writer, sheet_name='Water')
        db_dict['Emissivity'].to_excel(writer, sheet_name='Emissivity')
        db_dict['Vegetation Growth'].to_excel(writer, sheet_name='Vegetation Growth')
        db_dict['Water State'].to_excel(writer, sheet_name='Water State')
        db_dict['OHM'].to_excel(writer, sheet_name='OHM')
        db_dict['Albedo'].to_excel(writer, sheet_name='Albedo')
        db_dict['ANOHM'].to_excel(writer, sheet_name='ANOHM')
        db_dict['Biogen CO2'].to_excel(writer, sheet_name='Biogen CO2')
        db_dict['Leaf Area Index'].to_excel(writer, sheet_name='Leaf Area Index')
        db_dict['Water Storage'].to_excel(writer, sheet_name='Water Storage')
        db_dict['Conductance'].to_excel(writer, sheet_name='Conductance')
        db_dict['Leaf Growth Power'].to_excel(writer, sheet_name='Leaf Growth Power')
        db_dict['Drainage'].to_excel(writer, sheet_name='Drainage')
        db_dict['Max Vegetation Conductance'].to_excel(writer, sheet_name='Max Vegetation Conductance')
        db_dict['Porosity'].to_excel(writer, sheet_name='Porosity')
        db_dict['ESTM'].to_excel(writer, sheet_name='ESTM')
        db_dict['Profiles'].to_excel(writer, sheet_name='Profiles')
        db_dict['Irrigation'].to_excel(writer, sheet_name='Irrigation')
        db_dict['Soil'].to_excel(writer, sheet_name='Soil')
        db_dict['Snow'].to_excel(writer, sheet_name='Snow')
        db_dict['AnthropogenicEmission'].to_excel(writer, sheet_name='AnthropogenicEmission')
        db_dict['Spartacus Surface'].to_excel(writer, sheet_name = 'Spartacus Surface')
        db_dict['Spartacus Material'].to_excel(writer, sheet_name = 'Spartacus Material')
        db_dict['References'].to_excel(writer, sheet_name='References')

    for col in list(db_dict.keys()):
        if col == 'Types':
            db_dict[col]['descOrigin'] = db_dict[col]['Type'].astype(str) + ', ' + db_dict[col]['Origin'].astype(str)
        elif col == 'References': 
            db_dict[col]['authorYear'] = db_dict[col]['Author'].astype(str) + ', ' + db_dict[col]['Publication Year'].astype(str)
        elif col == 'Country' or col == 'Region':
            pass
        else:
            db_dict[col]['descOrigin'] = db_dict[col]['Description'].astype(str) + ', ' + db_dict[col]['Origin'].astype(str)

surf_df_dict = {
    'Paved' : 'NonVeg',
    'Buildings' : 'NonVeg',
    'Evergreen Tree' : 'Veg',
    'Decidous Tree' : 'Veg',
    'Grass' : 'Veg',
    'Bare Soil' : 'NonVeg',
    'Water' : 'Water',           
}

code_id_dict = {
    'Region': 10,
    'Country': 11,
    'Types': 12, 

    'NonVeg': 20,
    'Soil': 22,
    'Snow': 23,
    'Veg': 24,
    'Water': 25,

    'Biogen': 30,
    'Leaf Area Index': 31,
    'Leaf Growth Power': 32,
    'Max Vegetation Conductance': 33,
    'Porosity': 34,
    'Vegetation Growth': 35,
    'Spartacus Material' : 36,
    'Spartacus Surface': 37,
    
    'Emissivity': 40,
    'Albedo': 41,   
    'Water State': 42,
    'Water Storage': 43,
    'Conductance': 44,
    'Drainage': 45,

    'OHM': 50,
    'ANOHM': 51,
    'ESTM': 52,
    'AnthropogenicEmission': 53,
    
    'Profiles': 60,
    'Irrigation': 61,
    
    'Ref': 90,
}

def create_code(table_name):

    sleep(0.0000000000001) # Slow down to make code unique
    table_code = str(code_id_dict[table_name]) 
    doy = str(datetime.now().timetuple().tm_yday)
    ms = str(datetime.utcnow().strftime('%S%f')) # Year%DOY#Minute#millisecond
    code = int(table_code + doy + ms[3:])
    return code

param_info_dict = {
    'Albedo': {
        'surface': ['Paved','Buildings','Decidous Tree',  'Evergreen Tree','Grass', 'Bare Soil','Water', 'Snow'],
        'param': {
            'Alb_min': {
                'min': 0,
                'max': 1,
                'tooltip': 'Effective surface albedo (middle of the day value) for wintertime (not including snow).'},
            'Alb_max': {
                'min': 0,
                'max': 1,
                'tooltip': 'Effective surface albedo (middle of the day value) for summertime.'}
                }
            },
    'ANOHM': {'surface': ['Paved','Buildings','Decidous Tree', 'Evergreen Tree','Grass','Bare Soil','Water','Snow'],
            'param': {'AnOHM_Cp': {'min': 0,
                'max': 1,
                'tooltip': 'Volumetric heat capacity for this surface to use in AnOHM [J |m^-3|]'},
            'AnOHM_Kk': {'min': 0,
                'max': 1,
                'tooltip': 'Thermal conductivity for this surface to use in AnOHM [W m |K^-1|]'},
            'AnOHM_Ch': {'min': 0,
                'max': 1,
                'tooltip': 'Bulk transfer coefficient for this surface to use in AnOHM [-]'}}},

    'Biogen CO2': {
        'surface': ['Decidous Tree', 'Evergreen Tree', 'Grass'],
        'param': {'alpha': {'min': 0,
            'max': 1,
            'tooltip': 'The mean apparent ecosystem quantum. Represents the initial slope of the light-response curve. [umol CO2 umol photons^-1]'},
        'beta': {'min': 0, 'max': 1,
            'tooltip': 'The light-saturated gross photosynthesis of the canopy. [umol m-2 s-1 ]'},
        'theta': {'min': 0, 'max': 1,
        'tooltip': 'The convexity of the curve at light saturation.'},
        'alpha_enh': {'min': 0, 'max': 1,
        'tooltip': 'Part of the alpha coefficient related to the fraction of vegetation.'},
        'beta_enh': {'min': 0, 'max': 1, 'tooltip':'Part of the beta coefficient related to the fraction of vegetation.'},
        'resp_a': {'min': 0, 'max': 1, 'tooltip': 'Respiration coefficient a.'},
        'resp_b': {'min': 0, 'max': 1, 'tooltip': 'Respiration coefficient b - related to air temperature dependency.'},
        'min_respi': {'min': 0, 'max': 1, 'tooltip':'Minimum soil respiration rate (for cold-temperature limit) [umol m-2 s-1].'}
            }
        },
    'Conductance': {
        'surface': ['Paved','Buildings','Decidous Tree','Evergreen Tree','Grass','Bare Soil'],
        'param': {
            'G1': {'min': 0,
            'max': 1,
            'tooltip': 'Related to maximum surface conductance [mm |s^-1|]'},
        'G2': {'min': 0,
            'max': 1,
            'tooltip': 'Related to Kdown dependence [W |m^-2|]'},
        'G3': {'min': 0,
            'max': 1,
            'tooltip': 'Related to VPD dependence [units depend on `gsModel`]'},
        'G4': {'min': 0,
            'max': 1,
            'tooltip': 'Related to VPD dependence [units depend on `gsModel`]'},
        'G5': {'min': 0,
            'max': 1,
            'tooltip': 'Related to temperature dependence [°C]'},
        'G6': {'min': 0,
            'max': 1,
            'tooltip': 'Related to soil moisture dependence [|mm^-1|]'},
        'TH': {'min': 0, 'max': 1, 'tooltip': 'Upper air temperature limit [°C]'},
        'TL': {'min': 0, 'max': 1, 'tooltip': 'Lower air temperature limit [°C]'},
        'S1': {'min': 0,
            'max': 1,
            'tooltip': 'A parameter related to soil moisture dependence [-]'},
        'S2': {'min': 0,
            'max': 1,
            'tooltip': 'A parameter related to soil moisture dependence [mm]'},
        'Kmax': {'min': 0,
            'max': 1,
            'tooltip': 'Maximum incoming shortwave radiation [W |m^-2|]'},
        'gsModel': {'min': 0,
            'max': 1,
            'tooltip': 'Formulation choice for conductance calculation.'}
            }
        },
    'Drainage': {
        'surface': ['Paved','Buildings','Decidous Tree','Evergreen Tree','Grass','Bare Soil'],
    'param': {
        'DrainageCoef1': {'min': 0,
        'max': 1,
        'tooltip': 'Coefficient D0 [mm |h^-1|] used in :option:`DrainageEq`'},
    'DrainageCoef2': {
        'min': 0,
        'max': 1,
        'tooltip': 'Coefficient b [-] used in :option:`DrainageEq`'},
    'DrainageEq': {
        'min': 0,
        'max': 1,
        'tooltip': 'Calculation choice for Drainage equation'},
    'WetThreshold': {
        'min': 0, 
        'max': 1, 
        'tooltip': 'Depth of water which determines whether evaporation occurs from a partially wet or completely wet surface [mm].'}
        }
    },
    'Emissivity': {
        'surface':  ['Paved','Buildings','Decidous Tree','Evergreen Tree','Grass','Bare Soil'],
        'param': {'Emissivity': {'min': 0,
            'max': 1,
            'tooltip': 'Effective surface emissivity.'}
                 }
             },
    'Leaf Area Index': {
        'surface': ['Decidous Tree', 'Evergreen Tree', 'Grass'],
        'param': {'LAIEq': {'min': 0,
            'max': 1,
            'tooltip': 'LAI calculation choice.'},
        'LAIMin': {'min': 0, 'max': 1, 'tooltip': 'leaf-off wintertime value'},
        'LAIMax': {'min': 0,
            'max': 1,
            'tooltip': 'full leaf-on summertime value'}}},
    'Leaf Growth Power': {
        'surface': ['Decidous Tree', 'Evergreen Tree', 'Grass'],
        'param': {'LeafGrowthPower1': {'min': 0,
            'max': 1,
            'tooltip': 'a parameter required by LAI calculation in `LAIEq`'},
        'LeafGrowthPower2': {'min': 0,
            'max': 1,
            'tooltip': 'a parameter required by LAI calculation [|K^-1|] in `LAIEq`'},
        'LeafOffPower1': {'min': 0,
            'max': 1,
            'tooltip': 'a parameter required by LAI calculation [|K^-1|] in `LAIEq`'},
        'LeafOffPower2': {'min': 0,
            'max': 1,
            'tooltip': 'a parameter required by LAI calculation [|K^-1|] in `LAIEq`'}
            },
    }, 
    'Max Vegetation Conductance': {
        'surface': ['Decidous Tree','Evergreen Tree','Grass'],
        'param': {'MaxConductance': {'min': 0, 'max': 1, 'tooltip' : 'The maximum conductance of each vegetation or surface type. [mm s-1]'}}},
    'Porosity': {
        'surface': ['Decidous Tree'],
        'param': {'PorosityMin': {'min': 0, 'max': 1, 'tooltip': 'leaf-off wintertime value Used only for DecTr (can affect roughness calculation)'},
        'PorosityMax': {'min': 0, 'max': 1, 'tooltip' : 'full leaf-on summertime value Used only for DecTr (can affect roughness calculation)'}}},
    'Vegetation Growth': {
        'surface': ['Decidous Tree', 'Evergreen Tree', 'Grass'],
        'param': {
            'BaseT': {'min': 0, 'max': 1, 'tooltip':'Base Temperature for initiating growing degree days (GDD) for leaf growth. [°C]'},
            'BaseTe': {'min': 0, 'max': 1, 'tooltip': 'Base temperature for initiating sensesance degree days (SDD) for leaf off. [°C]'},
            'GDDFull': {'min': 0, 'max': 1, 'tooltip': 'The growing degree days (GDD) needed for full capacity of the leaf area index (LAI) [°C].'},
            'SDDFull': {'min': 0, 'max': 1, 'tooltip': 'The sensesence degree days (SDD) needed to initiate leaf off. [°C]'}}},
    'Water State': {
        'surface': ['Water'],
        'param': {
            'StateLimit': {'min': 0, 'max': 1, 'tooltip':'Upper limit to the surface state. [mm]. Currently only used for the water surface. Set to a large value (e.g. 20000 mm = 20 m) if the water body is substantial (lake, river, etc) or a small value (e.g. 10 mm) if water bodies are very shallow (e.g. fountains). WaterDepth (column 9) must not exceed this value.'},
            'WaterDepth': {'min': 0, 'max': 1, 'tooltip': 'Water depth [mm].'}}},
    'Water Storage': {
        'surface': ['Paved',
        'Buildings',
        'Decidous Tree',
        'Evergreen Tree',
        'Grass',
        'Bare Soil',
        'Water'],
        'param': {
            'StorageMin': {'min': 0,'max': 1, 'tooltip': 'Minimum water storage capacity for upper surfaces (i.e. canopy).'},
            'StorageMax': {'min': 0,
                'max': 1,
                'tooltip': 'Maximum water storage capacity for upper surfaces (i.e. canopy)'}}},
    'Soil': {
        'surface': ['No Surface'],
        'param': {
            'SoilDepth': {'min': 0, 'max': 1, 'tooltip': 'Soil density [kg m-3]'},
            'SoilStoreCap': {'min': 0, 'max': 1, 'tooltip': 'Limit value for SoilDepth [mm]'},
            'SatHydraulicCond': {'min': 0, 'max': 1, 'tooltip' : 'Hydraulic conductivity for saturated soil [mm s-1]'},
            'SoilDensity': {'min': 0, 'max': 1, 'tooltip' : 'Soil density [kg m-3]'},
            'InfiltrationRate': {'min': 0, 'max': 1, 'tooltip': 'Infiltration rate (Not currently used)'},
            'OBS_SMCap' : {'min':0,'max':1, 'tooltip': 'The maximum observed soil moisture. [m3 m-3 or kg kg-1]'},
            'OBS_SMDepth': {'min': 0, 'max': 1, 'tooltip':'The depth of soil moisture measurements. [mm]'},
            'OBS_SoilNotRocks': {'min': 0, 'max': 1, 'tooltip':'Fraction of soil without rocks. [-]'}}},

    'OHM': {
        'surface' : ['Paved','Buildings','Decidous Tree',  'Evergreen Tree','Grass', 'Bare Soil','Water', 'Snow'],
        'param'   : {
            'a1': {'tooltip' : 'Coefficient for Q* term [-]'},
            'a2': {'tooltip' : 'Coefficient for dQ*/dt term [h]'},
            'a3': {'tooltip' : 'Constant term [W m-2]'},
        }
    }
}