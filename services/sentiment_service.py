import nltk
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag

# Run once if not downloaded
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('sentiwordnet')

def penn_to_wn(tag):
    if tag.startswith('N'):
        return wordnet.NOUN
    if tag.startswith('V'):
        return wordnet.VERB
    if tag.startswith('J'):
        return wordnet.ADJ
    if tag.startswith('R'):
        return wordnet.ADV
    return None


def analyze_sentiment(text):
    tokens = word_tokenize(text.lower())
    tagged_words = pos_tag(tokens)

    pos_score = 0
    neg_score = 0
    count = 0

    for word, tag in tagged_words:
        wn_tag = penn_to_wn(tag)
        if not wn_tag:
            continue

        synsets = wordnet.synsets(word, wn_tag)
        if not synsets:
            continue

        senti_synset = swn.senti_synset(synsets[0].name())
        pos_score += senti_synset.pos_score()
        neg_score += senti_synset.neg_score()
        count += 1

    if count == 0:
        return "Neutral", 0.0, 0.0

    score = pos_score - neg_score

    if score > 0.05:
        label = "Positive"
    elif score < -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    fake_probability = round(abs(score), 2)

    return label, round(score, 2), fake_probability
