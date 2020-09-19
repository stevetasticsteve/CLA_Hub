import bleach

culture_events_shown_on_home_page = 10
# If auto_cross_reference = True program will scan description field for url slugs whenever that
# CE is saved. If it finds a matching slug in the description it will add a hyperlink
# If False hyperlinks will only be added to valid slugs within curly brackets {}
auto_cross_reference = True

# A list of allowed HTML tags the user can enter to HTML escaped fields.
bleach_allowed = ['strong', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6' 'li', 'ul',
                  'tr', 'th', 'td', 'thead', 'tbody', 'table', 'div']
bleach_attributes_allowed = {'table': 'class', 'div': 'class'}


def clean_html(html):
    return bleach.clean(str(html))#,
                        # tags=bleach_allowed,
                        # attributes=bleach_attributes_allowed,
                        # strip=False)
    # return html
