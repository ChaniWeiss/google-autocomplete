import auto_complete
import json


def get_search_term(term):
    return input(term)


def read_trie():
    the_file = open('trie.json')
    data = json.load(the_file)
    the_file.close()
    return data[1]['trie'], data[0]['strings']


def clear_str(term):
    return (''.join(e for e in term if e.isalnum())).lower()


if __name__ == "__main__":
    trie, strings = read_trie()
    term = get_search_term("start searching: \n")

    while True:
        while (term[-1] == "#"):
            term = get_search_term("start searching: \n")
        result = auto_complete.complete(clear_str(term), trie, strings)
        for res in result:
            print("\033[91m {}\033[00m" .format(f"{res.completed_sentence} ({res.source_text}) /score: {res.score}, offset: {res.offset}"))
        if term[-1] == "#":
            term = get_search_term("start searching: \n")
        else:
            term = term + get_search_term(term)
