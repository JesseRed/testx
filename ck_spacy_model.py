import spacy
from spacy.pipeline import EntityRuler
from spacy.strings import StringStore
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher

from spacy.tokens import Doc, Token, Span
import research_paper_xmljson as RP
import os
import json
from shutil import copyfile

class CkSpacyModel():

    def __init__(self, xml_dir, output_dir, section_names):
        self.xml_dir = xml_dir
        self.output_dir = output_dir
        self.section_names = section_names
        self.__current_xml_files_for_spacy_preprocessing = []
        self.__filenames = []
        self._TEXTS = []
        self._current_TEXTS_idx = 0
        self.nlp = spacy.load('en_core_web_md')
        self.ruler = EntityRuler(self.nlp,overwrite_ents=True  ).from_disk("./patterns.jsonl")
        #self.ruler = EntityRuler(self.nlp)
        self._current_sentence_idx = 0
        self.TRAIN_DATA = []
        self.stringstore = 0
        self.matcher = Matcher(self.nlp.vocab)
        Token.set_extension("is_unit",  getter= self.is_unit)
        Token.set_extension("alt_text", default = None) #  getter= self.get_alt_text)
        Token.set_extension("alt_text_keep", default = True) #  whether this word should be keeped in the alternative text (necessary because of trailing whitespaces))
        Token.set_extension("alt_text_trailing_whitespace_", default = " ")
        self.matcher_units = PhraseMatcher(self.nlp.vocab) # der PhraseMatcher fuer die Uniterkennung fuer alternative words
        self.matcher_alt_text = Matcher(self.nlp.vocab)
        self.pattern_file_custom_matcher_alt_text = "./Lib/units.jsonl"

    def pre_process(self):
        print('starting preprocess')   
        self.nlp.add_pipe(self.ruler, after="ner")
        self.nlp.add_pipe(self.custom_pipe_component_phrase_entity, before="ner")
        #self.nlp.add_pipe(self.custom_pipe_component_Name_et_al, after="ner")
        #self.nlp.add_pipe(self.custom_pipe_component_Quantity, last=True)
        #self.nlp.add_pipe(self.custom_pipe_component_set_extension_unit, last=True)

        # lade die pattern in den Matcher
        self.custom_matcher_alt_text()
