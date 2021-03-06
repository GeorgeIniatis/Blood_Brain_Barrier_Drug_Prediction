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


def replace_with_nan(working_set, string_to_replace):
    working_set.replace(string_to_replace, np.NaN, inplace=True)


def remove_unknown_compounds(working_set):
    working_set.drop(working_set[working_set['PubChem_CID'] == '-'].index, inplace=True)


def remove_compounds_without_all_chemical_descriptors(working_set):
    for descriptor in ['MW', 'TPSA', 'XLogP', 'NHD', 'NHA', 'NRB']:
        working_set.drop(working_set[working_set[descriptor] == '-'].index, inplace=True)


def load_from_excel(excel_file, worksheet):
    path = f"Dataset_Files/{excel_file}"
    return pd.read_excel(path, worksheet)


def load_from_csv(csv_file):
    path = f"Dataset_Files/{csv_file}"
    return pd.read_csv(path)


def load_to_excel(working_set, new_file_name):
    path = f"Dataset_Files/{new_file_name}"
    working_set.to_excel(path, engine='xlsxwriter')


def load_to_csv(working_set, new_file_name):
    # The large number of synonyms seems to be causing issues when converting the dataframe to csv
    working_set.drop(columns='Synonyms', inplace=True)
    # working_set.replace("-", np.NaN, inplace=True)
    path = f"Dataset_Files/{new_file_name}"
    working_set.to_csv(path)


def recalculate_bbb_permeability(working_set, more_than_or_equal_to_value):
    for index, row in working_set.iterrows():
        logBB = row['logBB']
        if logBB != '-':
            working_set.at[index, 'Class'] = 1 if float(logBB) >= more_than_or_equal_to_value else 0


