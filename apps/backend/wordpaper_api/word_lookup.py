from dataclasses import dataclass
import json
from typing import Any, Callable, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class WordNotFoundError(LookupError):
    pass


class WordLookupUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class DictionaryEntry:
    word: str
    transcription: str | None
    part_of_speech: str | None
    language: str
    definition: str
    origin: str | None
    source_name: str
    source_url: str


class DictionaryProvider(Protocol):
    def lookup(self, word: str, language: str = "en") -> DictionaryEntry: ...


class FreeDictionaryProvider:
    """Adapter for dictionaryapi.dev.

    Keeping the external response parsing here means the API and studio do not
    depend on this particular dictionary provider.
    """

    base_url = "https://api.dictionaryapi.dev/api/v2/entries"
    source_url = "https://dictionaryapi.dev/"

    def __init__(self, opener: Callable[..., Any] = urlopen) -> None:
        self._opener = opener

    def lookup(self, word: str, language: str = "en") -> DictionaryEntry:
        normalized_word = word.strip()
        if not normalized_word:
            raise WordNotFoundError("Enter a word first")
        if language != "en":
            raise WordNotFoundError("Automatic lookup currently supports English")

        url = f"{self.base_url}/{quote(language)}/{quote(normalized_word)}"
        request = Request(url, headers={"User-Agent": "wordpaper/0.1"})
        try:
            with self._opener(request, timeout=6) as response:
                payload = json.load(response)
        except HTTPError as error:
            if error.code == 404:
                raise WordNotFoundError(f'No dictionary entry for "{normalized_word}"') from error
            raise WordLookupUnavailableError("Dictionary service returned an error") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise WordLookupUnavailableError("Dictionary service is unavailable") from error

        try:
            entry = payload[0]
            meaning = next(
                item
                for item in entry.get("meanings", [])
                if item.get("definitions")
            )
            definition = meaning["definitions"][0]["definition"]
        except (IndexError, KeyError, StopIteration, TypeError) as error:
            raise WordNotFoundError(f'No usable definition for "{normalized_word}"') from error

        transcription = entry.get("phonetic") or next(
            (
                item.get("text")
                for item in entry.get("phonetics", [])
                if item.get("text")
            ),
            None,
        )
        if transcription and not transcription.startswith(("/", "[")):
            transcription = f"/{transcription}/"

        return DictionaryEntry(
            word=entry.get("word") or normalized_word,
            transcription=transcription,
            part_of_speech=meaning.get("partOfSpeech"),
            language="English",
            definition=definition,
            origin=entry.get("origin"),
            source_name="Free Dictionary API",
            source_url=self.source_url,
        )
