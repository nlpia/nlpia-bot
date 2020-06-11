from qary.skills.glossary_bots import Bot as GlossaryBot
from qary.skills.faq_bots import Bot as FaqBot


class PythonPredictor:
    def __init__(self, config):
        self.model = GlossaryBot()

    def predict(self, payload):
        scored_replies = sorted(self.model.reply(payload["text"]), reverse=True)
        if len(scored_replies) and len(scored_replies[0] > 1):
            return scored_replies[0][1]
        else:
            return f"{self.model.__module__.split('.')[-1].rstrip('s')}.Bot().reply({payload['text']}) returned nothing."


class FaqCortextPredictor:
    def __init__(self, config):
        self.model = FaqBot()

    def predict(self, payload):
        scored_replies = sorted(self.model.reply(payload["text"]), reverse=True)
        if len(scored_replies) and len(scored_replies[0] > 1):
            return scored_replies[0][1]
        else:
            return f"{self.model.__module__.split('.')[-1].rstrip('s')}.Bot().reply({payload['text']}) returned nothing."