# Use if SMILES includes backward or forward slash
def post_pubchem_cid_using_smiles(smiles):
    response = requests.post(url=BASE + f"smiles/cids/txt",
                             data={"smiles": smiles},
                             headers={"Content-Type": "application/x-www-form-urlencoded"})
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Use for all other SMILES
def get_pubchem_cid_using_smiles(smiles):
    response = requests.get(BASE + f"smiles/{smiles}/cids/txt")
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Use for all drug names with special characters
def post_pubchem_cid_and_smiles_using_name(name):
    response = requests.post(
        url=BASE + f"name/property/IsomericSMILES,Title/json",
        data={"name": name},
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    if response.status_code == 200:
        if len(response.json()['PropertyTable']['Properties']) == 1:
            pubchem_cid = response.json()['PropertyTable']['Properties'][0]['CID']
            smiles = response.json()['PropertyTable']['Properties'][0]['IsomericSMILES']
            return [pubchem_cid, smiles]
        else:
            for entry_returned in response.json()['PropertyTable']['Properties']:
                if name.lower() == entry_returned['Title'].lower():
                    return [entry_returned['CID'], entry_returned['IsomericSMILES']]

    return None


# Use for drug names without special characters
def get_pubchem_cid_and_smiles_using_name(name):
    response = requests.get(BASE + f"name/{name}/property/IsomericSMILES,Title/json")
    if response.status_code == 200:
        if len(response.json()['PropertyTable']['Properties']) == 1:
            pubchem_cid = response.json()['PropertyTable']['Properties'][0]['CID']
            smiles = response.json()['PropertyTable']['Properties'][0]['IsomericSMILES']
            return [pubchem_cid, smiles]
        else:
            for entry_returned in response.json()['PropertyTable']['Properties']:
                if name.lower() == entry_returned['Title'].lower():
                    return [entry_returned['CID'], entry_returned['IsomericSMILES']]
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
    return None


def get_side_effect_using_sider_cid(sider_side_effects_sorted, sider_cid):
    side_effects_list = []
    index_retrieved = np.searchsorted(sider_side_effects_sorted['SIDER_ID'], sider_cid)

    # Side effects for each drug are one under the other
    while sider_side_effects_sorted.iloc[index_retrieved]['SIDER_ID'] == sider_cid:
        side_effects_list.append(sider_side_effects_sorted.iloc[index_retrieved]['Side_Effect'])
        index_retrieved += 1

    return json.dumps(side_effects_list)


def get_indications_using_sider_cid(sider_indications_sorted, sider_cid):
    indications_list = []
    index_retrieved = np.searchsorted(sider_indications_sorted['SIDER_ID'], sider_cid)

    # Indications for each drug are one under the other
    while sider_indications_sorted.iloc[index_retrieved]['SIDER_ID'] == sider_cid:
        indications_list.append(sider_indications_sorted.iloc[index_retrieved]['Indication_Name'])
        index_retrieved += 1

    return json.dumps(indications_list)


def one_hot_encoding_side_effects(working_set):
    working_set['Side_Effects_JSON'] = ''

    for index, row in working_set.iterrows():
        side_effects_string = row['Side_Effects']
        if side_effects_string != '-':
            working_set.at[index, 'Side_Effects_JSON'] = json.loads(side_effects_string)

    one_hot_side_effects = working_set['Side_Effects_JSON'].str.join('|').str.get_dummies().add_prefix('Side_Effect_')
    joined_set = working_set.join(one_hot_side_effects)
    joined_set.drop(columns=['Side_Effects_JSON'], inplace=True)

    return joined_set


def one_hot_encoding_indications(working_set):
    working_set['Indications_JSON'] = ''

    for index, row in working_set.iterrows():
        indications_string = row['Indications']
        if indications_string != '-':
            working_set.at[index, 'Indications_JSON'] = json.loads(indications_string)

    one_hot_indications = working_set['Indications_JSON'].str.join('|').str.get_dummies().add_prefix('Indication_')
    joined_set = working_set.join(one_hot_indications)
    joined_set.drop(columns=['Indications_JSON'], inplace=True)

    return joined_set


# Assuming you have only the SMILES
def populate_dataset(excel_file, new_file_name):
    # SIDER datasets needed
    # Added column names and in the case of SIDER_Side_Effects and SIDER_Indications kept only PT to reduce size
    sider_cid_name = load_from_csv('SIDER_CID_Name.csv')
    sider_cid_name_sorted = sider_cid_name.sort_values('Drug_Name')

    sider_side_effects = load_from_csv('SIDER_Side_Effects.csv')
    sider_side_effects_sorted = sider_side_effects.sort_values('SIDER_ID')

    sider_indications = load_from_csv('SIDER_Indications.csv')
    sider_indications_sorted = sider_indications.sort_values('SIDER_ID')

    # Our compounds/drug dataset
    working_set = load_from_csv(excel_file)

    fill_nan(working_set)
    recalculate_bbb_permeability(working_set, -1)

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
                    side_effects = '-'
                    indications = '-'

                    # Search all compound synonyms for a hit in the SIDER dataset
                    # If we find a SIDER_CID we exit the for loop and search for any side effects
                    for synonym in synonyms_list:
                        sider_cid = get_sider_cid_using_name(sider_cid_name_sorted, synonym)
                        if sider_cid is not None:
                            side_effects = get_side_effect_using_sider_cid(sider_side_effects_sorted, sider_cid)
                            indications = get_indications_using_sider_cid(sider_indications_sorted, sider_cid)
                            break
                        else:
                            sider_cid = '-'
                            side_effects = '-'
                            indications = '-'
                else:
                    synonyms = '-'
                    name = '-'
                    sider_cid = '-'
                    side_effects = '-'
                    indications = '-'
            else:
                pubchem_cid = '-'
                sider_cid = '-'
                synonyms = '-'
                name = '-'
                side_effects = '-'
                indications = '-'
                descriptors = {'MolecularWeight': '-', 'XLogP': '-', 'TPSA': '-', 'HBondDonorCount': '-',
                               'HBondAcceptorCount': '-', 'RotatableBondCount': '-'}

            molecular_weight = descriptors['MolecularWeight']
            if molecular_weight != '-':
                molecular_weight = float(molecular_weight)

            working_set.at[index, 'Name'] = name
            working_set.at[index, 'PubChem_CID'] = pubchem_cid
            working_set.at[index, 'SIDER_CID'] = sider_cid
            working_set.at[index, 'MW'] = molecular_weight
            working_set.at[index, 'TPSA'] = descriptors['TPSA']
            working_set.at[index, 'XLogP'] = descriptors['XLogP']
            working_set.at[index, 'NHD'] = descriptors['HBondDonorCount']
            working_set.at[index, 'NHA'] = descriptors['HBondAcceptorCount']
            working_set.at[index, 'NRB'] = descriptors['RotatableBondCount']
            working_set.at[index, 'Synonyms'] = synonyms
            working_set.at[index, 'Side_Effects'] = side_effects
            working_set.at[index, 'Indications'] = indications

        else:
            print(f"Skipped: {index}")
            continue

        print(f"Processed: {index}")

        if index == 10:
            break

    # Sort and remove any unknown compounds, compounds without all chemical descriptors and duplicates
    working_set = working_set.sort_values('Name')
    remove_unknown_compounds(working_set)
    remove_compounds_without_all_chemical_descriptors(working_set)
    working_set.drop_duplicates(subset=['PubChem_CID'], inplace=True)
    print(
        "Dataset sorted and any unknown compounds, compounds without all chemical descriptors and duplicates were removed")
    print("Loading everything to excel and csv files")
    load_to_excel(working_set, f"{new_file_name}.xlsx")
    load_to_csv(working_set, f"{new_file_name}.csv")


if __name__ == "__main__":
    populate_dataset('Dataset_Completely_Clean.csv', 'Dataset_Populated')
