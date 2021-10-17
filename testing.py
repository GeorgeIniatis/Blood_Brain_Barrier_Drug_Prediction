from modify_dataset import *

working_set = load_from_excel('Dataset_New.xlsx', 'Sheet1')
remove_unknown_compounds(working_set)

load_to_excel(working_set, 'Dataset_Test.xlsx')
