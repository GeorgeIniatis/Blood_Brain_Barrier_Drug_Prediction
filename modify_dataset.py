from urllib.parse import quote
import pandas as pd
import numpy as np
import requests
import json

BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
DESCRIPTORS = ['MolecularWeight', 'XLogP', 'TPSA', 'HBondDonorCount', 'HBondAcceptorCount', 'RotatableBondCount']

pd.set_option('display.max_columns', None)


# Needed to avoid string to float error associated with NaN
def fill_nan(working_set):
    working_set.fillna('', inplace=True)


def remove_unknown_compounds(working_set):
    working_set.drop(working_set[working_set['PubChem_CID'] == '-'].index, inplace=True)


def load_from_excel(excel_file, worksheet):
    return pd.read_excel(excel_file, worksheet)


def load_to_excel(working_set, new_file_name):
    working_set.to_excel(new_file_name)


def recalculate_bbb_permeability(working_set, more_than_or_equal_to_value):
    working_set['Class'] = np.where(working_set['logBB'] >= more_than_or_equal_to_value, 1, 0)


def post_pubchem_cid_using_smiles(smiles):
    response = requests.post(url=BASE + f"smiles/cids/txt",
                             data={"smiles": smiles},
                             headers={"Content-Type": "application/x-www-form-urlencoded"})
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_pubchem_cid_using_smiles(smiles):
    response = requests.get(BASE + f"smiles/{smiles}/cids/txt")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_pubchem_cid_and_smiles_using_name(name):
    response = requests.get(BASE + f"name/{name}/property/IsomericSMILES/json")
    if response.status_code == 200:
        pubchem_cid = response.json()['PropertyTable']['Properties'][0]['CID']
        smiles = response.json()['PropertyTable']['Properties'][0]['IsomericSMILES']
        return [pubchem_cid, smiles]
    else:
        return None


def get_synonyms(pubchem_cid):
    response = requests.get(BASE + f"cid/{pubchem_cid}/synonyms/json")
    if response.status_code == 200:
        return json.dumps(response.json()['InformationList']['Information'][0]['Synonym'])
    else:
        return None


def get_chemical_descriptors(pubchem_cid):
    response = requests.get(
        BASE + f"cid/{pubchem_cid}/property/MolecularWeight,TPSA,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount/json")
    if response.status_code == 200:
        descriptors_dictionary = response.json()['PropertyTable']['Properties'][0]
        del descriptors_dictionary['CID']

        # Some descriptors are not available for a few rare compounds
        if len(descriptors_dictionary.keys()) != 6:
            for descriptor in DESCRIPTORS:
                if descriptor not in descriptors_dictionary.keys():
                    descriptors_dictionary[descriptor] = '-'

        return descriptors_dictionary
    else:
        return None


def get_sider_cid_using_name(sider_cid_name_sorted, drug_name):
    index_retrieved = np.searchsorted(sider_cid_name_sorted['Drug_Name'], drug_name)
    if index_retrieved < len(sider_cid_name_sorted):
        if drug_name == sider_cid_name_sorted.iloc[index_retrieved]['Drug_Name']:
            return sider_cid_name_sorted.iloc[index_retrieved]['SIDER_ID']
        else:
            return None
    else:
        return None


def get_side_effect_using_sider_cid(sider_side_effects_sorted, sider_cid):
    side_effects_list = []
    index_retrieved = np.searchsorted(sider_side_effects_sorted['SIDER_ID'], sider_cid)

    # Side effects for each drug are one under the other
    while sider_side_effects_sorted.iloc[index_retrieved]['SIDER_ID'] == sider_cid:
        side_effects_list.append(sider_side_effects_sorted.iloc[index_retrieved]['Side_Effect'])
        index_retrieved += 1

    return json.dumps(side_effects_list)


