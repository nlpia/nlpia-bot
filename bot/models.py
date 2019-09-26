
import logging

from django.db import models


log = logging.getLogger(__name__)


from bot.models_notes import NoteFile, Sentence  # noqa


class Agent(models.Model):
    name = models.TextField()


class State(models.Model):
    """ Context (state of mind, state of the world) of all agents (bots and humans) """
    context_name = models.TextField()
    agent = models.TextField(help_text="Human or bot agent expected to take the next turn or action")


class Action(models.Model):
    """ Probability for a state transition and the action name and parameters associate with that action """
    source = models.ForeignKey(State, related_name='source', on_delete=models.PROTECT)
    dest = models.ForeignKey(State, related_name='dest', on_delete=models.PROTECT)
    probability = models.FloatField(null=True, blank=True, default=1)
    action_name = models.TextField(default='text')
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT,
                              help_text="The human or autonomous agent that can perform this action")
    payload = models.TextField(default='', blank=True, null=True,
                               help_text="parameters of the action, in the case of the aciton 'text' or 'say', just the string to be uttered")


class URL(models.Model):
    url = models.URLField()


class Username(models.Model):
    """ A Username (nick) and span of time over which it was used """
    name = models.TextField(
        blank=False, null=False, default='',
        help_text="Informal name that agent has named themself.")
    active = models.NullBooleanField(blank=True, null=True, default=False)
    last_used = models.DateTimeField(
        null=True,
        help_text="Last time the username was used in a dialog (as a speaker/texter/chatter). " +
                  "null: presumably still being used.")
    first_used = models.DateTimeField()
    url = models.ForeignKey(URL, blank=True, null=True, default=None, on_delete=models.PROTECT)


class Contact(models.Model):
    name = models.TextField(blank=False, null=False, default='',
                            help_text="Informal name that a person prefers to be addressed by in spoken or text dialog.")
    full_name = models.TextField(blank=True, null=False, default='')
    first_name = models.TextField(blank=True, null=False, default='')
    last_name = models.TextField(blank=True, null=False, default='')
    urls = models.ManyToManyField(URL)
    email = models.EmailField(blank=True, null=True, )


class Speaker(models.Model):
    spoken_name = models.TextField(blank=True, null=False, default='')
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.PROTECT)
    bot = models.NullBooleanField(blank=True, null=True, default=False)
    username = models.TextField(blank=True, null=False, default='')
    likelihood = models.FloatField(blank=True, default=1.0, null=False)


class Attribution(models.Model):
    name = models.TextField(blank=True, null=False, default='')
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.PROTECT)
    bibtext = models.TextField(blank=True, null=False, default='')
    license = models.TextField(blank=True, null=False, default='')


class Context(models.Model):
    """ A tag indicating the conversation context """
    name = models.CharField(blank=False, null=False, default='conversation', max_length=255)
    subcontext = models.CharField(blank=True, null=True, max_length=255)
    attribution = models.ForeignKey(Attribution, null=True, blank=True, on_delete=models.PROTECT)


class DialogState(models.Model):
    context = models.ForeignKey(Context, on_delete=models.PROTECT)


class Statement(models.Model):
    """

    See Eisenstein p. 467 for an example of a dialog graph

    ## Refereneces
    - Jacob Eisenstein's https://github.com/jacobeisenstein/gt-nlp-class/raw/master/notes/eisenstein-nlp-notes.pdf
    - nodes don't have statements: https://gamedev.stackexchange.com/a/40524/132464
    - video game dialog tree: https://gamedev.stackexchange.com/a/40522/132464
    """
    state = models.ForeignKey(Context, on_delete=models.PROTECT)
    text = models.TextField(blank=True, null=True)
    reply = models.ForeignKey("self",
                              on_delete=models.PROTECT,
                              verbose_name="statements this is an acceptable reply to",
                              blank=True)
    # contexts = models.ManyToManyField(Context, blank=True)


class Reply(models.Model):
    """ Directed graph edge pointing from the prompting statement to the reply statement """
    # statement = models.ForeignKey(Statement, on_delete=models.PROTECT)
    context = models.ForeignKey(Context, on_delete=models.PROTECT)
    likelihood = models.FloatField(blank=True, default=1.0, null=False)
    speaker = models.ForeignKey(Speaker, null=True, on_delete=models.PROTECT)