#        self.nlp.add_pipe(self.custom_pipe_component_set_extension_unit_text, last=True)
        self.nlp.add_pipe(self.custom_pipe_comp_alt_text, last = True)
        # als letztes kommt dann die Wortersetzung fuer das simplified english ... 10 mg = xy mg

        self.extract_text()
        
    def reintegrate_patterns_to_ruler(self, file):
        self.ruler = EntityRuler(self.nlp).from_disk(file)
        #self.nlp.remove_pipe("ruler")
        self.nlp.replace_pipe("entity_ruler", self.ruler)
        #self.nlp.add_pipe(self.ruler, before="ner")

        #* The entity ruler is designed to integrate with spaCy’s existing statistical models 
        #* and enhance the named entity recognizer. If it’s added before the "ner" component, 
        #* the entity recognizer will respect the existing entity spans and adjust its 
        #* predictions around it. This can significantly improve accuracy in some cases. 
        #* If it’s added after the "ner" component, the entity ruler will only add spans to 
        #* the doc.ents if they don’t overlap with existing entities predicted by the model. 
        #* To overwrite overlapping entities, you can set overwrite_ents=True on initialization.




    def show_ents(self, doc):
        if doc.ents:
            for ent in doc.ents:
                print(ent.text+' - '+ent.label_+' - '+str(spacy.explain(ent.label_)))
        else:
            print('No named entities found.')

    def get_next_sentence(self):
        self._current_TEXT = self._TEXTS[self._current_TEXTS_idx]
        self._current_doc = self.nlp(self._current_TEXT)
        sentences = list(self._current_doc.sents)
        sentence = sentences[self._current_sentence_idx]
        if self._current_sentence_idx < len(sentences)-1:
            self._current_sentence_idx += 1
        else:
            self._current_sentence_idx = 0
            print('next document')
            if self._current_TEXTS_idx < len(self._TEXTS)-1:
                self._current_TEXTS_idx += 1
            else:
                print('end of Text list')
        sentence = self.nlp(sentence.text)
        unknown_words = []
        for token in sentence:
            #print("check for : " + token.text)
            if token.is_oov:
                unknown_words.append(token)
                #print("not found: " + token.text)
            print(f"token.text = {token.text:{18}} : token._.alt_text = {token._.alt_text:{10}}")
        
        return (sentence, unknown_words)

    def add_pattern_to_entity_ruler(self,patterns,file):
        # die Prufung auf gleiche Lines hab ich nicht hinbekommen
        # daher pruefung auf doppelte und Loeschung von diesen
        self.ruler.add_patterns(patterns)
        self.ruler.to_disk(file)
        uniqlines = set(open(file).readlines())
        with open(file,'w',encoding='utf8') as fp:
            for line in uniqlines:
                fp.write(line)

    def add_sentence_to_TRAIN_DATA(self,sentence, filename):
        exists = os.path.isfile(filename)
        if exists:
            with open(filename,'r',encoding='utf8') as fh:
                for line in fh:
                    one_line = line[:-1]
                    self.TRAIN_DATA.append(one_line)
        self.TRAIN_DATA.append(sentence)
        if exists:
            # haenge nur den einen aktuellen Listeneintrag an
            with open(filename,'a',encoding='utf8') as fh:
                listitem = self.TRAIN_DATA.pop()
                fh.write('%s\n' % listitem)
        if not exists:
            with open(filename,'w+',encoding='utf8') as fh:
                for listitem in self.TRAIN_DATA:
                    fh.write('%s\n' % listitem)

    def add_word_to_stringstore(self, word, path):
        try:
            self.stringstore = StringStore().from_disk(path)
            self.stringstore.add(word)
        except:
            self.stringstore = StringStore(word)
        self.stringstore.to_disk(path)


    def add_word_to_vocab_permanently(self,word):
        pass
    
    def add_word_to_vocab_temporarely(self, word):
        pass

    def add_stringstore_to_vocab_temporarely(self, file):
        try:
            self.stringstore = StringStore().from_disk(file)
            for word in self.stringstore:
                lex = self.nlp.vocab[word]
                self.nlp.vocab[word].is_oov = False
        except:
            print("cannot read stringstore in file " + file)
    

    def add_pattern_jsonl_file_to_vocab_and_entity_matcher(self, pattern_file):
        (ents, pattern) = self.read_gazetteer(pattern_file)
        for i in range(len(ents)-1):
            #print(ents[i])
            #print(pattern[i])
            #print(type(pattern[i]))
            self.matcher.add(ents[i], None, pattern[i])
#           self.matcher.add(entity, None, *phrases)

    

    def read_gazetteer(self, loc):
        pattern = []
        ents = []
        idx = 0
        for i, line in enumerate(open(loc)):
            idx +=1
            data = eval(line.strip())
#            data = json.loads(line.strip())
            # ich fuege zum Vocab den String
            #phrase = self.nlp.tokenizer(data["pattern"])
            #phrase = data["pattern"][0]
            ents.append(data["label"])
            # ich fuege zum matcher das pattenr
            pattern.append(data["pattern"])

            # adde die Worte zum vocab
            #print(f"laenge der phrases = {len(phrases)}")
    #        print(phrase)
            try:
                phrase = ["pattern"][1]["lower"]
                for w in phrase:
                    _ = self.nlp.tokenizer.vocab[w.text]
            except:
                pass
        return (ents, pattern)
        # for i, line in enumerate(open(loc)):
        #     data = json.loads(line.strip())
        #     #! dann duerfen es aber nur einzelne Worte sein
        #     phrase = self.nlp.tokenizer(data["pattern"])
        #     # adde die Worte zum vocab
        #     print(f"laenge der phrases = {len(phrase)}")
        #     for w in phrase:
        #         _ = self.nlp.tokenizer.vocab[w.text]
        #     if len(phrase) >= 2:
        #         yield phrase

