def item_is_private(item_id):
    query = db.object_collection.object_id == item_id
    query &= db.collections.id == db.object_collection.collection_id
    for collection in db(query).select():
        if not collection.collections.private:
            return False
    return True


def link_object_collections(object_id, collection_id):
    db.object_collection.insert(object_id=object_id, collection_id=collection_id)


def get_owner_id(object_id):
    return db(db.objects.id==object_id).select(db.objects.owner_id).first().owner_id



def get_unfiled_collection(user_id=auth.user_id):
    return db((db.collections.name == "Unfiled") & (db.collections.owner_id == user_id)).select().first()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def delete_item(object_id):
    db(db.objects.id == object_id).update(status=-1)
    db(db.object_collection.object_id == object_id).delete()
    session.flash = {"status": "success", "message": "Item successfully deleted."}
    return redirect(URL('collections', 'index'))


def translate_sortby(query, subject):
    if query == 'date-new':
        return ~subject.created_on
    elif query == 'date-old':
        return subject.created_on
    elif query == 'a-z':
        return subject.name
    elif query == 'z-a':
        return ~subject.name
    elif query == 'value-high':
        return ~subject.currency_value
    elif query == 'value-low':
        return subject.currency_value
    elif query == 'user-a-z':
        return db.auth_user.username
    elif query == 'user-z-a':
        return ~db.auth_user.username
    else:  # default
        return ~subject.updated_on


def maybe_list(var):
    if type(var) is list:
        return [int(v) for v in var]
    else:
        return [int(var)]


def add_in_trade_field(object):
    in_trade_query = (((db.trades_receiving.recv_object_id == object.id) & (db.trades_receiving.trade_id == db.trades.id))
                          | ((db.trades_sending.sent_object_id == object.id) & (db.trades_sending.trade_id == db.trades.id))) \
                         & ~(db.trades.status.belongs([1,2,3]))
    trades = db(in_trade_query).select(db.trades.id, db.trades.sender, db.trades.receiver)
    object.in_trade = len(trades) > 0
    if object.in_trade:
        trade = trades.first()
        object.trade_id = trade.id
        object.trade_sender = trade.sender
        object.trade_receiver = trade.receiver
    return object

