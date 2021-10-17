from modify_dataset import *
from rdkit.Chem import Descriptors

if __name__ == "__main__":
    working_set = load_from_excel('Dataset.xlsx', 'Sheet1')

    load_to_excel(working_set, 'Dataset_new.xlsx')
