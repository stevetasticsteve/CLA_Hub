from django.core.cache import cache
from lexicon import models

import os
from zipfile import ZipFile


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

    Also adds attributes that are helpful to the spell checker. If Matat filter is true Matat data is output
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


def get_word_list(checked=True):
    """Get all words from the lexicon.
    Returns a list in alphabetical order."""
    word_objs = get_db_models(matat_filter=False)
    words = []
    for w in word_objs:
        if w.type == "word":
            # skip unchecked words when required
            if checked:
                if not w.checked:
                    continue
            words.append(w.kgu)
            # automatically append spelling variations
            spelling_variations = models.KovolWordSpellingVariation.objects.filter(
                word=w
            )
            if spelling_variations:
                for s in spelling_variations:
                    words.append(s.spelling_variation)
        elif w.type == "verb":
            words += w.get_conjugations(checked)
            spelling_variations = models.VerbSpellingVariation.objects.filter(verb=w)
            if spelling_variations:
                for s in spelling_variations:
                    words.append(s.spelling_variation)
    return [w for w in words if w]


def write_dic_file():
    """Write the .dic file used in Hunspell."""
    words = get_word_list(checked=True)
    # write a new .dic file in
    dic_file = os.path.join("lexicon", "oxt_extension", "dictionaries", "kgu_PG.dic")
    with open(dic_file, "w") as file:
        file.write(str(len(words)))
        file.writelines([f"\n{w}" for w in words])


def update_oxt_version():
    """Update the spell check version number to match CLAHub."""
    try:
        version = models.LexiconMetaData.objects.get(pk=1).version
    except models.LexiconMetaData.DoesNotExist:
        models.LexiconMetaData.objects.create()
        version = models.LexiconMetaData.objects.get(pk=1).version

    with open("lexicon/oxt_extension/description_template.xml", "r") as file:
        contents = file.read()
    with open("lexicon/oxt_extension/description.xml", "w") as file:
        file.write(contents.replace("$VERSION", str(version)))
    return version


def write_oxt_package():
    """Zip together the hunspell spellcheck as a .oxt file."""
    write_dic_file()
    version = update_oxt_version()
    # zip the relevent files together
    zip_path = os.path.join("data", f"kovol_spellcheck_{version}.oxt")
    contents_path = os.path.join("lexicon", "oxt_extension")
    contents = []
    [contents.append(os.path.join(contents_path, f)) for f in os.listdir(contents_path)]
    [
        contents.append(os.path.join(contents_path, "dictionaries", f))
        for f in os.listdir(os.path.join(contents_path, "dictionaries"))
    ]
    contents.append(os.path.join(contents_path, "META-INF", "manifest.xml"))

    with ZipFile(zip_path, "w") as myzip:
        for c in contents:
            myzip.write(c, arcname=c.lstrip(contents_path))
    return zip_path
