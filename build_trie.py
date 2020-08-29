import json
import os


max_chars_to_match = 50
num_suggestions = 5


def init_node(ids):
    return {"ids": ids if type(ids) is list else [ids], "next_letters": {}}


def insert_str_to_trie(root, str, id):
    curr = root
    clean_str = ''.join(e for e in str if e.isalnum()).lower()
    for letter in clean_str[:max_chars_to_match]:
        if letter not in curr['next_letters']:
            curr['next_letters'][letter] = init_node(id)
        elif id not in curr['next_letters'][letter]['ids']:
            if len(curr['next_letters'][letter]['ids']) < num_suggestions:
                curr['next_letters'][letter]['ids'].append(id)
        curr = curr['next_letters'][letter]


def insert_sub_str_to_trie(root, str, id):
    arr = str.split()
    for i in range(len(arr)):
        insert_str_to_trie(root, ''.join(arr[i:]), id)


def get_data_from_file():
    for root, dirs, files in os.walk('./nice_sentences'):
        for file in files:
            data = open(os.path.join(root, file), "r", encoding="utf8")
            yield data, file


def insert_strs_and_map(root):
    id = 0
    data = []
    for data_file, file_name in get_data_from_file():
        lines = (data_file.read()).split("\n")
        for line in lines:
            data.append([line, file_name])
            insert_sub_str_to_trie(root, line, id)
            id += 1
    root['ids'] = list(range(id))
    return data


def build():
    root = init_node([])
    data = insert_strs_and_map(root)
    data_for_file = [{"strings": data}, {"trie": root}]
    with open("trie.json", "w") as f:
        json.dump(data_for_file, f)


if __name__ == "__main__":
    build()
