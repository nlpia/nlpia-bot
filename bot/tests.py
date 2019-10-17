import os
from django.test import TestCase

from django.utils import timezone
from django.core.urlresolvers import reverse  # noqa
from bot.forms import ChatForm  # noqa

from bot.models_notes import NoteFile


class ChatTest(TestCase):

    def create_note(self, path="/midata/private/journal/test_note.md"):
        return NoteFile.objects.create(dir=os.path.dirname(path), file=os.path.basename(path), created_at=timezone.now())

    def test_note_creation(self):
        note = self.create_note()
        self.assertTrue(isinstance(note, NoteFile))
        self.assertEqual(note.__unicode__(), note.dir)
