from bs4 import BeautifulSoup
import requests

BASE_URL = "https://ordnet.dk/ddo/ordbog?query="


def get_word_info(word):
    link = BASE_URL + word
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
    bojning_elements = soup.select('#id-boj .tekstmedium')
    if len(bojning_elements) > 0:
        bojning = list(map(lambda x: x.strip(), bojning_elements[0].get_text().split(
            '\xa0'))) if len(bojning_elements) > 0 else None
    else:
        bojning = None

    # audio
    audio_elements = soup.select('#id-udt audio a')
    if len(audio_elements) > 0:
        audio = list(map(lambda x: x.get('href'), audio_elements))
    else:
        audio = None

    #definition
    definition_elements = soup.select('.definitionBoxTop .allow-glossing')

    if len(definition_elements) > 0:
        definition = definition_elements[0].get_text().strip().split(',')
        part_of_speech = definition[0]
        kon = definition[1].strip() if part_of_speech == 'substantiv' and len(definition) >= 2 else None
    else:
        part_of_speech = None
        kon = None

    return {
        'word': word,
        'bojning': bojning,
        'audio': audio,
        'part_of_speech': part_of_speech,
        'kon': kon,
        'dictionary_url': link
    }


if __name__ == '__main__':
    r = get_word_info('hvor længe')
    print(r)
