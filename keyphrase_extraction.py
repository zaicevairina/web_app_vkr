from nltk.stem.snowball import SnowballStemmer
import csv
import re
import pymorphy2
from nltk.stem.porter import *
import pickle
from rake import RAKE
from env import stops
from deeppavlov.dataset_readers.basic_classification_reader import BasicClassificationDatasetReader
from deeppavlov.dataset_iterators.basic_classification_iterator import BasicClassificationDatasetIterator
from deeppavlov.dataset_iterators.basic_classification_iterator import BasicClassificationDatasetIterator
from deeppavlov.models.preprocessors.str_lower import str_lower
from deeppavlov.models.tokenizers.nltk_moses_tokenizer import NLTKMosesTokenizer
from deeppavlov.core.data.simple_vocab import SimpleVocabulary
from deeppavlov.models.sklearn import SklearnComponent
from deeppavlov.metrics.accuracy import sets_accuracy
import numpy as np



morph=pymorphy2.MorphAnalyzer()
stemmer=SnowballStemmer('russian')
r = RAKE()

dict_stop=set(['метод','определение','условие','момент','значение','результат','критерий',
               'работа','вариант','брянский государственный университет','научнотехнический вестник',
              'соответствие','такой образ','весь критерий','пример','выбор','ключевое слово','период',
              'уравнение','формула','множитель','повышение','оценка','проведение',
              'машина','нагрузка','брянская область','точка','случай','расчет','таблица','расчёт',
              'с показатель','град','обработка','статья','элемент','раз','применение','центр','форма','важная задача'])


with open('cls_model.pickle', 'rb') as f:
    cls = pickle.load(f)

with open('tf_idf_model.pickle', 'rb') as f:
    tfidf = pickle.load(f)

def treatment_text2(text):
    text = re.sub("[^а-яА-Яa-zA-Z0-9,.?]", " ", str(text))
    text = text.replace('\t',' ')
    text = text.replace('\n', ' ')
    while text.find('  ')!=-1:
        text = text.replace('  ',' ')
    text = str(text)
    return text

def treatment_text(review):
    review_text = re.sub("[^а-яА-ЯЁёa-zA-Z0-9]", " ", review)
    review_text = review_text.replace('ё','е')
    review_text = review_text.replace('Ё', 'Е')
    words = review_text.lower().split()
    words = [w for w in words if not w in stops]
    words = [morph.parse(w)[0].normal_form for w in words]
    words = [stemmer.stem(w) for w in words]
    words = [w for w in words if not w in stops]
    return(words)


def normalize(keyphrase):
    try:
        words = keyphrase.split()
        if len(words)>1:
            main_noun = words[-1]
            flag_noun = False
            flag_adj = False
            for i in words[:-1]:
                if 'NOUN' not in  morph.parse(i)[0].tag and 'ADJF' not in morph.parse(i)[0].tag:
                    return morph.parse(words[0])[0].lexeme[0][0] + ','+morph.parse(words[2])[0].lexeme[0][0]
                if 'NOUN' in morph.parse(i)[0].tag:
                    flag_noun=True
                if 'ADJF' in morph.parse(i)[0].tag:
                    flag_adj=True
            s = ''

            if flag_noun is False:
                for word in words[:-1]:
                    for i in morph.parse(word)[0].lexeme:
                        if morph.parse(main_noun)[0].tag.gender in i.tag and 'nomn' in i.tag:

                            s+=i.word + ' '
                            break
                return s + morph.parse(main_noun)[0].lexeme[0][0]

            elif flag_noun is True and flag_adj is False:
                s = morph.parse(words[0])[0].lexeme[0][0]
                for i in words[1:]:
                    try:
                        s+= ' '+morph.parse(i)[0].lexeme[1][0]
                    except:
                        pass
                return s

            else:
                flag_first_noun=False

                for word in words:
                    if 'ADJF' in  morph.parse(word)[0].tag and flag_first_noun is False:
                        rod = find_rod(words[words.index(word)+1:])
                        for i in morph.parse(word)[0].lexeme:
                            if rod in i.tag and 'nomn' in i.tag:

                                s+=i.word + ' '
                                break
                    elif 'ADJF' in  morph.parse(word)[0].tag and flag_first_noun is True:
                        rod = find_rod(words[words.index(word)+1:])
                        for i in morph.parse(word)[0].lexeme:
                            if rod in i.tag and 'gent' in i.tag:
                                s+=i.word + ' '
                                break
                    elif  'NOUN' in  morph.parse(word)[0].tag and flag_first_noun is False:
                        flag_first_noun=True

                        s += morph.parse(word)[0].lexeme[0][0] + ' '
                    else:

                        s += morph.parse(word)[0].lexeme[2][0] +' '


            return s
        elif len(words)==1:
            return morph.parse(words[0])[0].lexeme[0][0]
    except:
        pass
#         print(' '.join(words),'НЕ МОЖЕТ БЫТЬ ПРЕОБРАЗОВАН')

