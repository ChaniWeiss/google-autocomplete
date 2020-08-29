from dataclasses import dataclass

num_suggestions = 5

@dataclass
class AutoCompleteData:
    completed_sentence: str
    source_text: str
    offset: int
    score: int

    def __init__(self, sentence, file_name, offset, score):
        self.completed_sentence = sentence
        self.source_text = file_name
        self.offset = offset
        self.score = score

#----------------------------score functions-----------------------------#
def perfect_score(term):
    return len(term) * 2


def replacement_score(args):
    term = args['term']
    i = args['index']
    neg_scores = {0: 5, 1: 4, 2: 3, 3: 2}
    negative_score = neg_scores[i] if i in neg_scores else 1
    return (i + len(term) - 1) * 2 - negative_score


def remove_add_letter_score(args):
    term = args['term']
    i = args['index']
    neg_scores = {0: 10, 1: 8, 2: 6, 3: 4}
    negative_score = neg_scores[i] if i in neg_scores else 2
    return (i + len(term)) * 2 - negative_score
#---------------------------------------------------------------------#

#---------------------helpers match functions-----------------------------#

def smaller_str_id(matches):
    return sorted(matches, key=lambda i: i['string'])[:num_suggestions]


def calc_offset(term, sentence):
    sentence = ''.join(e for e in sentence if e.isalnum()).lower()
    return sentence.find(term)


def init_AutoCompleteData(matches):
    result = []
    for match in matches:
        result.append(AutoCompleteData(match['string'], match['file_name'], match['offset'], match['score']))
    return result


def best_score_for_same_id(matches):
    matches_ids = {}
    for match in matches:
        if match['id'] in matches_ids:
            if match['score'] > matches_ids[match['id']]['score']:
                matches_ids[match['id']] = match
        else:
            matches_ids[match['id']] = match
    return list(matches_ids.values())


def update_score_heap(matches, new_matches, score):
    matches += [{'score': score, 'id': match['id'], 'offset': match['offset'], 'file_name': match['file_name'],
                 'string': match['string']} for match in new_matches]
    matches = best_score_for_same_id(matches)
    largest = []
    for i in range(min(len(matches),num_suggestions)):
        largest.append(max(matches, key=lambda i: i['score']))
        matches.remove(largest[-1])
    return largest


def possible_replacement_letters(trie, term):
    return trie['next_letters'].keys() - [term[0]]


#---------------------------------------------------------------------#


#------------------------- match functions----------------------------#


def get_perfect_matches(term, i, trie, strings, new_term=None):
    new_term = term if not new_term else new_term
    curr = trie
    if term[i:] != '':
        for letter in term[i:]:
            if letter not in curr['next_letters']:
                if not curr['next_letters']:
                    break
                return None
            curr = curr['next_letters'][letter]
    return [{"id": id, "string": strings[id][0], "file_name": strings[id][1],
             "offset": calc_offset(new_term, strings[id][0])} for id in curr['ids']]


def find_perfect_matches(term, trie, strings):
    matches = get_perfect_matches(term, 0, trie, strings)
    if not matches:
        return []
    score = perfect_score(term)
    for match in matches:
        match['score'] = score
    if len(matches) >= num_suggestions:
        matches = smaller_str_id(matches)
        return init_AutoCompleteData(matches)
    return matches


def replacement_matches(possible_matches, term, i, trie, strings):
    result = possible_matches
    score = replacement_score({"term": term[i:], "index": i})
    for letter in possible_replacement_letters(trie, term[i:]):
        new_term = term[:i] + letter + term[i + 1:]
        matches = get_perfect_matches(term, i + 1, trie['next_letters'][letter], strings, new_term)
        if not matches:
            continue
        result = update_score_heap(result, matches, score)
    return result


def add_letter_matches(possible_matches, term, i, trie, strings):
    score = remove_add_letter_score({"term": term[i:], "index": i})
    result = possible_matches
    for letter in trie['next_letters']:
        new_term = term[:i] + letter + term[i:]
        matches = get_perfect_matches(term, i, trie['next_letters'][letter], strings, new_term)
        if not matches:
            continue
        result = update_score_heap(result, matches, score)
    return result


def remove_letter_matches(possible_matches, term, i, trie, strings):
    score = remove_add_letter_score({"term": term[i:], "index": i})
    result = possible_matches
    if term[i + 1:] == "":
        return result
    new_term = term[:i] + term[i + 1:]
    matches = get_perfect_matches(term, i + 1, trie, strings, new_term)
    if matches:
        result = update_score_heap(result, matches, score)
    return result


def find_matches(term, trie, strings, possible_matches):
    non_perfect_match_func = [replacement_matches, add_letter_matches, remove_letter_matches]
    curr = trie
    possible_matches = possible_matches
    for i, letter in enumerate(term):
        for match_func in non_perfect_match_func:
            possible_matches = match_func(possible_matches, term, i, curr, strings)
        if letter not in curr['next_letters']:
            break
        curr = curr['next_letters'][letter]

    return init_AutoCompleteData(possible_matches)

#---------------------------------------------------------------------#


def complete(term, trie, strings):
    result = find_perfect_matches(term, trie, strings)
    if len(result) < num_suggestions:
        result = find_matches(term, trie, strings, result)
    return sorted(result, key=lambda i: i.score, reverse=True)
