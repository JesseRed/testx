pre_string = "{\"label\":\"MEDICATION\",\"pattern\":\""
post_string = "\"}"
with open('G:\OneDrive\Python\SpacyEditor\Lib\drugs.jsonl','x',encoding='utf8') as fw:
    with open('G:\OneDrive\Python\SpacyEditor\Lib\clincalc_drugspell_2018_11u.txt','r',encoding='utf8') as fr:
        idx = 0
        for line in fr:
            new_med = line[:-1]
            new_entry = pre_string + new_med + post_string + '\n'
            fw.write(new_entry)
            #{"label":"MEDICATION","pattern":"Marijuana"}
        