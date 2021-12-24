from bs4 import BeautifulSoup
from bs4.element import Tag
import requests

BASE_URL = "http://ordnet.dk/ddo/ordbog?query="


def get_word_info(word, pos=None):
    link = BASE_URL + word
    if (pos is not None):
        link = link + f",{pos}"
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'html.parser')

    # nomatch = soup.select('.nomatch')
    # if len(nomatch) > 0:
    #     bojning = None
    #     audio = None
    #     part_of_speech = None
    #     kon = None
    #     print(f'WARN: Word "{word}" not found in the ordbog')
    # else:

    # bojning
    bojning_element = soup.select_one('#id-boj .tekstmedium')
    if bojning_element is not None:
        bojning = list(
            map(lambda x: x.strip(), bojning_element.get_text().split('\xa0')))
    else:
        bojning = None

    # definition
    definition_elements = soup.select('.definitionBoxTop .allow-glossing')

    if len(definition_elements) > 0:
        definition = definition_elements[0].get_text().strip().split(',')
        part_of_speech = definition[0]
        kon = definition[1].strip() if part_of_speech == 'substantiv' and len(
            definition) >= 2 else None
    else:
        part_of_speech = None
        kon = None

    udtale_main_element = soup.select_one('#id-udt')

    if udtale_main_element is not None:
        # print(udtale_main_element)
        udtale_elements = udtale_main_element.select(
            '.lydskrift, .lydskrift ~ .diskret, .dividerDouble')

        # print(udtale_elements)

        def udtale_element_mapper(el: Tag):
            if el.has_attr('class') and 'dividerDouble' in el['class']:
                return '||'
            else:
                return el.get_text().strip().replace('\xa0', '')

        ipa = ' '.join(list(map(udtale_element_mapper, udtale_elements)))

        # audio
        audio_elements = udtale_main_element.select('audio a')
        if len(audio_elements) > 0:
            audio = list(map(lambda x: x.get('href'), audio_elements))
        else:
            audio = None

    else:
        ipa = None
        audio = None

    return {
        'word': word,
        'bojning': bojning,
        'ipa': ipa,
        'audio': audio,
        'part_of_speech': part_of_speech,
        'kon': kon,
        'dictionary_url': link
    }


if __name__ == '__main__':
    r = get_word_info('sige')
    print(r)
