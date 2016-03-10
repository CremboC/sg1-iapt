def item_is_private(item_id):
    query = db.object_collection.object_id == item_id
    query &= db.collections.id == db.object_collection.collection_id
    for collection in db(query).select():
        if not collection.collections.private:
            return False
    return True


def link_object_collections(object_id, collection_id):
    db.object_collection.insert(object_id=object_id, collection_id=collection_id)


def get_unfiled_collection(user_id=auth.user_id):
    return db((db.collections.name == "Unfiled") & (db.collections.owner_id == user_id)).select().first()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def translate_sortby(query):
    if query == 'date-new':
        return ~db.objects.created_on
    elif query == 'date-old':
        return db.objects.created_on
    elif query == 'a-z':
        return db.objects.name
    elif query == 'z-a':
        return ~db.objects.name
    elif query == 'value-high':
        return ~db.objects.currency_value
    elif query == 'value-low':
        return db.objects.currency_value
    else:  # default
        return ~db.objects.updated_on
