import os
from django.core.management.base import BaseCommand
from cake.models import*
from django.core.files import File


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        pass