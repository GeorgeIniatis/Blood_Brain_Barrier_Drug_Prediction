from modify_dataset import get_synonyms, get_cid_using_smiles, get_cid_using_name, BASE, quote


print(quote("CCNC(=N/C#N)\\NCCSCc1c(Br)cccn1", safe=''))
print(get_synonyms(5385314))
