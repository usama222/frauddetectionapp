import nltk
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag


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
    obj_score = 0
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
        obj_score += senti_synset.obj_score()
        count += 1

    if count == 0:
        return "Neutral", 0.0, 0.0

    # Average scores per word
    avg_pos = pos_score / count
    avg_neg = neg_score / count
    avg_obj = obj_score / count

    # Net sentiment score
    score = round(avg_pos - avg_neg, 2)

    # Sentiment label
    if score > 0.05:
        label = "Positive"
    elif score < -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    # -------------------------------------------------------
    # Fake Probability — based on subjectivity + extremity
    # A review is suspicious when:
    #   - It is highly subjective (low objectivity)
    #   - AND has extreme sentiment (very high pos or neg)
    # Formula: subjectivity * extremity (capped at 1.0)
    # -------------------------------------------------------
    subjectivity = round(1 - avg_obj, 4)          # 0=objective, 1=subjective
    extremity    = round(min(abs(score) * 2, 1.0), 4)  # 0=mild, 1=extreme
    fake_probability = round(subjectivity * extremity, 2)

    return label, score, fake_probability
