# coding=utf-8


def item_is_private(item_id):
    """
    Helper to check whether the item is private.
    If the item is in at least one public collection, it is public.
    :type item_id: int
    :return boolean private or not
    """
    query = db.object_collection.object_id == item_id
    query &= db.collections.id == db.object_collection.collection_id
    for collection in db(query).select():
        if not collection.collections.private:
            return False
    return True


def link_object_collections(object_id, collection_id):
    """
    Adds an object to a collection
    :param object_id: int
    :param collection_id: int
    """
    db.object_collection.insert(object_id=object_id, collection_id=collection_id)


def get_owner_id(object_id):
    """
    Get the owner id of the given object
    :param object_id:
    :return:
    """
    return db(db.objects.id == object_id).select(db.objects.owner_id).first().owner_id


def get_unfiled_collection(user_id=auth.user_id):
    """
    Get the unfiled collection of the user. By default, if not is passed, the currently logged in user is used.
    :param user_id:
    :return:
    """
    return db((db.collections.name == "Unfiled") & (db.collections.owner_id == user_id)).select().first()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def delete_item(object_id):
    """
    Delete item by setting its status to -1 and removing all connections to collections
    :param object_id:
    :return:
    """
    db(db.objects.id == object_id).update(status=-1)
    db(db.object_collection.object_id == object_id).delete()
    session.flash = {"status": "success", "message": "Item successfully deleted."}
    return redirect(URL('collections', 'index'))


def translate_sortby(query, subject):
    """
    Convert a sort by text into the actual query for db
    :param query:
    :param subject: can bd db.auth_user, db.collections or db.objects
    :return:
    """
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
    elif query == 'private-no-yes':
        return db.collections.private
    elif query == 'private-yes-no':
        return ~db.collections.private
    else:  # default
        return ~subject.updated_on


def maybe_list(var):
    """
    Useful when dealing with vars from a form that may have multiple values
    :param var:
    :return:
    """
    if type(var) is list:
        return [int(v) for v in var]
    else:
        return [int(var)]


def add_in_trade_field(object):
    """
    Adds a field which indicates whether the passed item is currently in a trade.
    :param object:
    :return:
    """
    in_trade_query = (((db.trades_receiving.recv_object_id == object.id) & (db.trades_receiving.trade_id == db.trades.id))
                          | ((db.trades_sending.sent_object_id == object.id) & (db.trades_sending.trade_id == db.trades.id))) \
                         & ~(db.trades.status.belongs([1, 2, 3]))
    trades = db(in_trade_query).select(db.trades.id, db.trades.sender, db.trades.receiver)
    object.in_trade = len(trades) > 0
    if object.in_trade:
        trade = trades.first()
        object.trade_id = trade.id
        object.trade_sender = trade.sender
        object.trade_receiver = trade.receiver
    return object


def add_object_tooltip(row, tradable=True):
    objects = row.objects
    if tradable:
        txt = "{0} \n £{1} \n Type: {2} \n Summary: {3} \n".format(objects.name, objects.currency_value, row.types.name, objects.summary)
    else:
        txt = "{0} \n £{1} \n This item is not tradable due it's status or use in another trade. \n".format(objects.name, objects.currency_value)
    row.objects.tooltip = txt


# Get items that are not currently in any trade
def get_user_items(userid, tradeid=None):
    # Get items in public collections
    gen_query = (db.objects.owner_id == userid) & \
                (db.types.id == db.objects.type_id) & \
                (db.objects.id == db.object_collection.object_id) & \
                (db.object_collection.collection_id == db.collections.id) & \
                (db.collections.private == 'F')

    coll_query = (db.objects.id == db.object_collection.object_id) & \
                 (db.object_collection.collection_id == db.collections.id)

    items_in_trade = []
    # Get items in public collections
    recv_query = gen_query & \
                 (db.trades_receiving.recv_object_id == db.objects.id) & \
                 (db.trades_receiving.trade_id == db.trades.id) & \
                 (db.trades.status == 0)

    sent_query = gen_query & \
                  (db.trades_sending.sent_object_id == db.objects.id) & \
                  (db.trades_sending.trade_id == db.trades.id) & \
                  (db.trades.status == 0)

    if tradeid is not None:

        items_in_trade.extend(db(db.trades_receiving.trade_id == tradeid).select(db.trades_receiving.recv_object_id).column())
        items_in_trade.extend(db(db.trades_sending.trade_id == tradeid).select(db.trades_sending.sent_object_id).column())

        items_in_trade = map(int, items_in_trade)

        recv_query &= (db.trades.id != tradeid)
        sent_query &= (db.trades.id != tradeid)

    objs_in_trade_recv = db(recv_query & coll_query).select(
        db.types.name,
        db.objects.ALL,
        db.collections.ALL,
        db.trades.ALL,
        groupby=db.objects.id)

    objs_in_trade_sent = db(sent_query & coll_query).select(
        db.types.name,
        db.objects.ALL,
        db.collections.ALL,
        db.trades.ALL,
        groupby=db.objects.id)

    in_trade_ids = []
    for obj in objs_in_trade_recv:
        obj.tradable = False
        add_object_tooltip(obj, False)
        in_trade_ids.append(obj.objects.id)

    for obj in objs_in_trade_sent:
        obj.tradable = False
        add_object_tooltip(obj, False)
        in_trade_ids.append(obj.objects.id)

    items_not_for_trade = db((db.objects.owner_id == userid) & (db.objects.status == 0) & ~db.objects.id.belongs(
        in_trade_ids) & coll_query & (db.types.id == db.objects.type_id)).select(
        db.types.name,
        db.collections.ALL,
        db.objects.ALL,
        groupby=db.objects.id)

    for obj in items_not_for_trade:
        obj.tradable = False
        add_object_tooltip(obj, False)

    in_trade_ids = map(int, in_trade_ids)
    duplicate_objects = db((db.objects.owner_id == userid) & (db.objects.status == 2) & ~db.objects.id.belongs(
        in_trade_ids) & ~(db.objects.id.belongs(items_in_trade)) & (db.types.id == db.objects.type_id) & coll_query &
                           (db.collections.private == 'F')).select(
        db.types.name,
        db.collections.ALL,
        db.objects.ALL)

    available_objects = compact_collection_names(duplicate_objects)

    for obj in available_objects:
        obj.tradable = True
        add_object_tooltip(obj)

    objects = []
    objects.extend(compact_collection_names(objs_in_trade_recv))
    objects.extend(compact_collection_names(objs_in_trade_sent))
    objects.extend(available_objects)
    objects.extend(compact_collection_names(items_not_for_trade))
    return objects


def compact_collection_names(all_objects):
    available_objects = []
    ids = []
    for obj in all_objects:
        if not (int(obj.objects.id) in ids):
            ids.append(int(obj.objects.id))
            collections = set()
            for obj2 in all_objects:
                if obj.objects.id == obj2.objects.id:
                    collections.add(obj2.collections.name)
            compacted_obj = obj
            compacted_obj.collection_names = ' '.join(collections)
            available_objects.append(compacted_obj)
    return available_objects


def get_user_collections(user_id):
    """
    Get all collection names of the given user
    :param user_id:
    :return:
    """
    return db(db.collections.owner_id == user_id).select(db.collections.name).column()


def get_user_collections_no_unfiled(user_id):
    """
    Get all collection names of the given user, ignoring the unfiled one.
    :param user_id:
    :return:
    """
    collections = get_user_collections(user_id)
    collections.remove('Unfiled')
    return collections