# Assuming you have only the SMILES
def populate_dataset(excel_file, worksheet, new_file_name):
    # SIDER datasets needed. Added columns and in the case of SIDER_Side_Effects kept only PT in order to reduce size
    sider_cid_name = load_from_excel('SIDER_CID_Name.xlsx', 'drug_names')
    sider_cid_name_sorted = sider_cid_name.sort_values('Drug_Name')

    sider_side_effects = load_from_excel('SIDER_Side_Effects.xlsx', 'Sheet1')
    sider_side_effects_sorted = sider_side_effects.sort_values('SIDER_ID')

    # Our compounds/drug dataset
    working_set = load_from_excel(excel_file, worksheet)

    fill_nan(working_set)
    # recalculate_bbb_permeability(working_set, -1)

    for index, row in working_set.iterrows():
        if row['PubChem_CID'] == '':

            row_smiles = row['SMILES']

            # Try to get CID from SMILES
            # If it includes a forward or backward slash use a POST request, otherwise use a GET request
            if ("/" in row_smiles) or ("\\" in row_smiles):
                pubchem_cid = post_pubchem_cid_using_smiles(row_smiles)
            else:
                row_smiles_encoded = quote(row_smiles, safe='')
                pubchem_cid = get_pubchem_cid_using_smiles(row_smiles_encoded)

            if (pubchem_cid is not None) and (pubchem_cid != 0):
                # Get descriptors and synonyms if available
                # Some compounds don't have any synonyms or name
                descriptors = get_chemical_descriptors(pubchem_cid)
                synonyms = get_synonyms(pubchem_cid)

                if synonyms is not None:
                    synonyms_list = json.loads(synonyms)
                    name = synonyms_list[0]
                    sider_cid = '-'

                    # Search all compound synonyms for a hit in the SIDER dataset
                    # If we find a SIDER_CID we exit the for loop and search for any side effects
                    for synonym in synonyms_list:
                        sider_cid = get_sider_cid_using_name(sider_cid_name_sorted, synonym)
                        if sider_cid is not None:
                            side_effects = get_side_effect_using_sider_cid(sider_side_effects_sorted, sider_cid)
                            break
                        else:
                            sider_cid = '-'
                            side_effects = '-'
                else:
                    synonyms = '-'
                    name = '-'
                    sider_cid = '-'
                    side_effects = '-'
            else:
                pubchem_cid = '-'
                sider_cid = '-'
                synonyms = '-'
                name = '-'
                side_effects = '-'
                descriptors = {'MolecularWeight': '-', 'XLogP': '-', 'TPSA': '-', 'HBondDonorCount': '-',
                               'HBondAcceptorCount': '-', 'RotatableBondCount': '-'}

            working_set.at[index, 'Name'] = name
            working_set.at[index, 'PubChem_CID'] = pubchem_cid
            working_set.at[index, 'SIDER_CID'] = sider_cid
            working_set.at[index, 'MW'] = float(descriptors['MolecularWeight']) if descriptors[
                                                                                       'MolecularWeight'] != '-' else \
                descriptors['MolecularWeight']
            working_set.at[index, 'TPSA'] = descriptors['TPSA']
            working_set.at[index, 'XLogP'] = descriptors['XLogP']
            working_set.at[index, 'NHD'] = descriptors['HBondDonorCount']
            working_set.at[index, 'NHA'] = descriptors['HBondAcceptorCount']
            working_set.at[index, 'NRB'] = descriptors['RotatableBondCount']
            working_set.at[index, 'Synonyms'] = synonyms
            working_set.at[index, 'Side_Effects'] = side_effects

        else:
            print(f"Skipped: {index}")
            continue

        print(f"Processed: {index}")

    # Sort and remove any unknown compounds and duplicates
    working_set = working_set.sort_values('Name')
    remove_unknown_compounds(working_set)
    working_set = working_set.drop_duplicates(subset=['PubChem_CID'])

    load_to_excel(working_set, new_file_name)


if __name__ == "__main__":

    working_set = load_from_excel('Dataset.xlsx', 'Sheet1')
    #.replace('\'', '"')
    side_effects = json.loads(working_set.iloc[285]['Side_Effects'])
    print(side_effects)
    for effect in side_effects:
        print(effect)



