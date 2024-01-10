# To do

## Bugs
- If a CE is titled '3' it clashes with CE pk=3
- Tags can potentially produce None as the slug. django.slugify is used on the tag and '==' will become ''
Added if loops in templates to catch this bug and stop a server error, but the tag will still exit - being
visible on the tags page but unaccessible as it has no slug.
- Audio is replicated on save during tests
- Editing a CE means your user overwrites the last edited by information for texts too,
even if you didn't edit them.
- You can't reuse a picture say for a profile pic and a CE pic.
- Management commands overwrite all date information


11/1/24
- None shows in last modified when new word made
- Libre office export
- Hitting return on the search bar refreshes the page
- Spelling variations not included in spell check exports