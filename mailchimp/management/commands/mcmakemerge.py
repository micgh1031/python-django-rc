from django.core.management import BaseCommand
from django.contrib.sites.models import Site
from mailchimp.utils import get_connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 1:
            print 'You have to specify exactly one argument to this command'
            return
        merge = args[0]
        print 'Adding the merge var `%s` to all lists' % merge
        c = get_connection()
        for list in c.lists.values():
            print 'Checking list %s' % list.name
            list.add_merges_if_not_exists(merge)
            print '  ok'
        print 'Done'