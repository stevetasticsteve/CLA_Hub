from django.core.cache import cache
from lexicon import models


def get_lexicon_words_from_cache(matat_filter=False):
    lexicon_words = cache.get("lexicon_words")

    if lexicon_words:
        return lexicon_words

    elif not lexicon_words:
        lexicon_entries = get_db_models(matat_filter)
        cache.set("lexicon", lexicon_entries)
        cache.set("lexicon_words", [w for w in lexicon_entries if w.type != "phrase"])
        return cache.get("lexicon_words")


def get_db_models(matat_filter):
    """Query database and return Kovol words and verbs in alphabetical order.

    Also adds attributes that are helpful to the spell checker.
    """
    if matat_filter:
        words = models.KovolWord.objects.exclude(matat__isnull=True)
        verbs = models.MatatVerb.objects.all()
        phrases = models.PhraseEntry.objects.exclude(matat__isnull=True)
    else:
        words = models.KovolWord.objects.all()
        verbs = models.ImengisVerb.objects.all()
        phrases = models.PhraseEntry.objects.all()

    for w in words:
        w.type = "word"
        # add spelling variations to list for spell checking
        w.variations = [
            word.spelling_variation
            for word in models.KovolWordSpellingVariation.objects.filter(word=w)
        ]

    for v in verbs:
        v.type = "verb"
        # add conjugations and spelling variations for spell checking
        v.conjugations = v.get_conjugations()
        variations = models.VerbSpellingVariation.objects.filter(verb=v)
        if variations:
            v.conjugations += [v.spelling_variation for v in variations]
    for p in phrases:
        p.type = "phrase"

    if matat_filter:
        for w in words:
            w.kgu = w.matat
        for v in verbs:
            v.pk = v.imengis_verb.pk
        for p in phrases:
            p.kgu = p.matat

    words_queryset = sorted(
        [w for w in words] + [v for v in verbs], key=lambda x: str(x)
    )
    cache.set("words_queryset", words_queryset)

    lexicon = [w for w in words] + [v for v in verbs] + [p for p in phrases]

    return sorted(lexicon, key=lambda x: str(x))
