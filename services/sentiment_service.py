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


# -------------------------------------------------------
# Domain-specific complaint keywords (negative push)
# These words are common in app reviews but SentiWordNet
# fails to score them correctly in context
# -------------------------------------------------------
COMPLAINT_KEYWORDS = {
    # Performance issues
    'crash', 'crashes', 'crashed', 'crashing',
    'slow', 'slower', 'slowest', 'lag', 'lagging', 'lags',
    'freeze', 'freezes', 'frozen', 'hang', 'hangs', 'hanging',
    'bug', 'bugs', 'buggy', 'glitch', 'glitches',
    'error', 'errors', 'broken', 'fail', 'fails', 'failed',
    # Trust issues
    'scam', 'fraud', 'fake', 'cheat', 'cheating', 'steal',
    'waste', 'useless', 'worthless', 'garbage', 'trash',
    'spam', 'virus', 'malware', 'dangerous', 'unsafe',
    # User experience
    'terrible', 'horrible', 'awful', 'worst', 'pathetic',
    'disappointing', 'disappointed', 'uninstall', 'refund',
}

# Positive boost keywords (in case SentiWordNet misses them)
POSITIVE_KEYWORDS = {
    'fast', 'smooth', 'reliable', 'stable', 'easy',
    'useful', 'helpful', 'recommend', 'recommended'
}

COMPLAINT_PENALTY = 0.15   # subtract per complaint word found
POSITIVE_BOOST    = 0.10   # add per positive keyword found


def analyze_sentiment(text):
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t.isalpha()]  # remove punctuation & numbers

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

        # Fix #1: Top 3 synsets average — reduces wrong meaning issue
        k = min(3, len(synsets))
        p = n = o = 0.0
        for i in range(k):
            ss = swn.senti_synset(synsets[i].name())
            p += ss.pos_score()
            n += ss.neg_score()
            o += ss.obj_score()

        pos_score += (p / k)
        neg_score += (n / k)
        obj_score += (o / k)
        count += 1

    if count == 0:
        # Even if no SentiWordNet words found, apply keyword rules
        base_score = 0.0
    else:
        avg_pos = pos_score / count
        avg_neg = neg_score / count
        avg_obj = obj_score / count
        base_score = round(avg_pos - avg_neg, 4)

    # -------------------------------------------------------
    # Rule-based correction — domain keyword adjustment
    # Handles complaint/positive words SentiWordNet misses
    # -------------------------------------------------------
    token_set = set(tokens)

    complaint_hits = token_set & COMPLAINT_KEYWORDS
    positive_hits  = token_set & POSITIVE_KEYWORDS

    rule_adjustment = 0
    rule_adjustment -= len(complaint_hits) * COMPLAINT_PENALTY
    rule_adjustment += len(positive_hits)  * POSITIVE_BOOST

    final_score = round(base_score + rule_adjustment, 2)

    # -------------------------------------------------------
    # Sentiment Label
    # -------------------------------------------------------
    if final_score > 0.05:
        label = "Positive"
    elif final_score < -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    # -------------------------------------------------------
    # Fake Probability
    # subjectivity * extremity (capped at 1.0)
    # -------------------------------------------------------
    if count > 0:
        avg_obj = obj_score / count
        subjectivity = round(1 - avg_obj, 4)
    else:
        subjectivity = 0.5  # unknown = assume moderate

    extremity        = round(min(abs(final_score) * 2, 1.0), 4)
    fake_probability = round(subjectivity * extremity, 2)

    return label, final_score, fake_probability
