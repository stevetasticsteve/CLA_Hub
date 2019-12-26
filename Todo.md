# To do

## New features
- User section to see what everyone's worked on
- Export features
- Way to link institutes to realm of reality write up
- Search tags
- Search texts
- Hardcode in CLAHubDev admin login
- label and value tags - enables user extensions without coding - users can add their own fields
- tests for people app and imports

## UI improvements
- Editing or removing uploaded pictures (Ajax drag and drop?)
- User friendliness testing
- Make jumbotron minimal_base.html shorter so it fits on screen
- Bilas 404 and 500 pages

## Server improvements
- Paginate texts, alphabetical CEs and tags pages
- Think of 'background' information that can be stored by server that might be helpful for queries
- Form validation for audio files
- Improve search
- Functional tests
- Make a 2nd level of user so Auth isn't open to them on the admin site
- Remove valid for DA Boolean? Covered by phonetic standard. Expand phonetic standard to include orthography?

## Bugs
- auto hyperlink defaults to finding the shortest thing it can, you can't refer to similarly worded CEs of shorter length
- If a CE is titled '3' it clashes with CE pk=3
- case sensitivity in auto cross linking
- Tags can potentially produce None as the slug. django.slugify is used on the tag and '==' will become ''
Added if loops in templates to catch this bug and stop a server error, but the tag will still exit - being
visible on the tags page but unaccessible as it has no slug.

- Edit tests not working now there is example data