def find_rod(words):
    for w in words:
        if 'NOUN' in morph.parse(w)[0].tag:
            return morph.parse(w)[0].tag.gender


def find_adj(sentence, index_noun, pred_noun):
    if pred_noun == 0 and index_noun == 0:
        return 0
    if pred_noun == 0 and index_noun != 0:
        i = index_noun - 1
        flag_ad = False
        flag_noun = False
        while i >= 0:
            if 'ADJF' in morph.parse(sentence[i])[0].tag:
                flag_ad = True
            elif 'NOUN' in morph.parse(sentence[i])[0].tag:
                flag_noun = True
            elif flag_ad is False and flag_noun is False:
                return i + 1

            flag_ad = False
            flag_noun = False
            i -= 1
        return i + 1

    else:
        i = index_noun - 1
        flag_ad = False
        flag_noun = False
        while i > pred_noun:
            if 'ADJF' in morph.parse(sentence[i])[0].tag:
                flag_ad = True
            elif 'NOUN' in morph.parse(sentence[i])[0].tag:
                flag_noun = True
            elif flag_ad is False and flag_noun is False:
                return i + 1

            flag_ad = False
            flag_noun = False
            i -= 1
        return i + 1


def keyword_extraction(text):
    sentences_origin = text.split('.')
    sentences_tr = list(map(treatment_text, sentences_origin))
    test=[]
    for sentence_tr, sentence_or in zip(sentences_tr, sentences_origin):
        # sentence_tr_set = set(sentence_tr)
        # if len(sentence_tr) > 5 and kws_tr_set.intersection(sentence_tr_set):
        #     test.append((sentence_or, ' '.join(sentence_tr)))
        if len(sentence_tr) > 5:
            test.append((sentence_or, ' '.join(sentence_tr)))
    x_test = []
    for s in test:
        x_test.append(s[1])
    x_test = tuple(x_test)
    y_pred = cls(tfidf(x_test))
    sentences_with_kw = []
    for i in range(len(y_pred)):
        if y_pred[i] == '1':
            sentences_with_kw.append(test[i])
    dict_cand = {}
    for sentence in sentences_with_kw:
        cand = extract_candidate(sentence[0])
        cand = list(map(normalize, cand))
        for key_cand in cand:
            if key_cand in dict_cand:
                dict_cand[key_cand] += 1
            else:
                dict_cand[key_cand] = 1
    dict_cand_sort = {k: v for k, v in sorted(dict_cand.items(), key=lambda item: item[1], reverse=True)}
    result = []
    count = 0
    k = set(['1', '2', '3', '4', '5', '&', '?', '/', '\\', '!'])

    for word in dict_cand_sort.keys():
        try:
            if count < 15:
                if ',' in word:
                    word = word.split()
                    result += word
                elif k.intersection(set(word)) == set() and word not in dict_stop and 'ADJF' not in morph.parse(word)[
                    0].tag:
                    result.append(word)
                    count += 1
            else:
                break
        except:
            pass
    for i in result:

        flag = False
        s = i.replace(',', ' ')
        s = s.split(' ')
        for j in s:
            if 'NOUN' in morph.parse(j)[0].tag:
                flag = True
        if flag is False:
            result.remove(i)
    result = list(map(lambda x: x.replace(',', ' '), result))
    result = ', '.join(result)
    if result!='' :
        return result
    else:
        keywords = r.keywords_extract(text)
        keywords = ', '.join(keywords).capitalize()
        return keywords

def extract_candidate(origin):
    candidate = []
    x = re.sub("[^а-яА-Я]", " ", origin)
    while x.find('  ') != -1:
        x = x.replace('  ', ' ')
    x = x.split()
    x = list(filter(lambda x: len(x) > 2, x))
    pr = 0

    for i in range(len(x) - 1):
        if 'NOUN' in morph.parse(x[i])[0].tag and 'NOUN' in morph.parse(x[i + 1])[0].tag and i + 2 != len(x):
            pass
        elif 'NOUN' in morph.parse(x[i])[0].tag and 'NOUN' in morph.parse(x[i + 1])[0].tag and i + 2 == len(x):
            try:
                k = find_adj(x, i + 2, pr)
                pr = i
                if ' '.join(x[k:i + 1]) in sentences_with_kw[2][0]:
                    candidate.append(' '.join(x[k:i + 2]))
                else:
                    begin = origin.find(x[k])
                    end = origin.find(x[i + 1]) + len(x[i + 1])
                    candidate += origin[begin:end].split(',')
            except:
                pass
        elif 'NOUN' in morph.parse(x[i])[0].tag and 'NOUN' not in morph.parse(x[i + 1])[0].tag:

            k = find_adj(x, i, pr)
            pr = i

            if ' '.join(x[k:i + 1]) in origin:
                candidate.append((' '.join(x[k:i + 1])))
            else:
                begin = origin.find(x[k], len(' '.join(x[:k])))
                end = origin.find(x[i], len(' '.join(x[:i]))) + len(x[i])
                candidate += origin[begin:end].split(',')
    return candidate