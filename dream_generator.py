import random

import nltk
from nltk.probability import LidstoneProbDist

import dream_images

MUTATE_TAGS = ('NN', 'NNS')  # ('NN', 'NNS', 'VB', 'VBD', 'VBG', 'VBN', 'RB', 'JJ', 'JJR', 'JJS')
COMP_SAMPLE_SIZE = 3


class DreamContext:
    def __init__(self):
        self.dream_tokens = []
        self.merged_tokens = []
        self.characteristics = {}

    def add_characteristic(self, tag):
        if tag[1] not in self.characteristics:
            self.characteristics[tag[1]] = set()
        self.characteristics[tag[1]].add(tag[0])

    def add_dream_text(self, dream):
        sentences = nltk.sent_tokenize(dream)
        tokens = []
        for s in sentences:
            tokenized_sent = nltk.word_tokenize(s)
            tokens += tokenized_sent

        tagged_sent = nltk.pos_tag(tokens)
        for tup in tagged_sent:
            if tup[1] in MUTATE_TAGS:
                self.add_characteristic(tup)

        self.dream_tokens.append(tokens)
        self.merged_tokens += tokens


class DreamEntry:
    def __init__(self, tokens):
        self.text = ' '.join(tokens)
        self.tokens = tokens
        self.nouns = set()
        self.verbs = []

        tags = nltk.batch_pos_tag([self.tokens])
        for tag in tags[0]:
            if tag[1] in ('NN', 'NNS'):
                self.nouns.add(tag[0])
        print self.nouns
        image_url = False
        attempts = 0;
        while not image_url and attempts < 5:
            noun = random.sample(self.nouns, 1)[0]
            print "Getting image using ", noun
            image_url = dream_images.get_photo(noun)
            attempts += 1
        print "image={}".format(image_url)

    def __str__(self):
        return self.text


def load_random_dreams(dreams, num):
    result = []

    for i in range(0, num):
        index = random.randrange(len(dreams))
        sents = nltk.sent_tokenize(dreams[index])
        for s in sents:
            result += nltk.word_tokenize(s)

    return result


def mutate_dream(dream, context):
    sents = nltk.sent_tokenize(dream)
    new_sents = []

    est = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
    content_model = nltk.NgramModel(3, context.merged_tokens, estimator=est)

    part_samples = {}
    for tag in context.characteristics:
        comp_set = context.characteristics[tag]
        part_samples[tag] = random.sample(comp_set, min(COMP_SAMPLE_SIZE, len(comp_set)))

    mutate_map = {}

    for s in sents:
        tok = nltk.tokenize.word_tokenize(s)
        tag = nltk.pos_tag(tok)
        for tup in tag:
            if tup[1] in MUTATE_TAGS:
                attempts = 0
                print "CHANGING", tup
                if tup[0] in mutate_map:
                    word = mutate_map[tup[0]]
                else:
                    if random.randrange(3) >= 1:
                        word = tup[0]
                    else:
                        while True:
                            word = random.sample(context.characteristics[tup[1]], 1)[0]
                            # word = content_model.choose_random_word(new_sents[-2:])
                            new_tag = nltk.pos_tag([word])[0]

                            # print word, new_tag
                            if new_tag[0] != tup[0] and new_tag[1] == tup[1]:
                                break
                            if attempts > 4:
                                word = random.sample(context.characteristics[tup[1]], 1)[0]
                                break
                            attempts += 1
                    mutate_map[tup[0]] = word
                print tup[0], "=>", word
                new_sents.append(word)
            else:
                new_sents.append(tup[0])
    return new_sents


def generate_dream(context, num_words=200):
    # pull tokens from dreams
    # tokenized_content = load_random_dreams(dreams, 4)

    # create N-gram modeler for content generation
    est = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
    content_model = nltk.NgramModel(3, context.merged_tokens, estimator=est)

    # Starting words (i.e. "seed" for generator)
    starting_words = ["I", "was"]
    # starting_words = content_model.generate(100)[-2:]

    content = content_model.generate(num_words, starting_words)
    entry = DreamEntry(content)
    return entry


def test(entries):
    nouns = []
    for e in entries:
        sentences = nltk.sent_tokenize(e)
        sentences = [nltk.word_tokenize(s) for s in sentences]
        sentences = [nltk.pos_tag(s) for s in sentences]

        for s in sentences:
            det = False
            for tup in s:
                if tup[1] == 'DT' and tup[0] in ('a', 'an', 'the'):
                    det = True
                elif det and tup[1] in ('NN', 'NNS'):
                    nouns.append(tup[0])
                    det = False

    print nouns
