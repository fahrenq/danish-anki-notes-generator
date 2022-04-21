from get_word_info import get_word_info
import genanki
import requests
from os import path
import json


def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default


class QuestionOnlyHashNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])


deck = genanki.Deck(2059400110, '🇩🇰 Danish')

package = genanki.Package(deck)
package.media_files = []

css = """
.card {
  background-image: url("bg-english.jpg");
  background-size: cover;
}

.front + .back {
  border-radius: 0px 0px 7px 7px;
  position: relative;
  top: -7px;
}

.back + .front {
  border-radius: 0px 0px 7px 7px;
  position: relative;
  top: -7px;
}

.front {
  background-color: #18adaa;
  padding: 20px;
  border-radius: 7px;
}

.back {
  background-color: white;
  color: #016ea6;
  padding: 20px;
  border-radius: 7px;
}

.word {
  font-size: 50px;
  text-align: center;
}

.phonetic {
  text-align: center;
  font-size: 20px;
  margin-top: 10px;
  font-family: monospace;
}

.part-of-speech {
  text-align: center;
  margin-top: 5px;
}

.kon {
  text-align: center;
}

.bojning {
  text-align: center;
  margin-top: 5px;
}

.definition {
  font-size: 40px;
  margin-top: 10px;
  text-align: center;
}

.example {
  margin-top: 10px;
  color: #6d8891;
  text-align: center;
}

.type-prompt input {
  width: 100%;
  padding: 12px 20px;
  border: 2px solid #6d8891;
  border-radius: 4px;
  background-color: white !important;
  color: #6d8891 !important;
  font-size: 20px;
}

.type-prompt {
  margin-top: 20px;
  text-align: center;
  font-size: 20px
}

.first-letters {
  text-align: center;
  font-size: 30px;
  font-family: monospace;
  letter-spacing: 2px;
}

.replay-button { text-decoration: none; display: inline-flex; vertical-align: middle; margin: 3px; }
.replay-button svg { width: 25px; height: 25px; }
.replay-button svg circle { fill: none; stroke: #fff; }
.replay-button svg path { fill: #fff; }



"""

qfmt = """
<div class="front">
  <div class="word">{{Question}}</div>
  <div class="part-of-speech">{{PartOfSpeech}}</div>
  <div class="phonetic">{{IPA}}</div>
</div>
"""

afmt = """
<div class="front">
  <div class="word">{{Question}}</div>
  <div class="part-of-speech">{{PartOfSpeech}}</div>
  <div class="phonetic">{{IPA}}{{#Media}}{{Media}}{{/Media}}</div>
</div>

<div class="back">

  <div class="kon">
      {{Køn}}
  </div>
  <div class="bojning">
      {{Bøjning}}
  </div>
  <div class="definition">
      {{Answer}}
  </div>
  <div class="example">
      {{Example}}
  </div>

</div>
"""

qfmtR = """
<div class="front">
  <div class="first-letters"></div>
  <div class="type-prompt">{{type:Question}}</div>
  <div class="part-of-speech">{{PartOfSpeech}}</div>
</div>

<div class="back">

<div class="definition">
    {{Answer}}
</div>
<div class="example">
    {{Example}}
</div>

</div>

<script>
var input = "{{Question}}";
var output = input.replace(/(?<=[A-zÅåÆæØøÄäÖöÜüẞß()])([A-zÅåÆæØøÄäÖöÜüẞß])/g, '_');
document.querySelector(".first-letters").innerHTML = output;
</script>
"""

afmtR = """
<div class="front">
  <div class="word">{{Question}}</div>
  <div class="part-of-speech">{{PartOfSpeech}}</div>
  <div class="phonetic">{{IPA}}{{#Media}}{{Media}}{{/Media}}</div>
  <div class="type-prompt">{{type:Question}}</div>
</div>

<div class="back">

<div class="kon">
    {{Køn}}
</div>
<div class="bojning">
    {{Bøjning}}
</div>
<div class="definition">
    {{Answer}}
</div>
<div class="example">
    {{Example}}
</div>

</div>
"""

