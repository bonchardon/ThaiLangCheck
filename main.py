# TODO: apply and test some tokenization approaches that could be applied when working with Thai language
#  think of editing approaches when working with Thai, as well
from xml.etree import ElementTree as ET

import pythaispell
import sentencepiece
# import pythaipiece

import pythainlp
from pythainlp import sent_tokenize, word_tokenize
from pythainlp.tokenize.multi_cut import find_all_segment, mmcut, segment
from pythainlp.util import normalize
# for spell checking
from pythainlp.spell import NorvigSpellChecker
from pythainlp.corpus import ttc
import pythainlp.word_vector
from pythainlp.corpus.common import thai_words
from pythainlp import Tokenizer
from pythainlp import spell, correct
from pythainlp import correct
from pythainlp.tokenize import subword_tokenize

import tltk
from wordcut import Wordcut
from nlpo3 import segment as seg_nlpo3
from nlpo3 import load_dict

import deepcut
import jpype
import os
import pandas as pd
from py4j.java_gateway import JavaGateway
gateway = JavaGateway()
# from cutkum.tokenizer import Cutkum


class LexTo(object):
    def __init__(self):
        filePath = os.path.abspath(os.path.dirname(__file__))
        jpype.startJVM(jpype.getDefaultJVMPath(), '-ea', '-Djava.class.path=%s/LongLexTo' % (filePath))

        LongLexTo = jpype.JClass("LongLexTo")
        self.lexto = LongLexTo('%s/lexitron.txt' % (filePath))
        self.typeString = {}
        self.typeString[0] = "unknown"
        self.typeString[1] = "known"
        self.typeString[2] = "ambiguous"
        self.typeString[3] = "English/Digits"
        self.typeString[4] = "special"

    def tokenize(self, line):
        line = line.strip()

        self.lexto.wordInstance(line)
        typeList = self.lexto.getTypeList()
        typeList = [self.typeString[n.value] for n in typeList]

        wordList = []
        begin = self.lexto.first()
        while self.lexto.hasNext():
            end = self.lexto.next()
            wordList.append(line[begin:end])
            begin = end

        return wordList, typeList


class Tokenization:

    # here are various thai libraries used to analyze thai
    # (what actually interests us --> tokenization of a text with mistakes and typos)

    # TODO: here we try out all the possible ways to tokenize thai text

    def pythainlp_try(self, data):
        # Default word tokenizer use a word list from pythainlp.corpus.common.thai_words()
        words = set(thai_words())
        custom_tokenizer = Tokenizer(words)
        return find_all_segment(data), \
               word_tokenize(data, keep_whitespace=False), \
               custom_tokenizer.word_tokenize(data)

    def wordcutThai(self, data):
        wordcut = Wordcut.bigthai()
        return wordcut.tokenize(data)

    def ThaiNltk(self, data):
        return tltk.corpus.collocates(data)

    def Thaideepcut(self, data):
        return deepcut.tokenize(data)

    def Thainlpo3(self, data):

        # here we can also load additional dictionaries and use those in segmentation process
        # to make it more profound
        return seg_nlpo3(data)

    def cutkum_tokenizer(self, data):
        " REMEMBER: cutkum works just fine, but unfortunately cutkum requires old versions of tensorflow \
                    (tensorflow1.x) installed:\
                    it puts tensorflow.contrib error if that a new version of tensorflow.\
                    Other thai libraries require tensorflow2.x versions."
        ck = Cutkum()
        return ck.tokenize(data)


class SpellingCheck:

    # TODO: here trying possible ways to check spelling without prior tokenization

    # def __init__(self, data):
    #     super().__init__(data)

    def spell_checker(self, data):

        checker = NorvigSpellChecker(custom_dict=ttc.word_freqs())
        return checker.correct(data)


class FastT:

    # TODO: accomplish my idea on how to use fastText embedding technique to work with Thai text
    #  (and accomplish tokenization task)

    def __init__(self):
        pass

    def fastext(self):
        pass


if __name__ == '__main__':

    path = "C:\/Users\Марина\Desktop\/trwiki-20181001-corpus.xml"
    # path = False
    if path:
        tree = ET.parse(path)
        root = tree.getroot()

        for page in root.findall('page'):
            print(page.find('content').text)

    train_data = "ข้อ 1 มนุษย์ทั้งหลายเกิดมามีอิสระและเสมอภาคกันในเกียรติศักด[เกียรติศักดิ์]และสิทธิ ต่างมีเหตุผลและมโนธรรม และควรปฏิบัติต่อกันด้วยเจตนารมณ์แห่งภราดรภาพ"
    data = "ผมลััักของนะผมลักของนะ"
    # when applied typos are deleted
    # data = normalize(data)

    separateWords = Tokenization()
    spelling = SpellingCheck()
    # TODO: check issue "jpype._jvmfinder.JVMNotFoundException: No JVM shared library file (jvm.dll) found.
    #  Try setting up the JAVA_HOME environment variable properly."
    # lexto = LexTo()
    # words, types = lexto.tokenize(data)
    # print("Lexto progect check ==> ", words, types)

    # just a dataframe with all initial result

    all, reg, cus = separateWords.pythainlp_try(data)

    df = pd.DataFrame()
    df['Possible segmentations using pythainlp'] = all
    df['Regular pythainlp library'] = ['|'.join(reg)]
    df['Custom pythainlp library'] = ['|'.join(cus)]
    df['Deepcut library'] = '|'.join(separateWords.Thaideepcut(data=data))
    print(df.T)
