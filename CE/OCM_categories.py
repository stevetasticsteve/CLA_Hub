import re
import taggit.utils
from django.utils.text import slugify

OCM_categories = ['1 Material institution',
                  '2 Kinship institution',
                  '3 Social institution',
                  '4 Art and play institution',
                  '5 Religious institution',
                  '6 Judicial institution',
                  '7 Economic institution',
                  '8 Education institution',
                  '9 Political institution'
]

OCM_sub_categories = [
    ['1-1 Geography & Weather',
    '1-2 Settlements & Communities',
    '1-3 Roads & Traffic',
    '1-4 Structures & Buildings',
    '1-5 Furniture & Appliances',
    '1-6 Energy; Power & Fire',
    '1-7 Food & Drink',
    '1-8 Gardening & Gathering',
    '1-9 Hunting & Fishing',
    '1-10 Farming & Ranching',
    '1-11 Clothing & Adornment',
    '1-12 Vehicles & Machines',
    '1-13 Tools & Instruments',
    '1-14 Plants & Animals',
    '1-15 Sky Land & Water'],
    ['2-1 Terminology & Relationships',
    '2-2 Family & Clan',
    '2-3 Grandparents & Grandchildren',
    '2-4 Tribe & Nation',
    '2-5 Outsiders & Non-relatives'],
    ['3-1 History & Trends',
    '3-2 Identity & Pride',
    '3-3 Marriage & Family',
    '3-4 Interpersonal & Social Relationships',
    '3-5 National & Global Relationships',
    '3-6 Communication & Conversation',
    '3-7 Words & Language',
    '3-8 Health & Sickness',
    '3-9 Birth & Dying',
    '3-10 Burial & Funeral Practices',
    '3-11 Mourning & Adjustment to Death',
    '3-12 Suicide & Unnatural Death',
    '3-13 Cult of the Dead & After Death',
    '3-14 Sex & Reproduction',
    '3-15 Social Problems & Issues',
    '3-16 Heroes & Villains',
    '3-17 Celebrations; Rites & Initiations',
    '3-18 Fights; Antagonisms & Battles',
    '3-19 Infant Care & Childhood',
    '3-20 Instilling of Norms and Customs',
    '3-21 Social Stratification & Status',
    '3-22 Daily & Cyclic Routines',
    '3-23 Rest; Vacations & Holidays',
    '3-24 Humor & Wit',
    '3-25 Etiquette & Ethics',
    '3-26 Cliques & Groups',
    '3-27 Drivers & Emotions',
    '3-28 Behavior Modifications',
    '3-29 Travel & Relocation',
    '3-30 Social Media & Internet'],
    ['4-1 Music & Musical Instruments',
    '4-2 Games & Hobbies',
    '4-3 Sports & Physical Recreation',
    '4-4 Radio & Television',
    '4-5 Film & Theatre',
    '4-6 Night Life & Night Clubs',
    '4-7 Decorative Art & Crafts',
    '4-8 Dance & Party',
    '4-9 Literature & Poetry',
    '4-10 Oratory & Speeches'],
    ['5-1 Gods & Spirits',
    '5-2 Cosmology & Mythology',
    '5-3 Sacred Objects & Places',
    '5-4 Dreams & Visions',
    '5-5 Luck & Chance',
    '5-6 Prayers & Sacrifices',
    '5-7 Purification & Atonement',
    '5-8 Divination & Revelation',
    '5-9 Avoidance & Taboo',
    '5-10 Rituals & Ceremonies',
    '5-11 Miracles & Magic',
    '5-12 Theological Systems & Disputes',
    '5-13 Tolerance & Intolerance',
    '5-14 Denominations & Sects',
    '5-15 Non-human Beings & Sacred Critters',
    '5-16 Leaders & Controllers'],
    ['6-1 Offenses & Crimes',
    '6-2 Contracts & Agreements',
    '6-3 Standard Procedures & Legal Norms',
    '6-4 Personnel & Authorities',
    '6-5 Initiation & Execution of Justice'],
    ['7-1 Raw Materials for Production',
    '7-2 Personal & Communal Property',
    '7-3 Human & Financial Capital',
    '7-4 Business & Employment',
    '7-5 Labor & Occupation Issues',
    '7-6 Wages & Salaries',
    '7-7 Borrowing & Lending',
    '7-8 Renting & Leasing',
    '7-9 Giving & Receiving',
    '7-10 Inheritance & Birthright',
    '7-11 Welfare & Assistance',
    '7-12 Industry; Manufacturing & Production',
    '7-13 Buying; Selling & Consuming',
    '7-14 Distribution & Delivery of Goods',
    '7-15 Saving & Investing'],
    ['8-1 Theory & Methods of Education',
    '8-2 Culture & Social Norm Education',
    '8-3 Life Skills & Vocational Education',
    '8-4 Elementary & Higher Education',
    '8-5 Teacher & Student Issues/Relationships'],
    ['9-1 Form & Rules of Government',
    '9-2 Activities & Extent of Government',
    '9-3 Councils & Ruling Officials',
    '9-4 Police & Social Control',
    '9-5 Political Parties & Groups',
    '9-6 Citizen & Non-citizen Criteria/Relations',
    '9-7 Taxation & Public Benefits',
    '9-8 Elections & Exploitations',
    '9-9 Military Affairs',
    '9-10 Coups & Revolution']
]


def _OCM_all_categories():
    # provides a simple list of all the subcategories
    categories = []
    for level1 in OCM_sub_categories:
        for level2 in level1:
            categories.append(level2)
    return categories

def _OCM_slug_dictionary():
    # provides a dictionary where the key 1-1 refers to the value Geography & Weather
    # allows looking up of short codes and matching category titles
    # {'1-1': 'Geography & Weather}
    ocm_codes = re.findall(r'\d+.\d+', str(OCM_sub_categories))
    slug_codes = [code.replace('.', '-') for code in ocm_codes]
    categories = []
    for category in OCM_sub_categories:
        for subcategory in category:
            r = re.search(r'\d+.\d+ ', subcategory)
            categories.append(subcategory[r.end():])
    return dict(zip(slug_codes, categories)), ocm_codes


_slugs, _codes = _OCM_slug_dictionary()


def Generate_OCM():
    # provides a list of dictionaries that represent the OCM model
    # [{'code':'1-1', 'name':'1-1 Geography & Weather', 'slug': '1-1-geography-weather'}]
    OCM_list = []
    for i, institution in enumerate(OCM_sub_categories):
        institution_list = []
        for OCM_category in institution:
            institution_list.append({'code': re.search(r'\d+.\d+', OCM_category).group(),
                                     'slug': slugify(OCM_category),
                                     'name': OCM_category})
        OCM_list.append(institution_list)
    return OCM_list


OCM = Generate_OCM()
categories = _OCM_all_categories()


def check_tags_for_OCM(tagstring):
    # adds to django.Taggits parse tags function by checking for OCM tags, and if found
    # extends them automatically to include the title.
    tags = taggit.utils._parse_tags(tagstring)
    for i, tag in enumerate(tags):
        if tag in _slugs:
            tags[i] = tag + ' ' + _slugs[tag]
    return tags