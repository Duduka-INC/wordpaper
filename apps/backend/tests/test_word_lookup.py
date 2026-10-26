import io
import json
import unittest

from wordpaper_api.word_lookup import (
    DictionaryRouter,
    FreeDictionaryProvider,
    RussianWiktionaryProvider,
    WordNotFoundError,
    detect_language,
)


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
        self.assertEqual(entry.source_license, "CC BY-SA 3.0 / GFDL")

    def test_rejects_empty_word_before_network_request(self) -> None:
        provider = FreeDictionaryProvider()

        with self.assertRaises(WordNotFoundError):
            provider.lookup("  ")

    def test_detects_language_from_alphabet(self) -> None:
        self.assertEqual(detect_language("serendipity"), "en")
        self.assertEqual(detect_language("чудо"), "ru")

    def test_router_selects_provider_automatically(self) -> None:
        class FakeProvider:
            def __init__(self, language: str) -> None:
                self.language = language

            def lookup(self, word: str, language: str = "en"):
                return word, self.language, language

        router = DictionaryRouter(
            {"en": FakeProvider("english"), "ru": FakeProvider("russian")}
        )

        self.assertEqual(router.lookup("слово"), ("слово", "russian", "ru"))
        self.assertEqual(router.lookup("word"), ("word", "english", "en"))

    def test_maps_russian_wiktionary_extract(self) -> None:
        extract = """
= Русский =
=== Морфологические и синтаксические свойства ===
Существительное, неодушевлённое, средний род.
=== Произношение ===
МФА: ед. ч. [ˈsɫovə]
=== Семантические свойства ===
==== Значение ====
лингв. основная структурно-семантическая единица языка ◆ пример
==== Синонимы ====
=== Этимология ===
От праслав. *slovo.
= Болгарский =
"""
        payload = {
            "query": {
                "pages": {
                    "14083": {
                        "pageid": 14083,
                        "title": "слово",
                        "extract": extract,
                    }
                }
            }
        }
        provider = RussianWiktionaryProvider(
            opener=lambda *_args, **_kwargs: FakeResponse(json.dumps(payload).encode())
        )

        entry = provider.lookup(" слово ")

        self.assertEqual(entry.word, "слово")
        self.assertEqual(entry.transcription, "[ˈsɫovə]")
        self.assertEqual(entry.part_of_speech, "существительное")
        self.assertEqual(entry.language, "Русский")
        self.assertEqual(
            entry.definition,
            "лингв. основная структурно-семантическая единица языка",
        )
        self.assertEqual(entry.origin, "От праслав. *slovo.")
        self.assertEqual(entry.source_license, "CC BY-SA 4.0 / GFDL")


if __name__ == "__main__":
    unittest.main()
