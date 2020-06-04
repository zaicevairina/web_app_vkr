#-*-coding: utf-*-
from itertools import combinations
from nltk.tokenize import sent_tokenize, RegexpTokenizer
from nltk.stem.snowball import RussianStemmer
import networkx as nx
from sklearn.feature_extraction.text import CountVectorizer
import math
import re
import nltk
# nltk.download('stopwords')


def treatment_text(text):
    text = re.sub("[^а-яА-Яa-zЁёA-Z0-9,.?]", " ", str(text))
    text = text.replace('\t',' ')
    text = text.replace('\n', ' ')
    while text.find('  ')!=-1:
        text = text.replace('  ',' ')
    text = str(text)
    return text

class TextRank():
    
    def __init__(self):
        self.pattern = "(?u)\\b[\\w-]+\\b"
    
            
    def similarity_1(self,s1, s2):
        if not len(s1) or not len(s2):
            return 0.0
        return len(s1.intersection(s2))/(1.0 * (len(s1) + len(s2)))
    def similarity_2(self,s1,s2):
        s1 = list(s1)
        s2 = list(s2)
        s1 = ' '.join(map(str,s1))
        s2 = ' '.join(map(str,s2))
        vectorizer = CountVectorizer()

        x = vectorizer.fit_transform([s1, s2])
        s1_v = vectorizer.transform([s1])
        s2_v = vectorizer.transform([s2])
        s1 = s1_v.toarray()[0]
        s2 = s2_v.toarray()[0]

        sum = 0
        kv1 = 0
        kv2 = 0

        for i in range(s1.shape[0]):
            sum += s1[i] * s2[i]
            kv1 += s1[i] * s1[i]
            kv2 += s2[i] * s2[i]
        kv2 = math.sqrt(kv2) + 1e-8
        kv1 = math.sqrt(kv1) + 1e-8
        return sum / (kv1 * kv2)
    
    
    def textrank(self,text,similar='serense'):
        text = treatment_text(text)
        text = text.split('.')
        text = list(filter(lambda x: len(x.split()) > 6, text))
        text = '.'.join(text)

        sentences = sent_tokenize(text)
        tokenizer = RegexpTokenizer(r'\w+')
        lmtzr = RussianStemmer()
        words = [set(lmtzr.stem(word) for word in tokenizer.tokenize(sentence.lower()))
                 for sentence in sentences]
    
        pairs = combinations(range(len(sentences)), 2)
        if similar == 'serense':
            scores = [(i, j, self.similarity_1(words[i], words[j])) for i, j in pairs]
        if similar == 'cos':
            scores = [(i, j, self.similarity_2(words[i], words[j])) for i, j in pairs]
    
    
        scores = filter(lambda x: x[2], scores)
    
        g = nx.Graph()
        g.add_weighted_edges_from(scores)
        pr = nx.pagerank(g)
    
        return sorted(((i, pr[i], s) for i, s in enumerate(sentences) if i in pr),
                      key=lambda x: pr[x[0]], reverse=True)
    
    def extract(self,text,mera='serense',n=5):

        tr = self.textrank(text,similar=mera)
        top_n = sorted(tr[:n])
        x = ' '.join(x[2] for x in top_n)
        if x!='':
            return x
        else:
            return 'Слишком маленький текст (минимум 5 предложений)'


