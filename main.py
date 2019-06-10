import sys
import json
import spacy
from spacy.pipeline import EntityRuler
#sys.path.insert(0, 'G:\Google Drive\SPM\Python\Elsevier Spider\PyQt')
from ck_spacy_model import CkSpacyModel
from spacy import displacy
from qtpy import QtWidgets


from SpacyGUI.mainwindow import Ui_MainWindow


app = QtWidgets.QApplication(sys.argv)

# Comment
#* Important Comment
#! Warning
#? Question
# TODO: Do this or that
# @param myparam Der Parameter
# 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle("spaCyEditor for Scientific Writing Tool")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton_init_home.clicked.connect(self.init)
        self.ui.pushButton_init_work.clicked.connect(self.init)
        self.ui.pushButton_preprocess.clicked.connect(self.pre_process)
        self.ui.pushButton_test.clicked.connect(self.test)
        self.ui.pushButton_get_next_sentence.clicked.connect(self.next_sentence)
        self.ui.pushButton_add_pattern.clicked.connect(self.add_pattern)
        self.sp = None
        self.ui.pushButton_add_sentence_to_TRAIN_DATA.clicked.connect(self.add_sentence_to_TRAIN_DATA)
        self.ui.pushButton_save_selected_to_stringstore.clicked.connect(self.add_selected_word_to_stringstore)
        self.ui.pushButton_add_entity.clicked.connect(self.add_entity_to_json)
        self.ui.pushButton_auto_create_pattern.clicked.connect(self.auto_create_pattern)
        self.ui.pushButton_add_stringstore_temporarly_to_vocab.clicked.connect(self.add_stringstore_to_vocab_temporarely)
        self.ui.pushButton_auto_train_pattern_from_selection.clicked.connect(self.auto_train_pattern_from_selection)
        self.ui.pushButton_add_pattern_reintegrate.clicked.connect(self.reintegrate_pattern_to_spacy)
        self.ui.pushButton_add_drug_patterns_before_ner.clicked.connect(self.add_pattern_jsonl_file_to_vocab_and_entity_matcher)

    def init(self):
        print("Hello Spacy")
        self.ui.lineEdit_text_file_input_dir_XML.setText('G:\Daten\Elsevir_paper\XMLJSON')
        self.ui.lineEdit_text_file_input_dir_TXT.setText('G:\Daten\Elsevir_paper\TXT_extract')
        self.ui.lineEdit_text_file_output_dir.setText('G:\Daten\Elsevir_paper\Spacy_prepro')

    def next_sentence(self):
        if self.sp == None:
            print('preprocess has to be performed first')
            return
        
        (sentence, unknown_words) = self.sp.get_next_sentence()
        train_text = "('" + sentence.text + "', {'entities': [  "
        ent_text = ""
        for ent in sentence.ents:
            ent_text = ent_text + (" " + ent.text + " --- " + ent.label_ + " " +str(spacy.explain(ent.label_)) + "\n")
            train_text += "(" + str(ent.start_char) + ", " + str(ent.end_char) + ", '" + ent.label_ + "'), "
        train_text = train_text[:-2] + "]})"
        self.ui.textEdit_TRAIN_DATA_sentences.setText(train_text)
        # get alternative TExt
        alt_text = self.sp.get_sentence_alt_text(sentence)
        tok_text = ""
        for token in sentence:
            tok_text = tok_text + token.text + "#"
        
        self.ui.textEdit_alt_text_sentence.setText(alt_text)
        self.ui.textEdit_token_sentence.setText(tok_text)
        self.ui.textEdit_entities.setText(ent_text)
        html = displacy.render(sentence, style="ent", page=True)
        self.ui.textEdit_original_sentence.setText(sentence.text)
        self.ui.textEdit_ent_sentence.setText(html)

        # Setting unknown words
        unknown_words_text = []
        for token in unknown_words:
            unknown_words_text.append(token.text)
        self.ui.listWidget_unknown_words.clear()
        self.ui.listWidget_unknown_words.addItems(unknown_words_text)

        

    def pre_process(self):
        input_dir = self.ui.lineEdit_text_file_input_dir_XML.text()
        output_dir = self.ui.lineEdit_text_file_input_dir_TXT.text()
        text_part = []
        if self.ui.checkBox_prepro_abstract.isChecked():
            text_part.append('abstract')
        if self.ui.checkBox_prepro_introduction.isChecked():
            text_part.append('introduction')
        if self.ui.checkBox_prepro_methods.isChecked():
            text_part.append('methods')
        if self.ui.checkBox_prepro_results.isChecked():
            text_part.append('results')
        if self.ui.checkBox_prepro_discussion.isChecked():
            text_part.append('discussion')
        if self.ui.checkBox_prepro_conclusion.isChecked():
            text_part.append('conclusion')
        self.sp = CkSpacyModel(input_dir, output_dir, text_part)
        self.sp.pre_process()
        #sp.print_entities()
        # setting Entity List Widget
        with open(self.ui.lineEdit_entity_file.text(),'r',encoding='utf8') as fp:
            my_entities = json.load(fp)
        for key,item in my_entities.items():
            self.ui.listWidget_entities.addItem(key)
            


    def add_pattern(self):
        pattern = self.ui.textEdit_pattern.toPlainText()
        pattern = eval(pattern)
        file = self.ui.lineEdit_file_to_save_patterns.text()
        self.sp.add_pattern_to_entity_ruler(pattern,file)

    def test(self):
        text = """But Google is starting from behind. The company made a late push
        into hardware, and Apple’s Siri, available on iPhones, and Amazon’s Alexa
        software, which runs on its Echo and Dot devices, have clear leads in
        consumer adoption."""

        nlp = spacy.load("en_core_web_sm")
        doc1 = nlp(text)
        #displacy.serve(doc, style="ent")
        #nlp = spacy.load("en_core_web_sm")
        #doc1 = nlp(u"This is a sentence.")
        doc2 = nlp(u"This is another sentence.")
        html = displacy.render(doc1, style="ent", page=True)
