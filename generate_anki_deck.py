from get_word_info import get_word_info
import genanki
import requests


def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default


class QuestionOnlyHashNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])


deck = genanki.Deck(2059400110, 'Danish')


package = genanki.Package(deck)
package.media_files = []

css = """
.card {
    font-family: verdana;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}

.metainfo {
    font-size: 10px;
    margin-bottom: 10px;
}

.bojning {
    background-color: aliceblue;
    color: black;
    font-size: 15px;
    margin-bottom: 10px;
    line-height: 3;
}

.answer {
    margin-bottom: 10px;
}

.example {
    font-size: 15px;
}
"""
afmt = """
{{FrontSide}}
<hr id="answer">
<div class="metainfo">
    {{PartOfSpeech}} {{Køn}}
</div>
<div class="bojning">
    {{Bøjning}}
</div>
<div class="answer">
    {{Answer}}
</div>
<div class="example">
    {{Example}}
</div>
<br>
{{Media}}
"""

model = genanki.Model(1091735104, 'Danish',
                      fields=[
                          {'name': 'Question'},
                          {'name': 'Bøjning'},
                          {'name': 'PartOfSpeech'},
                          {'name': 'Køn'},
                          {'name': 'Example'},
                          {'name': 'Answer'},
                          {'name': 'Media'},
                      ],
                      css=css,
                      templates=[
                          {
                              'name': 'Card 1',
                              'qfmt': '{{Question}}',
                              'afmt': afmt
                          },
                      ])

if __name__ == '__main__':
    with open('./words.csv') as f:
        for line in f.readlines():
            tokenised = line.strip().split('|')

            word = tokenised[0]
            translation = tokenised[1]
            audio_position = safe_list_get(tokenised, 2, None)
            example = safe_list_get(tokenised, 3, "")
            dict_pos = safe_list_get(tokenised, 4, None)

            if audio_position == "":
                audio_position = None

            if audio_position is not None:
                audio_position = int(audio_position)

            info = get_word_info(word, dict_pos)

            # audio
            if info.get('audio') is not None:
                audio_urls = info.get('audio')

                if len(audio_urls) > 1 and audio_position is None:
                    print(
                        'ATTENTION: No audio_position specified for a word that has more than one audio file. Defaulting to the first variant.')
                    print(
                        f'Word: {word}, Translation: {translation}, Dictionary URL: {info.get("dictionary_url")}')
                    audio_position = 0
                    # raise 'More than 1 audio found, audio position not specified'

                if len(audio_urls) == 1:
                    audio_position = 0

                audio_url = audio_urls[audio_position]
                filename = audio_url.split('/')[-1]
                r = requests.get(audio_url)
                open('media/' + filename, 'wb').write(r.content)
                package.media_files.append('media/'+filename)
            else:
                filename = None

            bojning = info.get('bojning')
            kon = info.get('kon')
            part_of_speech = info.get('part_of_speech')

            note = QuestionOnlyHashNote(model=model, fields=[
                word,
                ' || '.join(bojning) if bojning is not None else '',
                part_of_speech if part_of_speech is not None else '',
                kon if kon is not None else '',
                example,
                translation,
                f'[sound:{filename}]' if filename is not None else ''
            ])
            deck.add_note(note)
            print(f'Added note for "{word}"')

    package.write_to_file('Danish.apkg')
