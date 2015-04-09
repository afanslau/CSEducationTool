from django.core.management.base import BaseCommand
from stackoverflow.graphrecs import KnowdGraph
from django.db.models import Q
import datetime

class Command(BaseCommand):

	help = 'Loads wikipedia topics from the api'
	def handle(self, *args, **options):
		kg_train = KnowdGraph(Q(creation_date__lt=datetime.datetime(2010,2,1)))
		kg_test = KnowdGraph(vocab=kg_train.vocab)