#*___________________________________________________________
#*___________________________________________________________
    #* CUSTOM PIPE COMPONENTS     
    #* Hier kommen die Cusom Pipe Components
    #*Aufgabe hauptsaechlich Entitaeten mittels Matchern zu verbessern
    #*Diese werden in der Funktion preproces in die Pipeline integriert
    
    def custom_pipe_component_phrase_entity(self, doc):
        # for ent in doc.ents:
        #     print(ent.text)
        # Apply the matcher to the doc
        matches = self.matcher(doc)
        # Create a Span for each match and assign the label 'ANIMAL'
        spans = [Span(doc, start, end, label=match_id) for match_id, start, end in matches]
        # Overwrite the doc.ents with the matched spans

        try:
            doc.ents = list(doc.ents) + spans
        except:
            print(f"overlapping Entities with {spans}")
#        doc.ents = spans
        return doc     

    def custom_pipe_component_Name_et_al(self, doc):
        print("entering_custom_pipe_component Name et al")
        new_ents = [] 
        for ent in doc.ents:
            print(f"ent = {ent}")
            # Only check for title if it's a person and not the first token
            replaced = False
        
            if ent.label_ == "PERSON":# and ent.end<len(doc)-2:
                # gib das neue label if et al. is in person or after Person
                if 'et' in ent.text and ('al' in ent.text or 'al.' in ent.text):
                    new_ent = Span(doc, ent.start, ent.end, label="REF")
                    replaced = True
                    print("new ents")
                else:
                    # wir schauen ob die danach folgenden et al sind
                    print("within label Person")
                    next_token = doc[ent.end +  1]
                    next_next_token = doc[ent.end + 2]
                    print(next_token.text)
                    print(next_next_token.text)
                    if next_token.text == "et" and next_next_token.text in ("al.", "al"):
                        new_ent = Span(doc, ent.start, ent.end+2, label="REF")
                        new_ents.append(new_ent)
                        replaced = True
                        print("new_ent")


            # es wird das neue angehangen
            if replaced:
                new_ents.append(new_ent)
                print('new ent')
            else:
            # es wird die alte Entitaet uveraendert uebertragen
                new_ents.append(ent)
                print("old ents")
            
        doc.ents = new_ents
        print(doc.ents)
        return doc     

    def custom_pipe_component_Quantity(self, doc):
       # 10 mg macht er meist als 10(CARDINAL) mg
       # Ziel 10 mg (QUANTITY)
        print("entering_custom_pipe_component Quantity")
        print(doc.text)
        new_ents = []
        for ent in doc.ents:
            print(ent.text)
            print(ent.label_)
            # Only check for title if it's a person and not the first token
            replaced = False
            if ent.label_ == "CARDINAL":# and ent.end<len(doc)-2:
                next_token = doc[ent.end]
                if next_token.text in ["mg", "g"]:
                    new_ent = Span(doc, ent.start, ent.end+1, label="QUANTITY")
                    replaced = True
            # es wird das neue angehangen
            if replaced:
                new_ents.append(new_ent)
                print('new ent')
            else:
            # es wird die alte Entitaet uveraendert uebertragen
                new_ents.append(ent)
                print("old ents")


        try:
            doc.ents = new_ents
        except:
            print("overlapping Entities in Quantity")
            for ent in new_ents:
                print(f"ent = {ent.text}   start = {ent.start}   stop = {ent.end}  label = {ent.label_}")
        #print(doc.ents)
        return doc     



    def custom_pipe_component_set_extension_unit(self, doc):
        pass
