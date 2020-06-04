from rake_nltk import Rake, Metric
from nltk.corpus import stopwords
import re

stops = set(stopwords.words("english")) | set(stopwords.words("russian"))

for i in ['результат','др','место','небходимость','рисунок','вывод','метр','фанат','осторожность','контент','таблица','схема']:
    stops.add(i)
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

from natasha import NamesExtractor
from natasha.markup import show_markup, show_json

def def_names(text):
    extractor = NamesExtractor()

    matches = extractor(text)
    facts = [_.fact.as_json for _ in matches]

    names = []
    for i in range(len(facts)):
        if 'first' in facts[i]:
            x = facts[i]['first'].lower()
            names.append(x)
        if 'middle' in facts[i]:
            x = facts[i]['middle'].lower()
            names.append(x)
        if 'last' in facts[i]:
            x = facts[i]['last'].lower()
            names.append(x)
    return names


class RAKE():

    def keywords_extract(self,text):
        names = def_names(text)
        for i in names:
            text.replace(i, '')
        # разделяем текст на токены и приводим к нижнему регистру
        tokenized_text = text.lower()
        # убираем все лишник символы
        tokenized_text = re.sub("[^а-яА-Яa-zA-Z.?!]", " ", tokenized_text)

        tokenized_text=tokenized_text.split()

        # остаяляем как потенциальные КС только сущ и прил т е в список стоп слов добавляем все остальное
        for i in tokenized_text:
            if 'NOUN' not in morph.parse(i)[0].tag and 'ADJF' not in morph.parse(i)[0].tag:
                stops.add(i)
        # print(tokenized_text)
        tokenized_text = ' '.join(tokenized_text)
        r = Rake(ranking_metric=Metric.WORD_FREQUENCY, stopwords=stops, max_length=1)
        # extract keywords from text
        r.extract_keywords_from_text(tokenized_text)

        for i in r.get_ranked_phrases():
            if 'NOUN' not in morph.parse(i)[0].tag and 'ADJF' not in morph.parse(i)[0].tag:
                del i

        keywords = r.get_ranked_phrases()[:20]

        words = [morph.parse(w)[0].normal_form for w in keywords]
        result = set()
        for i in words:
            if 'NOUN' in morph.parse(i)[0].tag and len(i) > 1:
                result.add(i)
        return result

