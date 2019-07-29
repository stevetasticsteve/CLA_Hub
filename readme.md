#CLA Hub#

A Django project to give bush teams a way to collaboratively create and maintain a culture file for learning tribal language and culture.
The software is intended to be run on a Raspberry pi 3 on an internal team network and accessed through a desktop web browser.

##Core features##
- Create web pages to document culture events (CEs)
    - Allow cross linking to other CEs
    - Provides a template for documenting CEs
    - Fields for phonetic and orthographic text
    - Label phonetic text with different levels of accuracy enabling exports of thoroughly checked
      phonetic data to other tools
    - Able to attach/embed audio recordings of vernacular texts
    - Able to attach/embed photos of CEs. Auto compression of pictures for low storage needs.
    - Store CE data in a database format allowing for retrieval and other processing
    - Be able to tag vernacular text with outline of cultural materials (OCM) tags
    - Unanswered questions regarding individual CE that can be gathered summarised

- CE index page
    - Displays most recently modified CEs
    - Able to show alphabetical list of CEs

- OCM summaries
    - Lift tagged vernacular text from CEs and generate summaries of all tags related to that cultural area
    - Be able to export OCM summaries

- Login and authorisation
    - Team members login with unique accounts that track contributions

- Backups
    - Culture file must be easy to back up and retrieve

- Exportable
    - Tools to export all data in useful formats

- Transferable
    - Team members leaving for home assignment need to be able to take a copy home for study


##Possible add-on tools##
- Phonetic to orthographic text auto convert
- Listening collection
- Support for mobile devices
- Meeting minutes and action points
- Lexicon