#*___________________________________________________________
#*___________________________________________________________
    #* EXTENSION Methods
    # Hier kommen die EXTENSION Methods
    # Hauptaufgabe ist das setzen von user defined Attributes, Propertien and Methods
    #Hauptziel fuer bestimmte Tokens ein neues text Token mit simplified english 
    #zu
    

    def custom_pipe_comp_alt_text(self, doc):
        # setze standardmaessig den alternativ text auf den Orginaltext
        for token in doc:
            token._.alt_text = token.text
            token._.alt_text_trailing_whitespace_ = token.whitespace_
        # nun wird der Matcher aufgerufen, der nach verschiedenen Regeln sucht
        # diese gefundenen Regeln werden danach abgefangen und der Alternativtext
        # wird entsprechend dieser Regeln gesetzt
        matches = self.matcher_alt_text(doc)
        # Create a Span for each match and assign the label 'ANIMAL'
        for match_id, start, end in matches:
            # Zahl die allein steht und als ent Type Cardinal ist
            if self.nlp.vocab.strings[match_id]=="NUMCARDINAL":
                doc[start]._.alt_text = "NUM"

            # UNITS
            # Wenn UNITS allein stehen 
            if self.nlp.vocab.strings[match_id]=="UNITS":
                doc[start]._.alt_text = "UNITS"
            # Wenn Units nach einer Zahl als eigenes Token stehen
            if self.nlp.vocab.strings[match_id]=="NUM_UNIT":
                doc[start]._.alt_text = "99"
                doc[start+1]._.alt_text = "UNITS" 
            # WEnn Units nach einer Zahl in einem Token stehen
            if self.nlp.vocab.strings[match_id]=="NUMUNIT": # zahl und Einheit wurde zusammen geschrieben
                doc[start]._.alt_text = "99UNITS"

            if self.nlp.vocab.strings[match_id]=="DRUGNAME":
                doc[start]._.alt_text = "DRUGNAME"
            if self.nlp.vocab.strings[match_id]=="NAMEETAL":
                doc[start]._.alt_text = "REF"
                doc[start+1]._.alt_text = "not to keep"
                doc[start+1]._.alt_text_keep = False
                doc[start+2]._.alt_text = "not to keep"
                doc[start+2]._.alt_text_keep = False
                doc[start+3]._.alt_text = "not to keep"
                doc[start+3]._.alt_text_keep = False
                
            if self.nlp.vocab.strings[match_id]=="REFx":
                doc[start]._.alt_text = "REF"
            if self.nlp.vocab.strings[match_id]=="REFS":
                doc[start]._.alt_text = "REF"
            if self.nlp.vocab.strings[match_id]=="REFpunkt":
                doc[start]._.alt_text = "REF"
            if self.nlp.vocab.strings[match_id]=="XYMIN":
                doc[start]._.alt_text = "XYMIN"
            if self.nlp.vocab.strings[match_id]=="XY-YEARREG":
                doc[start]._.alt_text = "99-year"
            if self.nlp.vocab.strings[match_id]=="XYYEARREG":
                doc[start]._.alt_text = "99year"
            if self.nlp.vocab.strings[match_id]=="XYMINREG":
                doc[start]._.alt_text = "99min"
            if self.nlp.vocab.strings[match_id]=="XY-MINREG":
                doc[start]._.alt_text = "99-min"

            if self.nlp.vocab.strings[match_id]=="XY_PROCENT":
                doc[start]._.alt_text = "99"
                doc[start+1]._.alt_text = "%"

            if self.nlp.vocab.strings[match_id]=="XY-RECEPTOR":
                doc[start]._.alt_text = "XY"
                doc[start+1]._.alt_text = "-"
                doc[start+2]._.alt_text = "receptor"
            if self.nlp.vocab.strings[match_id]=="XY_RECEPTOR":
                doc[start]._.alt_text = "XY"
                doc[start+1]._.alt_text = "receptor"


# {"label":"REFS","pattern":[{"TEXT": "AuthorsEtAl"}]}
# {"label":"REFx","pattern":[{"TEXT": "AuthorEtAl"}]}

#            doc[start]._.alt_text = doc[start].text + " " + self.nlp.vocab.strings[match_id] + " gefunden"
#        spans = [Span(doc, start, end, label=match_id) for match_id, start, end in matches]

        return doc   

    def custom_matcher_alt_text(self):
        pattern_file = self.pattern_file_custom_matcher_alt_text
        (ents, pattern) = self.read_pattern_matcher_file(pattern_file)
        for i in range(len(ents)-1):

            self.matcher_alt_text.add(ents[i], None, pattern[i])
 #           self.matcher.add(entity, None, *phrases)
        # pattern = []
        # pattern.append([{'IS_DIGIT': True}, {'LOWER':'ng'}])
        # pattern.append([{'IS_DIGIT': True}, {'LOWER':'mg'}])
        # self.matcher_units2.add('UNITS', None, *pattern)
    
    


    # diese Funktion soll den Text jedes Tokens setzen
    def custom_pipe_component_set_extension_unit_text(self, doc):
        # rufe den PhraseMatcher fuer die units auf
        #self.matcher_units2 = Matcher(self.nlp.vocab)
        self.add_pattern_jsonl_file_Phrasematcher("./Lib/units.jsonl")
        matches = self.matcher_units(doc)
        # Create a Span for each match and assign the label 'ANIMAL'
        for match_id, start, end in matches:
            doc[start]._.alt_text = doc[start].text + "_ unit gefunden"
