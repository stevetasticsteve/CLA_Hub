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
- A job handling system is needed. The import function won't work as the process takes longer than 30s and apache times
out. Need to install celery to get that working, and also because if a CE is uploaded with a large picture
and audio it's possible the POST will fail if the upload takes too long.
- Check through the generated HTML for unclosed tags or extra closing tags

## Deployment improvements
- Automated install to Raspberry pi script is required
- Villages in people app are hardcoded to Kovol
- server_url in PodcastFeed is hardcoded to 192.168.0.100. Spent days trying to figure out how to get Django to give me the host.
It's possible through a request but the django Feeds seems to ditch the request. Some magic is happening in url.paths, but I can't
get it to pass the request through to the Feed class so it can pull the host from the request.

## Bugs
- If a CE is titled '3' it clashes with CE pk=3
- Tags can potentially produce None as the slug. django.slugify is used on the tag and '==' will become ''
Added if loops in templates to catch this bug and stop a server error, but the tag will still exit - being
visible on the tags page but unaccessible as it has no slug.
- Audio is replicated on save during tests
- Editing a CE means your user overwrites the last edited by information for texts too,
even if you didn't edit them.

## Testing
- Functional tests need to be written, especially as bugs with the JS and complex form factories used in
the CE form tend to be overlooked in Django test cases.
