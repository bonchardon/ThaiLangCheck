# TODO: apply and test some tokenization approaches that could be applied when working with Thai language
#  think of editing approaches when working with Thai, as well

import pythainlp
from pythainlp import sent_tokenize, word_tokenize
from pythainlp.corpus.common import thai_words
from pythainlp.tokenize.multi_cut import find_all_segment, mmcut, segment
from pythainlp import Tokenizer
from pythainlp.tokenize.multi_cut import find_all_segment, mmcut, segment
from pythainlp.util import normalize
from pythainlp import correct
# for spell checking
from pythainlp.spell import NorvigSpellChecker
from pythainlp.corpus import ttc


import tltk
from wordcut import Wordcut
from nlpo3 import load_dict, segment
import deepcut
import jpype
import os
from py4j.java_gateway import JavaGateway
gateway = JavaGateway()
# from cutkum.tokenizer import Cutkum


class Tokenization:

    def __init__(self, data):

        # normalize helps us to ensure there are no typos or other minor issues in text
        # correct helps to correct spelling, it returns most likely spelling

        self.dataa = normalize(data)
        self.data = correct(self.dataa)

    # TODO: here we try out all the possible ways to tokenize thai text

    def pythainlp_try(self, data):

        regular_tokenizer = word_tokenize(data, keep_whitespace=False)

        words = set(thai_words())
        custom_tokenizer = Tokenizer(words)
        print("All possible segmentations using pythainlp ==> ", find_all_segment(data))
        return "Regular pythainlp library check ==> ", regular_tokenizer, "Custom pythainlp library check ==> ", custom_tokenizer.word_tokenize(data)

    def wordcutThai(self, data, input):
        wordcut = Wordcut(data)
        return wordcut.tokenize(input)

    def ThaiNltk(self, data):
        return tltk.corpus.collocates(data)

    def Thaideepcut(self, data):
        return deepcut.tokenize(data)

    def Thainlpo3(self, data):

        # here we can also load additional dictionaries and use those in segmentation process
        # to make it more profound

        return segment(data, "countries")

    def cutkum_tokenizer(self, data):
        " REMEMBER: cutkum works just fine, but unfortunately cutkum requires old versions of tensorflow \
                    (tensorflow1.x) installed:\
                    it puts tensorflow.contrib error if that a new version of tensorflow.\
                    Other thai libraries require tensorflow2.x versions."
        ck = Cutkum()
        return ck.tokenize(data)


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


class SpellingCheck():

    # TODO: here trying possible ways to check spelling without prior tokenization

    # def __init__(self, data):
    #     super().__init__(data)

    def normalize(self, data):
        return normalize(data)

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

    train_data = "ข้อ 1 มนุษย์ทั้งหลายเกิดมามีอิสระและเสมอภาคกันในเกียรติศักด[เกียรติศักดิ์]และสิทธิ ต่างมีเหตุผลและมโนธรรม และควรปฏิบัติต่อกันด้วยเจตนารมณ์แห่งภราดรภาพ"
    data = "สบายดีไหมเเหลืยม"
    # data = data.encode(encoding='UTF-8')

    separateWords = Tokenization(data)
    spelling = SpellingCheck()

    # TODO: check issue "jpype._jvmfinder.JVMNotFoundException: No JVM shared library file (jvm.dll) found. Try setting up the JAVA_HOME environment variable properly."
    # lexto = LexTo()
    # words, types = lexto.tokenize(data)
    # print("Lexto progect check ==> ", words, types)

    print(separateWords.pythainlp_try(data))
    print("WordcutThai library check ==> ", separateWords.wordcutThai(data=train_data, input=data))
    print("Deepcut library check ==> ", separateWords.Thaideepcut(data=data))
    # print("nlpo3 library check ==> ", separateWords.Thainlpo3(data=data))
    # print(separateWords.cutkum_tokenizer(data=data))

    print("Spell checking using pythainlp ==> ", spelling.spell_checker(data=data))
