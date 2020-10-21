from bs4 import BeautifulSoup
import requests

BASE_URL = "https://ordnet.dk/ddo/ordbog?query="


def get_word_info(word):
    link = BASE_URL + word
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'html.parser')
    bojning_elements = soup.select('#id-boj .tekstmedium')
    bojning = list(map(lambda x: x.strip(), bojning_elements[0].get_text().split(
        '\xa0'))) if len(bojning_elements) > 0 else None
    audio = list(map(lambda x: x.get('href'), soup.select('#id-udt audio a')))
    definition_elements = soup.select(
        '.definitionBoxTop .allow-glossing')[0].get_text().strip().split(',')
    part_of_speech = definition_elements[0]
    kon = definition_elements[1].strip() if part_of_speech == 'substantiv' else None

    return {
        'word': word,
        'bojning': bojning,
        'audio': audio,
        'part_of_speech': part_of_speech,
        'kon': kon
    }


if __name__ == '__main__':
    r = get_word_info('tyve')
    print(r)
