import spacy
from spacy.pipeline import EntityRuler
from spacy.strings import StringStore
import research_paper_xmljson as RP
import os

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
        self.ruler = EntityRuler(self.nlp).from_disk("./patterns.jsonl")
        #self.ruler = EntityRuler(self.nlp)
        self._current_sentence_idx = 0
        self.TRAIN_DATA = []


    def pre_process(self):
        print('starting preprocess')
        self.nlp.add_pipe(self.ruler, before="ner")
        self.extract_text()
        


    def add_word_to_vocab_permanently(self,word):
        pass
    
    def add_word_to_vocab_temporarely(self, word):
        pass

    def add_stringstore_to_vocab_temporarely(self, file):
        try:
            stringstore = StringStore().from_disk(file)
            for word in stringstore:
                lex = self.nlp.vocab[word]
                self.nlp.vocab[word].is_oov = False
        except:
            print("cannot read stringstore in file " + file)

    # Wandelt den Text von den XML Dokumenten in reinen Text um 
    # diese werden dann im self.output_dir gespeichert
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


    def print_entities(self):
        nlp = spacy.load('en_core_web_sm')
        print(type(self._TEXTS))
        print(type(self._TEXTS[0]))
        print(self._TEXTS[0])
        docs = nlp.pipe(self._TEXTS)
        for doc in docs:
            self.show_ents(doc)


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
            print("check for : " + token.text)
            if token.is_oov:
                unknown_words.append(token)
                print("not found: " + token.text)
                

        return (sentence, unknown_words)

    def add_pattern_to_entity_ruler(self,patterns):
        print(patterns)
        print(type(patterns))
        #patterns = [{"label": "ORG", "pattern": "Apple"},
        # {"label": "GPE", "pattern": [{"lower": "san"}, {"lower": "francisco"}]}]
        self.ruler.add_patterns(patterns)
        self.ruler.to_disk("./patterns.jsonl")

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
            stringstore = StringStore().from_disk(path)
            stringstore.add(word)
        except:
            stringstore = StringStore(word)
        stringstore.to_disk(path)

            

    # def get_next_unknown_word(self):

    #     if len(self.unknown_word_list)==0:
    #         print('length = 0 -> get new paper')
    #         text = self.get_new_plain_text_from_xml_file()
    #         doc = self.nlp(text)
    #         for idx in range(len(doc)):

    #             if doc[idx].text not in self.nlp.vocab:
    #                 self.unknown_word_list.append(doc[idx].text)
    #                 if idx<7:
    #                     start = 0
    #                 else:
    #                     start = idx-7
    #                 if idx>len(doc)-8:
    #                     ende = len(doc)-1
    #                 else:
    #                     ende = idx + 7
    #                 self.unknown_sent_list.append(doc[start:ende].text)
    #     # for token in doc:
    #     #     if token.text not in self.nlp.vocab:
    #     #         self.unknown_word_list.append(token.text)
    #     #         self.unknown_sent_list.append()
    #     print(f"get new entry from worlist with current length of : {len(self.unknown_word_list)}")
    #     uword = self.unknown_word_list.pop()
    #     usent = self.unknown_sent_list.pop()
    #     self.test_whether_exist(uword, usent)