#        spans = [Span(doc, start, end, label=match_id) for match_id, start, end in matches]

        return doc     


    def is_unit(self,token):
        return token.text == "mg"

    #def get_alt_text(self,token):
    #    return token._.alt_text




    def add_pattern_jsonl_file_Phrasematcher(self, pattern_file):
        (ents, unit_pattern) = self.read_gazetteer2(pattern_file)
        for i in range(len(ents)-1):
            #matcher_units.add("Units", None, *list(nlp.pipe(COUNTRIES)))
            self.matcher_units.add("UNITS", None, *list(self.nlp.pipe(unit_pattern)))
#            self.matcher_units.add(ents[i], None, pattern[i])
#           self.matcher.add(entity, None, *phrases)


    def read_gazetteer2(self, loc):
        pattern = []
        ents = []
        idx = 0
        for i, line in enumerate(open(loc)):
            idx +=1
            data = eval(line.strip())
            ents.append(data["label"])
            # ich fuege zum matcher das pattenr
            pattern.append(data["pattern"])
        return (ents, pattern)



    def read_pattern_matcher_file(self, loc):
        pattern = []
        ents = []
        for i, line in enumerate(open(loc)):
            data = eval(line.strip())
            ents.append(data["label"])
            pattern.append(data["pattern"])
        return (ents, pattern)

#*___________________________________________________________
#*___________________________________________________________
    #* Text Extraction von XML to txt     
    # Wandelt den Text von den XML Dokumenten in reinen Text um 
    #diese werden dann im self.output_dir gespeichert
    #
    def extract_text(self):
        idx = 0
        for file in os.listdir(self.xml_dir):
            print(f'schleife extract text with : {idx} ')
            if file.endswith('.xml'):
                input_filename = os.path.join(self.xml_dir, file)
                if len(self.section_names)==1:
                    prefix = self.section_names[0]
                else:
                    prefix = 'section_mix'

                output_filename = os.path.join(self.output_dir, prefix + '_' + file)
                print(output_filename)
                self.__current_xml_files_for_spacy_preprocessing.append(input_filename)

                with open(input_filename, "r", encoding="utf8") as f1:
                    print('-------------------------')
                    print('filename:' + input_filename)
                    xml = f1.read()
                    P = RP.Research_Paper_XMLJSON(xml, "json")
                    P.development_test()
                    #P.analyse_parsing()
                    rtext = ''
                    for section_name in self.section_names:
                        rtext = rtext + P.get_part_of_text(section_name)
                    #print(rtext)

                with open(output_filename,"w+", encoding="utf8") as f2:
                    self._TEXTS.append(rtext)
                    f2.write(rtext)
                idx += 1
            # ! This has to be removed in further versions    
            if idx > 10:
                break



    def get_sentence_alt_text(self, sent):
        # uebergabe eines doc objects /// sentence
        # rueckgabe eines TExtes das den alternativen TExt nutzt
        alt_text = ""
        sent_org_text = sent.text
        for token in sent:
            if token._.alt_text_keep:
                alt_text = alt_text + token._.alt_text + token._.alt_text_trailing_whitespace_
        return alt_text

    # def print_entities(self):
    #     nlp = spacy.load('en_core_web_sm')
    #     print(type(self._TEXTS))
    #     print(type(self._TEXTS[0]))
    #     print(self._TEXTS[0])
    #     docs = nlp.pipe(self._TEXTS)
    #     for doc in docs:
    #         self.show_ents(doc)

# Cardinal leerzeichen mg dann Quantity 
# vielleicht doch als Worteigenschaften das simplified Sentences einfuehren 
# eigenschaft fuer ein Token ._.is_simplified und ._.simp_text 

    # def drug_entities(self):
        
    #     matcher = Matcher(self.nlp.vocab)

    
    # def read_jsonl(self, file):
    #     with open(file,'r',encoding='utf8') as fr:
    #         for line in fr:
    #             data = json.loads(line.strip())
    #             print(data)
    #             print(data['pattern'])
    #             #rulertmp = EntityRuler(self.nlp).from_disk(file)
    #             #self.nlp.add_pipe(rulertmp, before="ner")
    #             print(f"patterns added from file {file}")
