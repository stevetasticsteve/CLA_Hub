from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from lexicon import models

import os
import csv
import datetime

conjugation_codes = {
    "past_1s": "1sp",
    "past_2s": "2sp",
    "past_3s": "3sp",
    "past_1p": "1pp",
    "past_2p": "2pp",
    "past_3p": "3pp",
    "present_1s": "1spr",
    "present_2s": "2spr",
    "present_3s": "3spr",
    "present_1p": "1ppr",
    "present_2p": "2ppr",
    "present_3p": "3ppr",
    "future_1s": "1sf",
    "future_2s": "2sf",
    "future_3s": "3sf",
    "future_1p": "1pf",
    "future_2p": "2pf",
    "future_3p": "3pf",
    "sg_imp": "simp",
    "pl_imp": "pimp",
    "enclitic_same_actor": "saen",
    "enclitic_1s": "1sen",
    "enclitic_1p": "1pen",
    "enclitic_2s": "2sen",
    "enclitic_2p": "2pen",
    "nominalizer": "nom",
}


class Command(BaseCommand):
    help = "import lexicon data from csv"

    def import_words(self, write=True):
        with open(os.path.join("data", "Kovol_lexicon.csv")) as file:
            data = [row for row in csv.DictReader(file)]

        data = [d for d in data if d["ID"]]
        for d in data:
            d["Kovol"] = d["Kovol"].rstrip(" ")

        phrases = [p for p in data if " " in p["Kovol"]]
        words = [w for w in data if " " not in w["Kovol"]]
        words = [w for w in words if w["POS"] != "v"]

        words = sorted(words, key=lambda x: int(x["ID"]))

        errors = 0
        rows = 0
        last_id = "0"
        for w in words:
            id = w["ID"]

            if w["Matat"] == "n/a":
                w["Matat"] = w["Kovol"]

            if w["Matat"]:
                matat = w["Matat"]
            else:
                matat = None

            try:
                date = datetime.datetime.strptime(w["Date"], "%d/%m/%y")
            except ValueError:
                date = datetime.date.today()

            if w["Checked"]:
                checked = True
            else:
                checked = False

            pos = w["POS"]
            if pos == "ass actr":
                pos = "rel"
            elif pos == "" or pos.lower() == "np":
                pos = "uk"

            if w["Example"]:
                comment = f'{w["Definition"]}, Example: {w["Example"]}'
            else:
                comment = w["Definition"]

            english = w["English"].split(", ")

            if id == last_id:
                try:
                    new_sense = models.KovolWordSense(
                        word=models.KovolWord.objects.get(kgu=w["Kovol"]),
                        sense=w["English"],
                    )
                    new_sense.full_clean()
                    if write:
                        new_sense.save()
                except models.KovolWord.DoesNotExist:
                    print(
                        f"An ID number looks like it doesn't match a sense. {id}, {w['Kovol']}"
                    )
                except ValidationError as e:
                    print(e)
            else:
                try:
                    new_word = models.KovolWord(
                        kgu=w["Kovol"],
                        eng=english[0],
                        tpi=w["Tok Pisin"],
                        comments=comment,
                        matat=matat,
                        created=date,
                        checked=checked,
                        modified_by="Importer",
                        pos=pos,
                    )

                    try:
                        new_word.full_clean()

                    except ValidationError as e:
                        if len(e.error_dict) == 1 and e.error_dict.get("tpi"):
                            pass
                        else:
                            print(f"validation error: {e} \nrow={w}\n\n")
                            errors += 1
                    if write:
                        new_word.save()

                    if len(english) > 1 and write:
                        for sense in english[1:]:
                            new_sense = models.KovolWordSense(
                                word=models.KovolWord.objects.get(kgu=w["Kovol"]),
                                sense=sense,
                            )
                            new_sense.save()
                except IntegrityError:
                    print(f"repeated word: ID: {w['ID']} {w['Kovol']}")

            last_id = id
            rows += 1
        print(f"{rows} words, {errors} errors")

        for p in phrases:
            try:
                date = datetime.datetime.strptime(p["Date"], "%d/%m/%y")
            except ValueError:
                date = datetime.date.today()

            if p["Example"]:
                comment = f'{p["Definition"]}, Example: {p["Example"]}'
            else:
                comment = p["Definition"]

            new_phrase = models.PhraseEntry(
                kgu=p["Kovol"],
                matat=p["Matat"],
                eng=p["English"],
                tpi=p["Tok Pisin"],
                comments=comment,
                created=date,
                modified_by="Importer",
            )
            try:
                new_phrase.full_clean()
            except ValidationError as e:
                if len(e.error_dict) == 1 and e.error_dict.get("linked_word"):
                    pass
                else:
                    print(f"validation error: {e} \nrow={p}\n\n")
            if write:
                try:
                    new_phrase.save()
                except IntegrityError:
                    new_sense = models.PhraseSense(
                        phrase=models.PhraseEntry.objects.get(kgu=p["Kovol"]),
                        sense=p["English"],
                    )
                    if write:
                        new_sense.save()
                    print(f"repeated phrase {p['Kovol']}")

    def import_verbs(self, write=True):
        with open(os.path.join("data", "Kovol_verbs.csv")) as file:
            data = [row for row in csv.DictReader(file)]

        data = sorted(data, key=lambda x: x["English"])
        english_verbs = set([v["English"] for v in data])

        for verb in english_verbs:
            conjugations = [v for v in data if verb == v["English"]]
            conjugation_dict = {}
            variations = []
            for c in conjugations:
                if c["Checked"]:
                    checked = True
                else:
                    checked = False

                kgu = c["Kovol"].split(" ")[0]

                english = c["English"].split(", ")
                eng = english[0]
                sense = english[1:]

                if not c["Mode"]:
                    key = f"{c['Tense']}_{c['Person']}"
                    conjugation_dict[key] = kgu
                    conjugation_dict[f"{key}_checked"] = checked

                elif c["Mode"] == "imperative":
                    if c["Person"] == "2s":
                        key = "sg_imp"
                        conjugation_dict[key] = kgu
                        conjugation_dict[f"{key}_checked"] = checked

                    elif c["Person"] == "2p":
                        key = "pl_imp"
                        conjugation_dict[key] = kgu
                        conjugation_dict[f"{key}_checked"] = checked

                elif c["Mode"] == "nominalizer":
                    key = "nominalizer"
                    conjugation_dict[key] = kgu
                    conjugation_dict[f"{key}_checked"] = checked

                elif c["Mode"] == "enclitic":
                    if c["Person"]:
                        key = f"enclitic_{c['Person']}"
                        conjugation_dict[key] = kgu
                        conjugation_dict[f"{key}_checked"] = checked
                    else:
                        key = "enclitic_same_actor"
                        conjugation_dict["enclitic_same_actor"] = kgu
                        conjugation_dict[f"{key}_checked"] = checked

                    if len(c["Kovol"].split(" ")) > 1:
                        v = c["Kovol"].split(" ")[1:]
                        variations.append((key, v))
            new_verb = models.ImengisVerb(
                eng=eng,
                created=datetime.date.today(),
                modified_by=c["Author"],
                tpi="",
            )
            new_verb.__dict__.update(conjugation_dict)
            try:
                new_verb.full_clean()
            except ValidationError as e:
                if len(e.error_dict) == 1 and e.error_dict.get("tpi"):
                    pass
                else:
                    print(f"validation error: {e} \nrow={c}\n\n")
            if write:
                new_verb.save()
                if sense:
                    for s in sense:
                        models.VerbSense.objects.create(verb=new_verb, sense=s)
                if variations:
                    for v in variations:
                        models.VerbSpellingVariation.objects.create(
                            verb=new_verb,
                            spelling_variation=v[1][0],
                            conjugation=conjugation_codes[v[0]],
                        )

    def import_check_list(self, write=True):
        with open(os.path.join("data", "check_list.csv")) as file:
            data = [row for row in csv.DictReader(file)]

        unmatched = []
        for d in data:
            found = False

            if d["Stanley spelling"]:
                stanley = f"Stanley: {d['Stanley spelling']} "
            else:
                stanley = ""

            if d["Hansen spelling"]:
                hansen = f"Hansen: {d['Hansen spelling']} "
            else:
                hansen = ""

            if d["Stous spelling"]:
                stous = f"Stous: {d['Stous spelling']} "
            else:
                stous = ""

            review_comments = stanley + hansen + stous
            orth = d["Orthography"]

            try:
                word = models.KovolWord.objects.get(kgu=orth)
                word.review = 1
                word.review_comments = review_comments
                word.review_time = datetime.date.today()
                word.review_user = "importer"
                word.save()
            except models.KovolWord.DoesNotExist:
                try:
                    phrase = models.PhraseEntry.objects.get(kgu=orth)
                    phrase.review = 1
                    phrase.review_comments = review_comments
                    phrase.review_time = datetime.date.today()
                    phrase.review_user = "importer"
                    phrase.save()
                except models.PhraseEntry.DoesNotExist:

                    for verb in models.ImengisVerb.objects.all():
                        conjugations = verb.get_conjugations()

                        if orth in conjugations:
                            verb.review = 1
                            verb.review_comments = review_comments
                            verb.review_time = datetime.date.today()
                            verb.review_user = "importer"
                            verb.save()
                            found = True
                            break
                    if not found:
                        unmatched.append(d)
                        print(f"didn't find {orth}")

        with open(os.path.join("data", "umnatched.csv"), "w") as file:
            fieldnames = list(unmatched[0].keys())
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unmatched)

    def handle(self, *args, **options):
        self.stdout.write("Importing")
        self.import_verbs(write=True)
        self.import_words(write=True)
        self.import_check_list()
