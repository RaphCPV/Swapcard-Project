import pickle
import string
import nltk
import time
import pandas as pd
import pymysql as sql
import numpy as np
import matplotlib.pyplot as plt

from string import digits
from gensim.models import KeyedVectors
from sklearn.cluster import DBSCAN
from wordcloud import WordCloud
from nltk import word_tokenize, WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from distance import levenshtein


nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

vec = []
lemmatizer = WordNetLemmatizer()

#connect to sql db
db_connection = sql.connect(host='localhost', database='swapcard', user='root', password='coucou74')

#create dataframe from our db
dfJobTtl = pd.read_sql("select job_title from user where not tags='[]' and not companies='[]' group by job_title order by count(*) desc limit 100", con=db_connection)
dfJobTtl = dfJobTtl.loc[2:]
print(dfJobTtl.head())


#take our job title into a string
text = dfJobTtl.to_string()

#removing the digits from the list
remove_digits = str.maketrans('', '', digits)
text2 = text.translate(remove_digits)
print(text2)

#removing characters
table = str.maketrans({key: ' ' for key in string.punctuation})
sentences = text2.translate(table).replace('d’', ' ')


#convert string to lowercase
sentences = sentences.lower()

#suppression de mots de 2 lettres ou moins
tab = []
tab = sentences.split()
for i in tab:
    if len(i) < 3:
        tab.remove(i)
print(tab)
chaine = " ".join(tab)

#use of nltk
tokens = nltk.word_tokenize(chaine)
print(tokens)
tagged = nltk.pos_tag(tokens)
print(tagged[0:6])


##################################################################################################

vectors = pickle.load(open('foo','rb'))
model = KeyedVectors.load_word2vec_format('testvec')
print('Model built')

import winsound
frequency = 1500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)


##################################################################################################
##################################################################################################

def fillveccluster(namelist):
    for a in namelist:
        if a in model.vocab:
            vec.append((a, model[a]))
    return vec

##################################################################################################

def cleaner(entree):

    print("Bonjour, je crois comprendre que vous êtes", entree)
    entree = entree.lower()

# découpe la chaine de caractère (tokenize)
    entree = entree.replace('-', ' ').replace('/', ' ').replace(digits, ' ')
    tokenized_entree = word_tokenize(entree)
    print(tokenized_entree)

    no_caract_entree = []
    for word in tokenized_entree:
        if word not in string.punctuation:
            no_caract_entree.append(word)
    print(no_caract_entree)

# supprime les stopword
    stoplist = set(stopwords.words('french'))
    int_no_stopwords = []
    for word in no_caract_entree:
        if word not in stoplist:
            int_no_stopwords.append(word)

# ramène les mots à leur racine
    stemmed_entree = []
    stemmer = SnowballStemmer('french')
    for word in int_no_stopwords:
        stemmed_entree.append(stemmer.stem(word))
    print(stemmed_entree)

# ramène les mots à leur forme la plus simple (lemmatize)
    lemmatized_entree = []
    for word in stemmed_entree:
        lemmatized_entree.append(lemmatizer.lemmatize(word))
    print(lemmatized_entree)
    lemmatized_str = " ".join(lemmatized_entree)

    metier = pd.read_csv('jobs.csv', sep='\t', low_memory=False)
    liste_metier = metier['libellé métier']


# propose une correction de l'orthographe
    if lemmatized_str not in model.vocab:
        mini = 100
        monmot = None

        # trouver la distance minimum et la print
        for nom in liste_metier:
            distance_lev = levenshtein(nom, lemmatized_str)
            if distance_lev < mini:
                 monmot = nom
            mini = min(mini, distance_lev)

        print('Le terme dans le dictionnaire le plus proche du mot saisi est à une distance de:', mini)
        print('TERME LE PLUS PROCHE', monmot)



    if lemmatized_str not in model.vocab:
        return exit("Merci de ré-essayer avec une orthographe correcte")

# Affichage des vecteurs du candidat

# vec.append((lemmatized_str, model[lemmatized_str]))
# print(vec)

##################################################################################################

#Récupération du Cold Start Candidate
entree = input("Entrez votre métier: ")
start_time = time.time()
cleaner(entree)


#faire la moyenne des vecteurs
#dist = KeyedVectors.distance(cold_start[1], cold_start[2])
# #pb car capte pas les deux distances à calculer
#print(dist)

#Placement du candidate dans nos clusters


#Renvoyer les termes les plus proches de notre candidat


##################################################################################################
dbVec = [v[1] for v in vectors]

cluster = DBSCAN(eps=0.5, min_samples=1, metric='cosine').fit(dbVec)
print(cluster.labels_)

##################################################################################################


#compter nombre de clusters
count = 0
for i in range(min(cluster.labels_), max(cluster.labels_)):
    nbr = max(cluster.labels_) +1

print('On a ', nbr, 'clusters !')

#compter nombre de mots clusterisés
num_out = (cluster.labels_ == -1).sum()
tot = 0
for i in cluster.labels_:
    tot = tot +1

print('On a ', tot, 'mots dans notre liste de métiers')
print(num_out, 'ne sont pas compris dans un cluster')

percent = 100 - round(num_out/tot * 100, 2)
print('Le pourcentage de mots clusterisés est de :', percent, '%')


##################################################################################################
"""
#WordCloud

wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(chaine)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
"""

##################################################################################################
##################################################################################################
"""
# PLOTTING OUR WORDS TO SEE REPARTITION

from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.datasets.samples_generator import make_blobs


# Generate sample data
#centers = [[1, 1], [-1, -1], [1, -1]]
X, labels_true = make_blobs(n_samples=tot, random_state=0)
X = StandardScaler().fit_transform(X)

# Compute DBSCAN
core_samples_mask = np.zeros_like(cluster.labels_, dtype=bool)
core_samples_mask[cluster.core_sample_indices_] = True
labels = cluster.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

print('Estimated number of clusters: %d' % n_clusters_)
print('Estimated number of noise points: %d' % n_noise_)
print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
print("Adjusted Rand Index: %0.3f"
      % metrics.adjusted_rand_score(labels_true, labels))
print("Adjusted Mutual Information: %0.3f"
      % metrics.adjusted_mutual_info_score(labels_true, labels))
print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(X, labels))

# Plot result

# Black removed and is used for noise instead.
unique_labels = set(labels)
colors = [plt.cm.Spectral(each)
          for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = (labels == k)

    xy = X[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),   # 'o' : marker en forme de cercle
             markeredgecolor='k', markersize=14)

    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()

##################################################################################################
#CALCULATING MOST APPROPRIATE VALUE OF EPSILON

from yellowbrick.cluster import KElbowVisualizer
from sklearn.cluster import KMeans

mod = KMeans()
visualizer = KElbowVisualizer(mod, k=(1, 10))
visualizer.fit(X)
visualizer.poof()
"""
##################################################################################################

#Performing PCA
"""
from sklearn import decomposition
from sklearn import preprocessing

std_scale = preprocessing.StandardScaler().fit(X)
X_scaled = std_scale.transform(X)
pca = decomposition.PCA(n_components=2)
pca.fit(X_scaled)

print(pca.n_components_)
print(pca.explained_variance_ratio_)
print(pca.explained_variance_ratio_.sum())
"""

##################################################################################################


print("----- TEMPS DE REPONSE : %s secondes ----- " % (time.time() - start_time))
