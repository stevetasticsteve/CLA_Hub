# To do

## New features
- User section to see what everyone's worked on
- Export features
- Way to link institutes to realm of reality write up
- Hardcode in CLAHubDev admin login
- label and value tags - enables user extensions without coding - users can add their own fields

## Removing features
- Consider removing tools if more aren't added. CLI jobs could be used instead

## UI improvements
- Editing or removing uploaded pictures (Ajax drag and drop?)
- User friendliness testing
- Make jumbotron minimal_base.html shorter so it fits on screen
- Bilas 404 and 500 pages

## Server improvements
- Paginate the pages that need it. Currently home page only
- Think of 'background' information that can be stored by server that might be helpful for queries
- Improve search
- Submit button on top as well as down below for forms
- Person ID number visible in profile and in list views
- Make a 2nd level of user so Auth isn't open to them on the admin site
- A job handling system is needed. The import function won't work as the process takes longer than 30s and apache times
out. Need to install celery to get that working, and also because if a CE is uploaded with a large picture
and audio it's possible the POST will fail if the upload takes too long.

## Deployment improvements
- Automated install to Raspberry pi script is required or Docker
- Villages in people app are hardcoded to Kovol

## Bugs
- If a CE is titled '3' it clashes with CE pk=3
- Tags can potentially produce None as the slug. django.slugify is used on the tag and '==' will become ''
Added if loops in templates to catch this bug and stop a server error, but the tag will still exit - being
visible on the tags page but unaccessible as it has no slug.
- Audio is replicated on save during tests
- Editing a CE means your user overwrites the last edited by information for texts too,
even if you didn't edit them.
- You can't reuse a picture say for a profile pic and a CE pic.
- Pagination doesn't handle lots and lots of pages elegantly

## Testing
- Functional tests need to be completed.
