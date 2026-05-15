import random
from words import word_pairs


def assign_words(players):

    pair = random.choice(word_pairs)

    common_word = pair[0]
    imposter_word = pair[1]

    imposter = random.choice(players)

    assignments = {}

    for player in players:

        if player == imposter:
            assignments[player] = imposter_word

        else:
            assignments[player] = common_word

    return assignments, imposter