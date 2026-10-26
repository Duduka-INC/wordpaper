import io
import json
import unittest

from wordpaper_api.word_lookup import FreeDictionaryProvider, WordNotFoundError


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class WordLookupTests(unittest.TestCase):
    def test_maps_external_dictionary_response(self) -> None:
        payload = [
            {
                "word": "serendipity",
                "phonetics": [{"text": "ˌserənˈdɪpəti"}],
                "meanings": [
                    {
                        "partOfSpeech": "noun",
                        "definitions": [
                            {"definition": "A fortunate discovery made by chance."}
                        ],
                    }
                ],
                "origin": "Coined by Horace Walpole.",
            }
        ]
        provider = FreeDictionaryProvider(
            opener=lambda *_args, **_kwargs: FakeResponse(json.dumps(payload).encode())
        )

        entry = provider.lookup(" serendipity ")

        self.assertEqual(entry.word, "serendipity")
        self.assertEqual(entry.transcription, "/ˌserənˈdɪpəti/")
        self.assertEqual(entry.part_of_speech, "noun")
        self.assertEqual(entry.language, "English")
        self.assertEqual(entry.definition, "A fortunate discovery made by chance.")

    def test_rejects_empty_word_before_network_request(self) -> None:
        provider = FreeDictionaryProvider()

        with self.assertRaises(WordNotFoundError):
            provider.lookup("  ")


if __name__ == "__main__":
    unittest.main()
