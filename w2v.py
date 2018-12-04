from gensim.models import KeyedVectors
from translate import Translator

trad = Translator(from_lang='fr', to_lang="en")

model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
#model.wv.save_word2vecformat('googlenews.txt')

condSortie = 1

while condSortie != 0:
    myInput = input("Entrez le mot à trouver : ")

    word = trad.translate(myInput)
    print('# of words', len(model.wv.vocab))
    print('sample words', list(model.wv.vocab.keys())[:10])

    # all the vocabulary is in this format : STD + word (for regular tags) COMPANY + word, INDUSTRY + word

    print(f'most similar words to {word} :\n{model.most_similar(word)}')
    # print(f'vector of word :\n{model[word]}')
    condSortie = input("Sortir ? :")
