from django.core.management.base import BaseCommand

from CE.models import CultureEvent


class Command(BaseCommand):
    help = '''If a CE\'s name is changed that change won't be reflected in the any automatic hyperlinks added to the
    description field. The solution is to schedule CLAHub to trigger the save function for all events periodically.
    Trigger via crontab using: source venv/bin/activate && python manage.py update_events'''

    def handle(self, **options):
        """Updates the profiles by running the save command. This will update hyperlinks in the family field
        to reflect name changes"""
        for event in CultureEvent.objects.all():
            event.save()
        self.stdout.write(self.style.SUCCESS('All Culture events updated'))