#        html = displacy.render([doc1, doc2], style="ent", page=True)
        self.ui.textEdit_ent_sentence.setText(html)


    def add_sentence_to_TRAIN_DATA(self):
        sentence = self.ui.textEdit_TRAIN_DATA_sentences.toPlainText()
        #tup = eval(sentence)
        filename = self.ui.lineEdit_file_to_save_TRAIN_DATA.text()
        self.sp.add_sentence_to_TRAIN_DATA(sentence,filename)

    def add_selected_word_to_stringstore(self):
        word_list = self.ui.listWidget_unknown_words.selectedItems()
        path = self.ui.lineEdit_stringstore_dir.text()
        for word in word_list:
            self.sp.add_word_to_stringstore(word.text(),path)

    def add_entity_to_json(self):
        new_entity_word = self.ui.lineEdit_entity_to_add.text()
        if len(new_entity_word)==0:
            print("no empty entities allowed")
            return
        with open(self.ui.lineEdit_entity_file.text(),'r',encoding='utf8') as fp:
            my_entities_dict = json.load(fp)
        my_entities_dict[self.ui.lineEdit_entity_to_add.text()] = self.ui.lineEdit_entity_description_to_add.text()
        self.ui.listWidget_entities.clear()
        for key,item in my_entities_dict.items():
            self.ui.listWidget_entities.addItem(key)
        with open(self.ui.lineEdit_entity_file.text(),'w+',encoding='utf8') as fp:
            json.dump(my_entities_dict,fp)
        

    def add_stringstore_to_vocab_temporarely(self):
        self.sp.add_stringstore_to_vocab_temporarely(self.ui.lineEdit_stringstore_dir.text())

    def auto_create_pattern(self):
        word_list = self.ui.listWidget_unknown_words.selectedItems()
        entity_list = self.ui.listWidget_entities.selectedItems()
        if len(word_list)==1:
            new_word = word_list[0].text()
        else:
            new_word = "Placeholder"
        if not len(entity_list)==1:
            print("please select exactly one Word in Entity list")
            return
        entity = entity_list[0].text()
        pattern_string = self.build_pattern_string(entity,new_word)
        self.ui.textEdit_pattern.setText(pattern_string)
        
    def auto_train_pattern_from_selection(self):
        cursor = self.ui.textEdit_original_sentence.textCursor()
#        cursor = self.ui.textEdit_ent_sentence.textCursor()
        new_word = cursor.selectedText()

        entity_list = self.ui.listWidget_entities.selectedItems()
        if not len(entity_list)==1:
            entity = 'Placeholder'
        else:
            entity = entity_list[0].text()
        pattern_string = self.build_pattern_string(entity,new_word)
        self.ui.textEdit_pattern.setText(pattern_string)

        train_text = self.ui.textEdit_TRAIN_DATA_sentences.toPlainText();
        train_text = train_text[:-3]
        if train_text[-1]==')':
            train_text = train_text + ", "
        start_index = cursor.selectionStart()
        stop_index = cursor.selectionEnd()
        new_entity_text = "(" + str(start_index) + ", " + str(stop_index) + ", '" + entity + "')]})"
        print(new_entity_text)
        self.ui.textEdit_TRAIN_DATA_sentences.setText(train_text + new_entity_text)            
#("tAl.", {"entities": [  (102, 115, "DATE"), (194, 196, "ORG"), (203, 213, "REF")]})

    def reintegrate_pattern_to_spacy(self):
        self.sp.reintegrate_patterns_to_ruler(self.ui.lineEdit_file_to_save_patterns.text());

    def add_pattern_jsonl_file_to_vocab_and_entity_matcher(self):
        file = self.ui.lineEdit_drugs_pattern_jsonl.text()
        self.sp.add_pattern_jsonl_file_to_vocab_and_entity_matcher( file)

    def build_pattern_string(self, entity, new_word):
        if self.ui.checkBox_lower.isChecked():
            pattern_string = ("[{'label': '" + entity + "', 'pattern': [{'lower': '" + new_word + "'}]}]")
        else:
            pattern_string = ("[{'label': '" + entity + "', 'pattern': '" + new_word + "'}]")
        return pattern_string

window = MainWindow()
window.show()




sys.exit(app.exec_())