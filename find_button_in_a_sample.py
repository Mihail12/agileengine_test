import difflib
import re
import sys

from bs4 import BeautifulSoup


def read_file(path):
    with open(path, 'r') as f:
        text = f.read()
    return text


def similarity(normalized1, s2):
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


def get_max_similar(similarity_gen):
    max_, value = 0, ''
    for sim in similarity_gen:
        if sim[0] > max_:
            max_, value = sim
    return max_, value


def find_in_sample(html_origin, html_sample):
    origin_button = re.findall(r'<.+\s+?id=[\"\']make-everything-ok-button[\"\'][\s\S]*?>[\s\S]*?</.+>', html_origin)
    origin_button_tag = origin_button[0] if origin_button else ''

    tag_name = re.findall(r'<(\w+)', origin_button_tag)[0]

    all_buttons = re.findall(rf'<{tag_name}[\s\S]+?>[\s\S]*?</{tag_name}>', html_sample)

    normalized_origin_button = origin_button_tag.lower()
    similarity_gen = ((similarity(normalized_origin_button, b), b) for b in all_buttons)
    _, tag = get_max_similar(similarity_gen)
    return tag


def xpath_soup(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name
            if siblings == [child] else
            '%s[%d]' % (child.name, 1 + siblings.index(child))
        )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


def get_xpath_to_tag(html, tag):
    tag_name = re.findall(r'<(\w+)', tag)[0]
    tag_attrs = BeautifulSoup(tag, 'html.parser').find('a').attrs
    bs = BeautifulSoup(html, 'html.parser').find(tag_name, tag_attrs)
    return xpath_soup(bs)


if __name__ == '__main__':
    path_to_origin = sys.argv[1]
    html_origin = read_file(path_to_origin)
    path_to_sample = sys.argv[2]
    html_sample = read_file(path_to_sample)

    tag = find_in_sample(html_origin, html_sample)
    sys.exit(get_xpath_to_tag(html_sample, tag))



