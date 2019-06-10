# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 12:28:47 2018

@author: Carsten
"""
#Es wird hier die Class angelegt mit der das Research paper struktuiert wird
# Idee ist, dass jeweils der html-source code eines papers uebergeben wird
# und damit alle Informationen zusammengesammelt werden
from bs4 import BeautifulSoup
import pickle
#from nltk import sent_tokenize
import xml.etree.ElementTree as ET
import re
import json
#class Paper():
#    
#    def _inti_(self,html):
#        self._Abstract = get_abstract_from_html(html)
#        self._Authors = get_authors_from_html(html)
#        self._Journal = get_journal_from_html(html)

class Research_Paper_XMLJSON():
    
    def __init__(self, xml, jsonx):
        self._html = ''
        self._xml = xml
        self._json = jsonx
        self._title = ''
        self._url = ''
        self._pii = ''
        self._doi = ''
        self._publicationName = ''
        self._aggregationType= ''
        self._format = ''
        self._issn = ''
        self._volume = ''
        self._identifier = ''
        self._eid = ''
        self._publisher = ''
        self._Authors_name = []
        self._openaccess = ''
        self._openaccessType = ''
        self._openaccessArticle = ''
        self._openArchiveArticle = ''
        self._openaccessSponsorName = []
        self._openaccessSponsorType = []
        self._openaccessUserLicense = ''
        self._subject = []
        self._link_api = ''
        self._link_scidir = ''
        self._abstract = ''
        self._scopus_id = ''
        self._scopus_eid = ''
        self._pubmed_id = ''
        self._year = ''
        self._item_weight = ''
        self._document_type = ''
        self._document_subtype = ''
        self._xml_text_figure = []
        self._xml_text_table = []
        self._xml_text_abstract = ''
        self._xml_text_abstract_structured = [] # background/Methods/results/discussion/Conclusion
        self._xml_text_introduction = ''
        self._xml_text_methods = ''
        self._xml_text_results = ''
        self._xml_text_discussion = ''
        self._xml_text_conclusion = ''
        self._xml_text_acknowledgment = ''
        self._xml_text_author_contributions = ''
        self._xml_text_funding = ''
        self._xml_text_competing_interests = ''
        self._xml_text_availability_of_data_and_material = ''
        self._xml_text_ethics = ''
        self._xml_text_limitations = ''
        self.dictOfSectionTagsToReplace = {'cross-ref': 'AuthorEtAl', 'cross-refs': 'AuthorsEtAl', 'math': 'CkMath', 'grant-sponsor':'CkGrantSponsorName', 'grant-number': 'CkGrantNumber'}
        self.listOfSectionTagsToPassOver = ['float-anchor', 'glyph', 'inter-ref', 'display', 'list', 'list-item', 'footnote', 'displayed-quote', 'enunciation', 'inline-figure', 'vsp', 'hsp', 'cross-out']
        self.listOfSectionTagsToTakeWith = ['italic', 'bold', 'sup', 'inf', 'small-caps','monospace', 'underline', 'sans-serif']
        self.__the_last_section = 'no entry'

        self.__introduction_headline_names = ['Introduction', 'Background', 'Theory']
        self.__methods_headline_names = ['Methods', 'Method', 'Patients and methods', 'Data analysis.', 'Materials and methods',
                                         'Material and methods', 'Materials', 'Methodology', 'Experimental setup', 'General method',
                                         'General methods', 'Statistics', 'Materials and experiments', 'Data description',
                                         'Datasets', 'Experimental methods', 'Experimental Methods', 'Data and experiment']
        self.__results_headline_names = ['Results', 'Result', 'Experimental results', 'Experimental result']
        self.__discussion_headline_names = ['Discussion', 'General discussion', 'Overall discussion', 'Experimental results and discussion',
                                            'Discussion and conclusion']
        self.__conclusion_headline_names = ['Conclusion', 'Conclusions', 'Concluding remarks', 'Concluding comments', 'Summary' ]
        self.__contributions_headline_names = ['Contributions', 'Author contributions', 'Author contribution' ]
        self.__funding_headline_names = ['Funding']
        self.__interests_headline_names = ['Competing interests', 'Competing financial interests', 'Declaration of conflicting interests',
                                           'Potential conflicts of interest', 'Conflicts of interest', 'Conflict of interest',
                                           'Conflict of Interest', 'Conflicts of Interest', 'Declarations of interest', 'Disclosure statement',
                                           'Disclosure','Declaration of Interest']
        self.__data_availability_headline_names = ['Availability of data and material']
        self.__ethics_headline_names = ['ethical standards', 'Ethical standards']
        self.__limitations_headline_names = ['limitations', 'Limitations of the proposed study']



    def split_to_sentences(self, text):
        #print('split_to_sentences')
        #print(text)
        #print(len(text))
        #print(type(text))
        # ! auskommentiert wegen spacy 
        #sentence = sent_tokenize(text)
        #self._text_Introduction_sentences = sent_tokenize(text)
        return(sentence)
    
    # def add_Citation_Information_NeuroImage(self,html_content):
    #     self._citation_pii = self._get_Citation_Information_NeuroImage(html_content,'name','citation_pii')
    #     self._citation_issn = self._get_Citation_Information_NeuroImage(html_content,'name','citation_issn')
    #     self._citation_volume = self._get_Citation_Information_NeuroImage(html_content,'name','citation_volume')
    #     self._citation_lastpage = self._get_Citation_Information_NeuroImage(html_content,'name','citation_lastpage')
    #     self._citation_issue = self._get_Citation_Information_NeuroImage(html_content,'name','citation_issue')
    #     self._citation_publisher = self._get_Citation_Information_NeuroImage(html_content,'name','citation_publisher')
    #     self._citation_firstpage = self._get_Citation_Information_NeuroImage(html_content,'name','citation_firstpage')
    #     self._citation_journal_title = self._get_Citation_Information_NeuroImage(html_content,'name','citation_journal_title')
    #     self._citation_type = self._get_Citation_Information_NeuroImage(html_content,'name','citation_type')
    #     self._citation_doi = self._get_Citation_Information_NeuroImage(html_content,'name','citation_doi')
    #     self._dcidentifier = self._get_Citation_Information_NeuroImage(html_content,'name','dc.identifier')
    #     self._citation_article_type = self._get_Citation_Information_NeuroImage(html_content,'name','citation_article_type')
    #     self._Article_type = self._get_Citation_Information_NeuroImage(html_content,'name','citation_article_type')
    #     self._citation_title = self._get_Citation_Information_NeuroImage(html_content,'name','citation_title')
    #     self._citation_publication_date = self._get_Citation_Information_NeuroImage(html_content,'name','citation_publication_date')
    #     self._citation_online_date = self._get_Citation_Information_NeuroImage(html_content,'name','citation_online_date')
    #     self._citation_pdf_url = self._get_Citation_Information_NeuroImage(html_content,'name','citation_pdf_url')
    #     self._Year = int(self._citation_publication_date[0:4])
    #
    def prints(self):
        print(self._publicationName)
        print(self._title)
        print(self._)
        print(self._citation_publication_date)
        print(self._year)
        print(self._text_Abstract)
        print('\n ---- in Sentences ----')
        print(self._text_Abstract_sentences)
        print('\nKeywords:')
        for i in range(len(self._Keywords)):
            print(self._Keywords[i])
        print('\nAuthors:')
        for i in range(len(self._Authors_surname)):
            print(self._Authors_givenname[i] + ' ' +self._Authors_surname[i] )
        print(self._url)
        #print(type(self._text_Introduction))
        print(self._text_Introduction)
        #print('\n ---- in Sentences ----')
        #self.split_to_sentences(self._text_Introduction)
#        print(self._text_Introduction_sentences)
        print('\n ---- in Sentences ----')
        print(self._text_Introduction_sentences)
        #print(type(self._text_Introduction_sentences))
        print('\n ---- Results in string ----')
        print(self._text_Results)
        print('\n ---- in Sentences ----')
        print(self._text_Results_sentences)
        print('\n ---- Discussion in string ----')
        print(self._text_Discussion)
        print('\n ---- in Sentences ----')
        print(self._text_Discussion_sentences)
        
        print('\n ---text Figure--')
        
        print(self._text_Figure_sentences)
        #print(self._text_Table)
        #print('\nArticle type: ' +  self._citation_article_type)


    def analyse_coredata(self, root):
        #print('analyse_coredata')
        for child in root:
            zugeordnet = 0
            if child.tag == 'doi':
                #print('doi found = ' + child.text)
                self._doi = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'pii':
                self._pii = child.text
                #print('pii = ' + child.text)
                zugeordnet = zugeordnet + 1
            if child.tag == 'title':
                self._title = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'url':
                self._url = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'publicationName':
                self._publicationName = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'aggregationType':
                self._aggregationType = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'issn':
                self._issn = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'volume':
                self._volume = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'identifier':
                self._identifier = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'eid':
                self._eid = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'publisher':
                self._publisher = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'creator':
                self._Authors_name.append(child.text)
                zugeordnet = 1
            if child.tag == 'openaccess':
                self._openaccess = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'openaccessType':
                self._openaccessType = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'openaccessArticle':
                self._openaccessArticle = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'openArchiveArticle':
                self._openArchiveArticle = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'openaccessSponsorName':
                self._openaccessSponsorName = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'openaccessSponsorType':
                self._openaccessSponsorType = child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'openaccessUserLicense':
                self._openaccessUserLicense= child.text
                zugeordnet = zugeordnet + 1
            if child.tag == 'subject':
                self._subject.append(child.text)
                zugeordnet = 1
            if child.tag == 'format':
                self._format = child.text

            if child.tag == 'link':
                if len(child.attrib)==2:
                    if child.attrib['rel']=='self':
                        self._link_api = child.attrib['href']
                        zugeordnet = zugeordnet + 1
                    if child.attrib['rel'] == 'scidir':
                        self._link_scidir = child.attrib['href']
                        zugeordnet = zugeordnet + 1
            if child.tag == 'description':
                if child.text is not None:
                    self._abstract = child.text
                zugeordnet = zugeordnet + 1

            # if zugeordnet != 1:
            #     print("child konnte nicht zugeordnet werdern")
            #     print("tag, attrig")
            #     print(child.tag, child.attrib)
            #     print("text")
            #     print(child.text)


    def analyse_objects(self, root):
        # currently not of interest
        pass

    def analyse_scopus_id(self, root):
        #print('analyse scopus id')
        self._scopus_id = root.text

    def analyse_scopus_eid(self, root):
        #print('analyse_scopus eid')
        self._scopus_eid = root.text

    def analyse_pubmed_id(self, root):
        #print('analyse_scopus eid')
        self._pubmed_id = root.text

    def analyse_link(self, root):
        # currently not of interest
        x = 1
        #print('analyse link')



    def analyse_originalText(self, root):
        #Sprint('-------------------------')
        #print('analyse originalText')
        # originalText
        # --doc
        # ----meta              meta information
        # ----serial-item       text
        for mynode in root.iter('item-weight'):
            self._item_weight = mynode.text

        for mynode in root.iter('document-type'):
            self._document_type = mynode.text
        for mynode in root.iter('document-subtype'):
            self._document_subtype = mynode.text

            #print(self._item_weight)

        doc = root.find("./doc")

        #print(doc.attrib)

        # print('schleife iter')
        # for node in root.iter():
        #     print(node.tag)
        for table in root.iter('table'):
            self.get_table_text(table)


        for figure in root.iter('figure'):
            self.get_figure_text(figure)

        for sections in root.iter('sections'):
            #print('into sectiosn')
            self.analyse_sections(sections)
        #manchmal steht das acknowledgment nicht in den sections sondern ausserhalb
        #if len(self._xml_text_acknowledgment)==0:
        for ack in root.iter('acknowledgment'):
            self._xml_text_acknowledgment = self.get_text_from_acknowledgment(ack)


    def analyse_sections(self,sections):
        for section in sections:
            if section.tag.find('section')>=0:
                section_name = self.get_section_name(section)
                if section_name=='introduction':
                    self._xml_text_introduction = self._xml_text_introduction + self.get_text_from_section(section)
                if section_name == 'materials-methods':
                    self._xml_text_methods = self._xml_text_methods + self.get_text_from_section(section)
                if section_name == 'results':
                    self._xml_text_results = self._xml_text_results + self.get_text_from_section(section)
                if section_name == 'discussion':
                    self._xml_text_discussion = self._xml_text_discussion + self.get_text_from_section(section)
                if section_name == 'conclusion':
                    self._xml_text_conclusion = self._xml_text_conclusion + self.get_text_from_section(section)
                if section_name == 'conclusion':
                    self._xml_text_acknowledgment = self._xml_text_acknowledgment + self.get_text_from_section(section)
                if section_name == 'author_contributions':
                    self._xml_text_author_contributions = self.get_text_from_section(section)
                if section_name == 'funding':
                    self._xml_text_funding = self.get_text_from_section(section)
                if section_name == 'competing_interests':
                    self._xml_text_competing_interests= self.get_text_from_section(section)
                if section_name == 'availability_of_data_and_material':
                    self._xml_text_availability_of_data_and_material = self.get_text_from_section(section)
                if section_name == 'ethics':
                    self._xml_text_ethics = self.get_text_from_section(section)
                if section_name == 'limitations':
                    self._xml_text_limitations = self.get_text_from_section(section)

                if section_name == 'unknown':
                    print('unknown section:')
                    print(section.tag)
                    print(ET.tostring(section))

    def get_section_name(self, section):
        print('get_section_name -------------', end = '')
        section_name = 'unknown'

        if 'role' in section.attrib:
            #print('role gefunden')
            if section.attrib['role'] == 'introduction':
                section_name = 'introduction'
            elif section.attrib['role'] == 'background':
                section_name = 'introduction'
            elif section.attrib['role'] == 'materials-methods':
                section_name = 'materials-methods'
            elif section.attrib['role'] == 'results':
                section_name = 'results'
            elif section.attrib['role'] == 'discussion':
                section_name = 'discussion'
            elif section.attrib['role'] == 'conclusion':
                section_name = 'conclusion'
            elif section.attrib['role'] == 'acknowledgement':
                section_name = 'unknown' #'acknowledgement1' # hier muessen noch die unterpunkte founding
            else:
                print('section role unknown: ')
                print(section.attrib['role'])
                print(ET.tostring(section))
            print('by role --->', end = '')
        if section_name=='unknown':
            # kein role attribut gefunden ... versuche es uber den Section Title
            idx = 0
            for section_title in section.iter('section-title'):
                idx = idx + 1


                print(f"section level = {idx}  Titel = {section_title.text} ", end = '')
                if section_title.text in self.__introduction_headline_names:
                    section_name = 'introduction'
                if section_title.text in self.__methods_headline_names:
                    section_name = 'materials-methods'
                if section_title.text in self.__results_headline_names:
                    section_name = 'results'
                if section_title.text in self.__discussion_headline_names:
                    section_name = 'discussion'
                if section_title.text in self.__conclusion_headline_names:
                    section_name = 'conclusion'
                if section_title.text in self.__contributions_headline_names:
                    section_name = 'author_contributions'
                if section_title.text in self.__funding_headline_names:
                    section_name = 'funding'
                if section_title.text in self.__interests_headline_names:
                    section_name = 'competing_interests'
                if section_title.text in self.__data_availability_headline_names:
                    section_name = 'availability_of_data_and_material'
                if section_title.text in self.__ethics_headline_names:
                    section_name = 'ethics'
                if section_title.text in self.__limitations_headline_names:
                    section_name = 'limitations'
                # wenn nach dem ersten Durchlauf noch keine Entscheidung
                if idx == 1 and section_name == 'unknown':
                    # wenn die letzte grosse ueberschrift introduction war dann
                    # ist jedes vorkommen des Worts results imperativ fuer die methods section
                    # diese sollte ohnehin nach methods
                    if self.__the_last_section == 'introduction':
                        if section_title.text.find('method') >= 0 or section_title.text.find('Method') >= 0:
                            section_name = 'materials-methods'
                if idx == 1 and section_name == 'unknown':
                    # wenn die letzte grosse ueberschrift introduction war dann
                    # ist jedes vorkommen des Worts results imperativ fuer die methods section
                    # diese sollte ohnehin nach methods
                    if self.__the_last_section == 'introduction' or self.__the_last_section == 'materials-methods':
                        if section_title.text.find('Result') >= 0 or section_title.text.find('result') >= 0:
                            section_name = 'results'

                if idx == 1 and section_name == 'unknown':
                    # wenn die letzte grosse ueberschrift introduction war dann
                    # ist jedes vorkommen des Worts results imperativ fuer die methods section
                    # diese sollte ohnehin nach methods
                    if self.__the_last_section == 'results':
                        if section_title.text.find('Discussion') >= 0 or section_title.text.find('discussion') >= 0:
                            section_name = 'discussion'

                if idx == 1 and section_name == 'unknown':
                    # wenn die letzte SEction die Introduction war und dann ordnen wir erneut der
                    # introduction zu da haeufig nochmal weitere subjections kommen
                    if self.__the_last_section == 'introduction':
                        if section_title.text != 'Experiment' and section_title.text != 'Experiments':
                            if len(re.findall(r"Experiment \d", section_title.text)) == 0:
                                section_name = 'introduction'

                if idx == 1 and section_name == 'unknown':
                    # wenn es das label 1 ist, dann muss es Introduction sein
                    if self.__the_last_section == 'no entry':
                        section_name = 'introduction'

                if section_name != 'unknown' or idx>=1:
                    break
                    # mit dem obigen Iter Befehl geht er alle subheadings durch
                    # das kann mit den Subheadings eine Zuordnung versucht werden
                    # das erscheint aber gefaehrlich

        if section_name == 'unknown':
            print('no section role found')
            print(ET.tostring(section))

        self.__the_last_section = section_name
        print('-----> ' + section_name)
        return section_name


    def get_text_from_section(self, section):
        new_text = ''
        for node in section.iter('para'):

            new_text = new_text + ' ' + node.text

            for ref in node:

                if ref.tag in self.dictOfSectionTagsToReplace:
                    new_text = new_text + self.dictOfSectionTagsToReplace[ref.tag] +ref.tail
                elif ref.tag in self.listOfSectionTagsToPassOver:
                    new_text = new_text + ref.tail
                elif ref.tag in self.listOfSectionTagsToTakeWith:
                    new_text = new_text + ref.text + ref.tail
                else:
                    print('unknown tag during text extraction:')
                    print(ref.tag)
                    print(ET.tostring(node))
        new_text = self.delete_artifacts(new_text)

        return new_text


    def get_text_from_acknowledgment(self, section):
        new_text = ''
        for node in section.iter('para'):
            if node.text is not None:
                new_text = new_text + node.text

                for ref in node:
                    if ref is not None:
                        if ref.text is not None and ref.tail is not None:
                            new_text = new_text + ref.text + ref.tail
        return new_text


    def get_table_text(self, node):
        for tablenode in node.iter():
            if tablenode.tag.find('simple') >= 0:
                #print(tablenode.text)
                self._xml_text_table.append(tablenode.text)

    def get_figure_text(self, node):
        for figurenode in node.iter():
            if figurenode.tag.find('simple') >= 0:
                self._xml_text_figure.append(figurenode.text)


    def delete_namespaces(self, root):
        for c in root.iter():
            if '}' in c.tag:
                c.tag = c.tag.split('}', 1)[1]
        return root

    def delete_artifacts(self, text):
        text = re.sub(' +', ' ', text)
#        text = text.replace('\t','')
#        text = text.replace('                  ','')
        text = re.sub(r"\s+"," ",text)
        return text

    def development_test(self):
        #tree = ET.parse(self._xml)
        root = ET.fromstring(self._xml)
        for child in root:
            child = self.delete_namespaces(child)
            if child.tag.find('coredata') >= 0:
                self.analyse_coredata(child)
                #print('analyse coredata about here')
            if child.tag.find('objects') >= 0:
                self.analyse_objects(child)
            if child.tag.find('scopus-id') >= 0:
                self.analyse_scopus_id(child)
            if child.tag.find('scopus-eid') >= 0:
                self.analyse_scopus_eid(child)
            if child.tag.find('pubmed-id') >= 0:
                self.analyse_pubmed_id(child)
            if child.tag.find('link') >= 0:
                self.analyse_link(child)
            if child.tag.find('originalText') >= 0:
                self.analyse_originalText(child)
            #print(child.tag, child.attrib)
            #print(child.text)
            if self._item_weight == 'HEAD-AND-TAIL':
                print('only HEAD-AND-TAIL paper ')

    def analyse_parsing(self):
        #print('analysing quality of parsing of file:')
        filename = self._doi
        filename = filename.replace(" ", "_")
        filename = filename.replace("/", "_")
        filename = filename.replace(".", "_")
        filename = filename + '.xml'
        exceptx = 0
        #print(filename)
        if self._item_weight!= "FULL-TEXT":
            print(self._item_weight)

        if len(self._title)<4:
            print("no titel found")
            exceptx = exceptx + 1
        if len(self._abstract)<4:
            print("no Abstract found")
            exceptx = exceptx + 1
        if len(self._xml_text_introduction)<4:
            print("no Introduction found")
            exceptx = exceptx + 1
        if len(self._xml_text_methods)<4:
            print("no Methods found")
            exceptx = exceptx + 1
        if len(self._xml_text_results)<4:
            print("no Results found")
            exceptx = exceptx + 1
        if len(self._xml_text_discussion) < 4:
            print("no Discussion found")
            exceptx = exceptx + 1

        if exceptx == 0:
            print("parsing without problems")

    def output_text(self):
        # print('ABSTRACT')
        # print(self._abstract)
        #self.prints()
        #print('INTRODUCTION')
        #print(self._xml_text_introduction)
        # print('METHODS')
        # print(self._xml_text_methods)
        # print('RESULTS')
        # print(self._xml_text_results)
        # print('DISCUSSION')
        # print(self._xml_text_discussion)
        # print('CONCLUSION')
        # print(self._xml_text_conclusion)
        # print('ACKNOWLEDGMENT')
        # print(self._xml_text_acknowledgment)
        with open('./tmp.txt','w+', encoding = 'utf-8') as f:
            f.write(self._title)
            f.write('\n\nABSTRACT\n')
            f.write(self._abstract)
            f.write('\n\nINTRODUCTION\n')
            f.write(self._xml_text_introduction)
            f.write("\n\nMETHODS\n")
            f.write(self._xml_text_methods)
            f.write('\n\nRESULTS\n')
            f.write(self._xml_text_results)
            f.write('\n\nDISCUSSION\n')
            f.write(self._xml_text_discussion)
            f.write('\n\nCONCLUSION\n')
            f.write(self._xml_text_conclusion)
            #print(self._xml_text_conclusion)
            f.write('\n\nACKNOWLEDGMENT\n')
            f.write(self._xml_text_acknowledgment)

        #print('now saving as json file')

    def get_whole_text(self):
        text = ''
        text = text + '\n\nAbstract\n'
        text = text + self._abstract
        text = text + '\n\nINTRODUCTION\n'
        text = text + self._xml_text_introduction
        text = text + "\n\nMETHODS\n"
        text = text + self._xml_text_methods
        text = text + '\n\nRESULTS\n'
        text = text + self._xml_text_results
        text = text + '\n\nDISCUSSION\n'
        text = text + self._xml_text_discussion
        text = text + '\n\nCONCLUSION\n'
        text = text + self._xml_text_conclusion
        text = text + '\n\nACKNOWLEDGMENT\n'
        text = text + self._xml_text_acknowledgment
        return text

    def get_part_of_text(self, textpart):
        if textpart == 'abstract':
            return self._abstract
        if textpart == 'introduction':
            print('nun der Text in der Class research_paper_xmljson')
            print(self._xml_text_introduction)
            return self._xml_text_introduction

        if textpart == 'methods':
            return self._xml_text_methods
        if textpart == 'results':
            return self._xml_text_results
        if textpart == 'discussion':
            return self._xml_text_discussion
        if textpart == 'conclusion':
            return self._xml_text_conclusion
        if textpart == 'acknowledgment':
            return self._xml_text_acknowledgment
        print("ERROR in  get_part_of_text as no section with the given name is available")

    def save_as_json(self, mypath):
        data = {"title": self._title,
            "url" : self._url,
            "pii" : self._pii,
            "doi" :self._doi,
            "publicationName": self._publicationName,
            "aggregationType" :self._aggregationType,
            "format" : self._format ,
            "issn" : self._issn ,
            "volume" : self._volume ,
            "identifier" : self._identifier ,
            "eid" : self._eid ,
            "publisher" : self._publisher ,
            "Authors_name" : self._Authors_name,
            "openaccess" : self._openaccess ,
            "openaccessType" : self._openaccessType ,
            "openaccessArticle" : self._openaccessArticle ,
            "openArchiveArticle" : self._openArchiveArticle ,
            "openaccessSponsorName" : self._openaccessSponsorName ,
            "openaccessSponsorType" : self._openaccessSponsorType ,
            "openaccessUserLicense" : self._openaccessUserLicense ,
            "subject" : self._subject ,
            "link_api" : self._link_api ,
            "link_scidir" : self._link_scidir ,
            "abstract" : self._abstract ,
            "scopus_id" : self._scopus_id ,
            "scopus_eid" : self._scopus_eid ,
            "pubmed_id" : self._pubmed_id ,
            "year" : self._year ,
            "xml_text_figure" : self._xml_text_figure ,
            "xml_text_table" : self._xml_text_table ,
            "xml_text_abstract" : self._xml_text_abstract ,
            "xml_text_abstract_structured" : self._xml_text_abstract_structured ,
            "xml_text_introduction" : self._xml_text_introduction ,
            "xml_text_methods" : self._xml_text_methods ,
            "xml_text_results" : self._xml_text_results ,
            "xml_text_discussion" : self._xml_text_discussion ,
            "xml_text_conclusion" : self._xml_text_conclusion ,
            "xml_text_acknowledgment" : self._xml_text_acknowledgment ,
            "xml_text_author_contributions" : self._xml_text_author_contributions ,
            "xml_text_funding" : self._xml_text_funding ,
            "xml_text_competing_interests" : self._xml_text_competing_interests ,
            "xml_text_availability_of_data_and_material" : self._xml_text_availability_of_data_and_material ,
            "dictOfSectionTagsToReplace" : self.dictOfSectionTagsToReplace,
            "listOfSectionTagsToPassOver" : self.listOfSectionTagsToPassOver,
            "listOfSectionTagsToTakeWith" : self.listOfSectionTagsToTakeWith
        }
        data = json.dumps(data)
        filename = mypath + self._publicationName + self._doi

        filename = filename.replace(" ", "_")
        filename = filename.replace("/", "_")
        filename = filename.replace(".", "_")
        filename = filename + '.json'

        with open(filename, 'w', encoding='utf8') as json_file:
            json.dump(data, json_file)

# if section_title.text.find('Introduction')>= 0:
#     section_name = 'introduction'
# if section_title.text.find('Background')>= 0:
#     section_name = 'introduction'
# if section_title.text.find('Theory')>= 0:
#     section_name = 'introduction'
# if section_title.text.find('Methods')>= 0:
#     section_name = 'materials-methods'
# if section_title.text == 'Method':
#     section_name = 'materials-methods'
# if section_title.text == 'Patients and methods':
#     section_name = 'materials-methods'
# if section_title.text.find('Data analysis.')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Materials and methods')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Material and methods')>= 0:
#     section_name = 'materials-methods'
# if section_title.text == 'Materials':
#     section_name = 'materials-methods'
# if section_title.text == 'Methodology':
#     section_name = 'materials-methods'
# if section_title.text.find('Experimental setup')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('General method')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Statistics')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Materials and experiments')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Data description')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Experiment')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Experiments')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Experiment 1')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Experiment 2')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Experiment 3')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Experiment 4')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Datasets')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Experimental methods')>= 0:
#     section_name = 'materials-methods'
# if section_title.text.find('Results')>= 0:
#     section_name = 'results'
# if section_title.text.find('Result') >= 0:
#     section_name = 'results'
# if section_title.text.find('Experimental results') >= 0:
#     section_name = 'results'
# if section_title.text.find('Discussion')>= 0:
#     section_name = 'discussion'
# if section_title.text.find('General discussion')>= 0:
#     section_name = 'discussion'
# if section_title.text.find('Overall discussion')>= 0:
#     section_name = 'discussion'
# if section_title.text.find('Experimental results and discussion')>= 0:
#     section_name = 'discussion'
# if section_title.text.find('Conclusions')>= 0:
#     section_name = 'conclusion'
# if section_title.text.find('Conclusion')>= 0:
#     section_name = 'conclusion'
# if section_title.text.find('Concluding remarks')>= 0:
#     section_name = 'conclusion'
# if section_title.text.find('Concluding comments')>= 0:
#     section_name = 'conclusion'
# if section_title.text.find('Summary')>= 0:
#     section_name = 'conclusion'
# if section_title.text.find('Contributions')>= 0:
#     section_name = 'author_contributions'
# if section_title.text.find('Author contributions')>= 0:
#     section_name = 'author_contributions'
# if section_title.text.find('Author contributions')>= 0:
#     section_name = 'author_contributions'
# if section_title.text.find('Author contribution')>= 0:
#     section_name = 'author_contributions'
# if section_title.text.find('Funding')>= 0:
#     section_name = 'funding'
# if section_title.text.find('Competing interests')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Competing financial interests')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Declaration of conflicting interests')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Potential conflicts of interest')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Conflicts of interest')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Conflict of interest')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Conflict of Interest')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Conflicts of Interest')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Declarations of interest')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Disclosure statement')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Disclosure')>= 0:
#     section_name = 'competing_interests'
# if section_title.text.find('Availability of data and material')>= 0:
#     section_name = 'availability_of_data_and_material'
# if section_title.text.find('ethical standards')>= 0:
#     section_name = 'ethics'
# if section_title.text.find('Ethical standards')>= 0:
#     section_name = 'ethics'
# if section_title.text.find('Limitations')>= 0:
#     section_name = 'limitations'
#
















 

