def score(reply, stmt=None, **kwargs):
    if kwargs is None or kwargs['sentiment_analyzer'] is None:
        return 0.0

    return 1.0 if kwargs['sentiment_analyzer'].polarity_scores(reply)['compound'] > -0.5 else 0.0
