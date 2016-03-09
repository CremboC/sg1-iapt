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
