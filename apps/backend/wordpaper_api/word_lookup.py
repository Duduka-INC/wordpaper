from dataclasses import dataclass
import json
import re
from typing import Any, Callable, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
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
    source_license: str


class DictionaryProvider(Protocol):
    def lookup(self, word: str, language: str = "en") -> DictionaryEntry: ...


def detect_language(word: str) -> str:
    return "ru" if re.search(r"[А-Яа-яЁё]", word) else "en"


class DictionaryRouter:
    def __init__(self, providers: dict[str, DictionaryProvider]) -> None:
        self._providers = providers

    def lookup(self, word: str, language: str = "auto") -> DictionaryEntry:
        selected_language = detect_language(word) if language == "auto" else language
        provider = self._providers.get(selected_language)
        if provider is None:
            raise WordNotFoundError(
                f'Automatic lookup does not support language "{selected_language}"'
            )
        return provider.lookup(word, selected_language)


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
            source_license="CC BY-SA 3.0 / GFDL",
        )


class RussianWiktionaryProvider:
    """Extract a compact Russian entry from the Russian Wiktionary API."""

    base_url = "https://ru.wiktionary.org/w/api.php"
    source_name = "Русский Викисловарь"

    _parts_of_speech = (
        "Существительное",
        "Прилагательное",
        "Глагол",
        "Наречие",
        "Местоимение",
        "Числительное",
        "Причастие",
        "Деепричастие",
        "Предлог",
        "Союз",
        "Частица",
        "Междометие",
    )

    def __init__(self, opener: Callable[..., Any] = urlopen) -> None:
        self._opener = opener

    def lookup(self, word: str, language: str = "ru") -> DictionaryEntry:
        normalized_word = word.strip()
        if not normalized_word:
            raise WordNotFoundError("Сначала введите слово")
        if language != "ru":
            raise WordNotFoundError("Этот словарь поддерживает русский язык")

        query = urlencode(
            {
                "action": "query",
                "prop": "extracts",
                "explaintext": "1",
                "redirects": "1",
                "format": "json",
                "titles": normalized_word,
            }
        )
        request = Request(
            f"{self.base_url}?{query}",
            headers={"User-Agent": "wordpaper/0.1 (dictionary lookup)"},
        )
        try:
            with self._opener(request, timeout=8) as response:
                payload = json.load(response)
        except HTTPError as error:
            if error.code == 404:
                raise WordNotFoundError(
                    f'В словаре нет статьи для слова «{normalized_word}»'
                ) from error
            raise WordLookupUnavailableError("Викисловарь вернул ошибку") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise WordLookupUnavailableError("Викисловарь сейчас недоступен") from error

        pages = payload.get("query", {}).get("pages", {})
        page = next(iter(pages.values()), {})
        extract = page.get("extract", "")
        if not extract or page.get("missing") is not None:
            raise WordNotFoundError(
                f'В словаре нет статьи для слова «{normalized_word}»'
            )

        russian_section = self._section(extract, "Русский", level=1)
        definition_section = self._section(russian_section, "Значение", level=4)
        definition = self._first_definition(definition_section)
        if not definition:
            raise WordNotFoundError(
                f'В статье «{normalized_word}» не найдено определение'
            )

        pronunciation_section = self._section(
            russian_section, "Произношение", level=3
        )
        transcription_match = re.search(r"МФА:[^\[]*(\[[^\]]+\])", pronunciation_section)
        transcription = transcription_match.group(1) if transcription_match else None
        part_of_speech = next(
            (
                name.lower()
                for name in self._parts_of_speech
                if re.search(rf"\b{re.escape(name)}\b", russian_section)
            ),
            None,
        )
        etymology = self._first_content_line(
            self._section(russian_section, "Этимология", level=3)
        )

        return DictionaryEntry(
            word=page.get("title") or normalized_word,
            transcription=transcription,
            part_of_speech=part_of_speech,
            language="Русский",
            definition=definition,
            origin=etymology,
            source_name=self.source_name,
            source_url=f"https://ru.wiktionary.org/wiki/{quote(normalized_word)}",
            source_license="CC BY-SA 4.0 / GFDL",
        )

    @staticmethod
    def _section(text: str, title: str, level: int) -> str:
        marks = "=" * level
        pattern = rf"(?ms)^\s*{marks}\s*{re.escape(title)}\s*{marks}\s*$\n?(.*?)(?=^\s*{marks}[^=].*?{marks}\s*$|\Z)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _first_content_line(text: str) -> str | None:
        return next((line.strip() for line in text.splitlines() if line.strip()), None)

    @classmethod
    def _first_definition(cls, text: str) -> str | None:
        line = cls._first_content_line(text)
        if line is None:
            return None
        definition = line.split("◆", 1)[0].strip()
        return definition or None
