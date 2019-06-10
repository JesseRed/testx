import json
import pandas as pd
from pandas import DataFrame

pre_string = "{\"label\":\"DRUG\",\"pattern\":[{\"LOWER\":\""
post_string = "\"}]}"
infile = 'G:\OneDrive\Python\SpacyEditor\Lib\Products.txt'
outfile = 'G:\OneDrive\Python\SpacyEditor\Lib\drugs_FDA_lower.jsonl'

data = pd.read_csv(infile,delimiter="\t")
df = DataFrame(data, columns=['DrugName','ActiveIngredient'])
drug_name_list = []
[drug_name_list.append(drug) for drug in df['DrugName']]
[drug_name_list.append(drug) for drug in df['ActiveIngredient']]
unique_list = list( dict.fromkeys(drug_name_list) ) 

with open(outfile,'w',encoding='utf8') as fw:
    for drug in unique_list:
        line = pre_string + drug.lower() + post_string + '\n'
        fw.write(line)
        line = pre_string + drug.lower() + 'e' + post_string + '\n'
        fw.write(line)

    
    line = pre_string + "morphin" + post_string + '\n'
    fw.write(line)
    line = pre_string + "morphine" + post_string + '\n'
    fw.write(line)
#{"label":"GPE","pattern":[{"lower":"san"},{"lower":"franciscosfg"}]}

#data.head()




# with open('G:\OneDrive\Python\SpacyEditor\Lib\drugs.jsonl','r',encoding='utf8') as fr:
#     for line in fr:
#         data = json.loads(line.strip())
#         print(data)
#         print(data['pattern'])
        
# def read( file):
#     for i, line in enumerate(open(file)):
#         data = json.loads(line.strip())
#         print(data["label"])
