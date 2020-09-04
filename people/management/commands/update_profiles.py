from django.core.management.base import BaseCommand

from people.models import Person


class Command(BaseCommand):
    help = '''If a profile\'s name is changed that change won't be reflected in the family field that refers to that 
    record. The solution is to schedule CLAHub to trigger the save function for all profiles periodically. '''

    def handle(self, **options):
        """Updates the profiles by running the save command. This will update hyperlinks in the family field
        to reflect name changes"""
        for profile in Person.objects.all():
            profile.save()
        self.stdout.write(self.style.SUCCESS('All records updated'))
