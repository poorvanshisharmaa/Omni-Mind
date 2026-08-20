from __future__ import annotations

import re

# Small curated lexicon for a handful of demo language pairs. This is a
# stand-in for a real MT model (Qwen2.5 / NLLB per the spec) — word-level
# substitution only, no grammar, no context. Swap `LexiconTranslationEngine`
# for a real model behind the same `TranslationEngine` interface.
_LEXICON: dict[str, dict[str, str]] = {
    "hi": {
        "meeting": "baithak", "decision": "faisla", "action": "karya", "risk": "jokhim",
        "deadline": "samay-seema", "owner": "zimmedar", "approved": "manzoor",
        "budget": "bajat", "client": "grahak", "report": "report", "team": "team",
        "week": "hafta", "month": "mahina", "yes": "haan", "no": "nahin",
        "please": "kripya", "thank": "dhanyavaad", "hello": "namaste",
    },
    "fr": {
        "meeting": "réunion", "decision": "décision", "action": "action", "risk": "risque",
        "deadline": "échéance", "owner": "responsable", "approved": "approuvé",
        "budget": "budget", "client": "client", "report": "rapport", "team": "équipe",
        "week": "semaine", "month": "mois", "yes": "oui", "no": "non",
        "please": "s'il vous plaît", "thank": "merci", "hello": "bonjour",
    },
    "es": {
        "meeting": "reunión", "decision": "decisión", "action": "acción", "risk": "riesgo",
        "deadline": "fecha límite", "owner": "responsable", "approved": "aprobado",
        "budget": "presupuesto", "client": "cliente", "report": "informe", "team": "equipo",
        "week": "semana", "month": "mes", "yes": "sí", "no": "no",
        "please": "por favor", "thank": "gracias", "hello": "hola",
    },
    "ja": {
        "meeting": "会議", "decision": "決定", "action": "アクション", "risk": "リスク",
        "deadline": "締め切り", "owner": "担当者", "approved": "承認済み",
        "budget": "予算", "client": "クライアント", "report": "レポート", "team": "チーム",
        "week": "週", "month": "月", "yes": "はい", "no": "いいえ",
        "please": "お願いします", "thank": "ありがとう", "hello": "こんにちは",
    },
}

_WORD_RE = re.compile(r"[A-Za-z']+")


class TranslationEngine:
    def translate(self, text: str, source_lang: str, target_lang: str, glossary: set[str] | None = None) -> str:
        raise NotImplementedError


class LexiconTranslationEngine(TranslationEngine):
    """Word-level dictionary substitution for a handful of demo languages.

    Not a real MT model — no grammar, no context, unknown words pass
    through unchanged. Genuinely honors the glossary lock (locked terms are
    never substituted) and genuinely produces different output per target
    language. Swap for a real Qwen2.5/NLLB call behind this same interface.
    """

    def translate(self, text: str, source_lang: str, target_lang: str, glossary: set[str] | None = None) -> str:
        glossary_lower = {g.lower() for g in (glossary or set())}
        table = _LEXICON.get(target_lang.lower())
        if not table:
            return text  # unsupported pair: pass through untranslated, honestly

        def replace(match: re.Match) -> str:
            word = match.group(0)
            if word.lower() in glossary_lower:
                return word  # glossary lock: never translate these
            translated = table.get(word.lower())
            if translated is None:
                return word
            return translated.capitalize() if word[0].isupper() else translated

        return _WORD_RE.sub(replace, text)


def get_translation_engine() -> TranslationEngine:
    return LexiconTranslationEngine()
