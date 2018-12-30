from pandas import DataFrame
from numpy import hstack
from yandex import Translater
from collections import defaultdict
from os import makedirs, path
from pymorphy2 import MorphAnalyzer
from optparse import OptionParser


COL1 = 'word1'
COL2 = 'word2'
BENCHMARKS_DIR = 'word-benchmarks'
SIMILARITY_DIR = 'word-similarity'


class Lemmatizer():
    def __init__(self, lang='ru'):
        self.lang = lang
        if self.lang == 'ru':
            self.lemmatizer = MorphAnalyzer()

    def lemmatize(self, word):
        if self.lang == 'ru':
            return self.lemmatizer.parse(word)[0].normal_form


def set_translator(api_key, src_lang='en', trg_lang='ru'):
    translator = Translater()
    translator.set_key(api_key)
    translator.set_from_lang(src_lang)
    translator.set_to_lang(trg_lang)
    return translator


def translate(text, translator):
    translator.set_text(text)
    return translator.translate()


def make_translated_dataset(df, words_src, words_trg, *columns):
    for word_src, word_trg in zip(words_src, words_trg):
        for col in columns:
            df[col].replace(word_src, word_trg, inplace=True)
    return df


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-a', '--api', action='store', dest='api_key')
    parser.add_option('-s', '--src', action='store', dest='src', default='en')
    parser.add_option('-t', '--trg', action='store', dest='trg', default='ru')
    options, args = parser.parse_args()

    translator = set_translator(options.api_key)
    lemmatizer = Lemmatizer(options.trg)

    name = 'mc-30'
    df = DataFrame.from_csv(path.join('{}.csv'.format(name)))
    words_src = list(set(hstack((df[COL1].values, df[COL2].values))))
    words_trg = [lemmatizer.lemmatize(translate(word, translator)) for word in words_src]

    while(True):
        try:
            make_translated_dataset(df.copy(), words_src, words_trg, COL1).to_csv(path.join(options.trg, '{}.csv'.format(name)))
            break
        except FileNotFoundError:
            makedirs(options.trg)
