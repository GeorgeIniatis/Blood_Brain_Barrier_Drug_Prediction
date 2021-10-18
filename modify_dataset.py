from urllib.parse import quote
import pandas as pd
import numpy as np
import requests

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


def post_cid_using_smiles(smiles):
    response = requests.post(url=BASE + f"smiles/cids/txt",
                             data={"smiles": smiles},
                             headers={"Content-Type": "application/x-www-form-urlencoded"})
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_cid_using_smiles(smiles):
    response = requests.get(BASE + f"smiles/{smiles}/cids/txt")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_cid_using_name(name):
    response = requests.get(BASE + f"name/{name}/cids/json")
    if response.status_code == 200:
        return response.json()['IdentifierList']['CID']
    else:
        return None


def get_synonyms(cid):
    response = requests.get(BASE + f"cid/{cid}/synonyms/json")
    if response.status_code == 200:
        return response.json()['InformationList']['Information'][0]['Synonym']
    else:
        return None


def get_chemical_descriptors(cid):
    response = requests.get(
        BASE + f"cid/{cid}/property/MolecularWeight,TPSA,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount/json")
    if response.status_code == 200:
        descriptors_dictionary = response.json()['PropertyTable']['Properties'][0]
        del descriptors_dictionary['CID']

        if len(descriptors_dictionary.keys()) != 6:
            for descriptor in DESCRIPTORS:
                if descriptor not in descriptors_dictionary.keys():
                    descriptors_dictionary[descriptor] = '-'

        return descriptors_dictionary
    else:
        return None


def populate_dataset(working_set):
    # Try to get CID from SMILES
    # If it includes a forward or backward slash use a POST request, otherwise use a GET request
    for index, row in working_set.iterrows():
        row_smiles = row['SMILES']

        if ("/" in row_smiles) or ("\\" in row_smiles):
            cid = post_cid_using_smiles(row_smiles)
        else:
            row_smiles_encoded = quote(row_smiles, safe='')
            cid = get_cid_using_smiles(row_smiles_encoded)

        if (cid is not None) and (cid != 0):
            descriptors = get_chemical_descriptors(cid)
            synonyms = get_synonyms(cid)

            if synonyms is not None:
                name = synonyms[0]
            else:
                synonyms = '-'
                name = '-'
        else:
            cid = '-'
            synonyms = '-'
            name = '-'
            descriptors = {'MolecularWeight': '-', 'XLogP': '-', 'TPSA': '-', 'HBondDonorCount': '-',
                           'HBondAcceptorCount': '-', 'RotatableBondCount': '-'}

        working_set.at[index, 'Name'] = name
        working_set.at[index, 'PubChem_CID'] = cid
        working_set.at[index, 'MW'] = float(descriptors['MolecularWeight']) if descriptors['MolecularWeight'] != '-' else descriptors['MolecularWeight']
        working_set.at[index, 'TPSA'] = descriptors['TPSA']
        working_set.at[index, 'XLogP'] = descriptors['XLogP']
        working_set.at[index, 'NHD'] = descriptors['HBondDonorCount']
        working_set.at[index, 'NHA'] = descriptors['HBondAcceptorCount']
        working_set.at[index, 'NRB'] = descriptors['RotatableBondCount']
        working_set.at[index, 'Synonyms'] = synonyms

        print(index)


if __name__ == "__main__":
    working_set = load_from_excel('Dataset.xlsx', 'Whole Set')
    fill_nan(working_set)
    recalculate_bbb_permeability(working_set, -1)

    print(working_set.shape)
    populate_dataset(working_set)

    remove_unknown_compounds(working_set)
    load_to_excel(working_set, 'Dataset_new.xlsx')
