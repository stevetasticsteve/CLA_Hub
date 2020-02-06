# To do

## New features
- User section to see what everyone's worked on
- Export features
- Way to link institutes to realm of reality write up
- Search tags
- Search texts
- Search people
- Hardcode in CLAHubDev admin login
- label and value tags - enables user extensions without coding - users can add their own fields
- tests for imports

## UI improvements
- Editing or removing uploaded pictures (Ajax drag and drop?)
- User friendliness testing
- Make jumbotron minimal_base.html shorter so it fits on screen
- Bilas 404 and 500 pages
- html title. Code an if into base template so a view can pass a title, otherwise read CLAHub

## Server improvements
- Paginate texts, alphabetical CEs and tags pages
- Think of 'background' information that can be stored by server that might be helpful for queries
- Improve search
- Functional tests
- Make a 2nd level of user so Auth isn't open to them on the admin site

## Deployment improvements
- Automated install to Raspberry pi script is required
- Villages in people app are hardcoded to Kovol
- server_url in PodcastFeed is hardcoded to 192.168.0.100. Spent days trying to figure out how to get Django to give me the host.
It's possible through a request but the django Feeds seems to ditch the request. Some magic is happening in url.paths, but I can't
get it to pass the request through to the Feed class so it can pull the host from the request.

## Bugs
- auto hyperlink defaults to finding the shortest thing it can, you can't refer to similarly worded CEs of shorter length
- If a CE is titled '3' it clashes with CE pk=3
- case sensitivity in auto cross linking
- Tags can potentially produce None as the slug. django.slugify is used on the tag and '==' will become ''
Added if loops in templates to catch this bug and stop a server error, but the tag will still exit - being
visible on the tags page but unaccessible as it has no slug.
- Can't add a question to the Example CE for some reason (can edit)
- Audio is replicated on save during tests
- Can't save more than one question when there is more than one text
- Editing a CE means your user overwrites the last edited by information for texts too,
even if you didn't edit them.
- Repeated digits cause clashes in people family auto linking. 5 and 359 won't play nicely together
as the replace operation replaces the match of 5 within 359





