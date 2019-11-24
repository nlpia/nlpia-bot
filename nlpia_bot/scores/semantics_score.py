def semantics(reply, stmt=None, kwargs=None):
    if kwargs is None or kwargs['nlp'] is None or stmt is None:
        return 0.0
    
    reply_doc = kwargs['nlp'](reply)
    stmt_doc = kwargs['nlp'](stmt)
    cos_sim = reply_doc.similarity(stmt_doc)

    return cos_sim