model = genanki.Model(1091735114, 'Danish (and reversed card)',
                      fields=[
                          {'name': 'Question'},
                          {'name': 'Bøjning'},
                          {'name': 'PartOfSpeech'},
                          {'name': 'Køn'},
                          {'name': 'Example'},
                          {'name': 'Answer'},
                          {'name': 'Media'},
                          {'name': 'IPA'},
                      ],
                      css=css,
                      templates=[
                          {
                              'name': 'Card 1',
                              'qfmt': qfmt,
                              'afmt': afmt
                          },
                          {
                              'name': 'Card 2',
                              'qfmt': qfmtR,
                              'afmt': afmtR
                          },
                      ])

if __name__ == '__main__':
    cache_file_exists = path.exists('./cache.json')
    if not cache_file_exists:
        cache_file = open('./cache.json', 'w+')
        cache_file.write('[]')
        cache_file.seek(0)
    else:
        cache_file = open('./cache.json', 'r+')
    cache = json.load(cache_file)

    with open('./words.csv') as f:
        for line in f.readlines():
            tokenised = line.strip().split('|')

            word = tokenised[0]
            cached = next((x for x in cache if x['Word'] == word), None)
            translation = tokenised[1]
            example = safe_list_get(tokenised, 2, "")

            # Audio position
            audio_position = safe_list_get(tokenised, 3, None)
            if audio_position == "":
                audio_position = None

            if audio_position is not None:
                audio_position = int(audio_position)
            else:
                audio_position = 0

            # Dict Position
            dict_position = safe_list_get(tokenised, 4, None)

            if dict_position is not None:
                dict_position = int(dict_position)

            # print(dict_position, cached['dict_position'])

            # Cache
            cache_available = \
                cached is not None \
                and cached['audio_position'] == audio_position \
                and cached['dict_position'] == dict_position

            if cache_available:
                print(f'Using cache for word "{word}"')
            else:
                print(f'No cache found for word "{word}"')

                first_word = word.split(',')[0]
                first_word = first_word.split('(')[0]
                info = get_word_info(first_word, dict_position)

                # audio
                if info.get('audio') is not None:
                    audio_urls = info.get('audio')

                    if len(audio_urls) > 1 and audio_position is None:
                        print(
                            'ATTENTION: No audio_position specified for a word that has more than one audio file. Defaulting to the first variant.')
                        print(
                            f'Word: {word}, Translation: {translation}, Dictionary URL: {info.get("dictionary_url")}')
                        # raise 'More than 1 audio found, audio position not specified'

                    audio_url = audio_urls[audio_position]
                    media_filename = audio_url.split('/')[-1]
                    media_path = './media/' + media_filename
                else:
                    audio_url = None
                    media_filename = None
                    media_path = None

                bojning = info.get('bojning')
                kon = info.get('kon')
                part_of_speech = info.get('part_of_speech')
                ipa = info.get('ipa')

                #   {'name': 'Question'},
                #   {'name': 'Bøjning'},
                #   {'name': 'PartOfSpeech'},
                #   {'name': 'Køn'},
                #   {'name': 'Example'},
                #   {'name': 'Answer'},
                #   {'name': 'Media'},
                #   {'name': 'IPA'},

                cached = {
                    'dict_position': dict_position,
                    'audio_position': audio_position,
                    'media_path': media_path,
                    'audio_url': audio_url,
                    'Word': word,
                    'Bøjning': ' || '.join(bojning) if bojning is not None else '',
                    'PartOfSpeech': part_of_speech if part_of_speech is not None else '',
                    'Køn': kon if kon is not None else '',
                    'Media': f'[sound:{media_filename}]' if media_filename is not None else '',
                    'IPA': ipa if ipa is not None else ''
                }

                cache = list(filter(lambda x: x['Word'] != word, cache))
                cache.append(cached)

            if cached['media_path'] is not None:
                if not path.exists(cached['media_path']):
                    print(f'Downloading audio for word "{word}"')
                    r = requests.get(cached['audio_url'])
                    with open(cached['media_path'], 'wb') as media_file:
                        media_file.write(r.content)
                package.media_files.append(cached['media_path'])

            note = QuestionOnlyHashNote(model=model, fields=[
                word,
                cached['Bøjning'],
                cached['PartOfSpeech'],
                cached['Køn'],
                example,
                translation,
                cached['Media'],
                cached['IPA'],
            ])
            deck.add_note(note)

    package.write_to_file('Danish.apkg')

    cache_file.seek(0)
    cache_file.truncate()
    cache_file.write(json.dumps(cache))
    cache_file.close()
