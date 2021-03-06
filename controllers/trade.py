# coding=utf-8


# Controller to view an existing trade
@auth.requires_login()
def view():
    trade_id = request.vars.tradeid
    trader_username = request.vars.trader_username

    trade = db.trades(trade_id)

    # TradeId specified but non-existant,
    if trade is None:
        session.flash = {"status": "danger", "message": "Error: trade does not exist"}
        return redirect(URL('trade', 'index'))

    # or user is not permitted to view
    if (auth.user_id != trade.sender) & (auth.user_id != trade.receiver):
        session.flash = {"status": "danger", "message": "Error: cannot view a trade in which you do not participate"}
        return redirect(URL('trade', 'index'))

    # Get objects currently in trade from sender
    trade_objects_from_sender = db(
        (db.trades_sending.trade_id == trade_id) & (db.types.id == db.objects.type_id) & (
        db.trades_sending.sent_object_id == db.objects.id)).select(
        db.objects.ALL, db.types.name)

    # Get objects currently in trade from receiver
    trade_objects_from_receiver = db(
        (db.trades_receiving.trade_id == trade_id) & (db.types.id == db.objects.type_id) & (
        db.trades_receiving.recv_object_id == db.objects.id)).select(
        db.objects.ALL, db.types.name)

    for obj in trade_objects_from_receiver:
        obj.tradable = False
        add_in_trade_field(obj.objects)
        add_object_tooltip(obj)

    for obj in trade_objects_from_sender:
        obj.tradable = False
        add_in_trade_field(obj.objects)
        add_object_tooltip(obj)

    # Get other user's username
    if trade.sender == auth.user_id:
        trader_id = trade.receiver
        trade_objects = [trade_objects_from_sender, trade_objects_from_receiver]
    else:
        trader_id = trade.sender
        trade_objects = [trade_objects_from_receiver, trade_objects_from_sender]

    if trader_username is None:
        trader_username = db(db.auth_user.id == trader_id).select(db.auth_user.username)
        if len(trader_username) == 0:
            session.flash = {"status": "danger", "message": "Error: invalid username"}
            return redirect(URL('trade', 'index'))
        else:
            trader_username = trader_username[0].username
    if not trade.seen & (trade.receiver == auth.user_id):
        db(db.trades.id == trade.id).update(seen=True)
    return {"user_is_receiver": auth.user_id == trade.receiver, "tradeid": trade_id, "trader_id": trader_id,
            "status": trade.status, "trader_username": trader_username,
            "editable": trade.status == 0,
            "trade_objects": trade_objects}


# Method to display the page in which users can create a new trade
# (called when offering to trade for a particular item)
@auth.requires_login()
def new():
    # Method can accept a user or an item id, the receiver_id will take precedence over the user if both are specified
    receiver_id = request.vars.receiver_id
    item_id = request.vars.item_id

    if request.vars.receiver_username == auth.user.username:
        session.flash = {"status": "danger", "message": "Error: You cannot trade with yourself."}
        return redirect(URL('trade', 'index'))

    if (request.vars.receiver_id is None) & (request.vars.item_id is None) & (request.vars.receiver_username is not None):
        receiver = db(db.auth_user.username == request.vars.receiver_username).select().first()
        if receiver is None:
            session.flash = {"status": "danger", "message": "Error: username does not exist"}
            return redirect(URL('trade', 'index'))
        else:
            receiver_id = receiver.id

    if (receiver_id is None) & (item_id is None):
        session.flash = {"status": "danger", "message": "Error: no specified receiver_id or item_id"}
        return redirect(URL('trade', 'index'))

    obj = None
    if receiver_id is not None:
        receiver_username = db(db.auth_user.id == receiver_id).select(db.auth_user.username).column()
        if len(receiver_username) == 0:
            session.flash = {"status": "danger", "message": "Error: invalid user id"}
            return redirect(URL('trade', 'index'))
        receiver_username = receiver_username[0]
    else:
        obj = db((db.objects.id == item_id) & (db.types.id == db.objects.type_id)).select(db.objects.ALL, db.types.name)
        if len(obj) == 0:
            session.flash = {"status": "danger", "message": "Error: invalid item id"}
            return redirect(URL('trade', 'index'))

        obj = obj[0]
        add_in_trade_field(obj.objects)
        if obj.objects.in_trade:
            session.flash = {"status": "danger",
                             "message": "Error: item cannot be traded as it is currently in another trade"}
            return redirect(URL('trade', 'index'))

        receiver_username = db(db.auth_user.id == obj.objects.owner_id).select(
            db.auth_user.username).column()[0]
        obj = obj.objects.id

    if receiver_username == db(db.auth_user.id == auth.user_id).select(db.auth_user.username).column()[0]:
        session.flash = {"status": "danger", "message": "Error: you can't trade with yourself!"}
        return redirect(URL('trade', 'new'))
    else:
        receiver_id = db(db.auth_user.username == receiver_username).select(db.auth_user.id)
        if len(receiver_id) == 0:
            session.flash = {"status": "danger", "message": "Error: username does not exist"}
            return redirect(URL('trade', 'new'))
        receiver_id = receiver_id[0].id
        # Retrieve available items for both users
        available_items = [get_user_items(auth.user_id, True), get_user_items(receiver_id, False)]
        # Retrieve all available collections for both users (used to filter items)
        collections = [get_user_collections_no_unfiled(auth.user_id), get_user_collections_no_unfiled(receiver_id)]
        return {"user_id": auth.user_id, "trader_id": receiver_id, "trader_username": receiver_username,
                "available_objects": available_items, "wanted_object": obj, "collections": collections}


# Method to edit an existing trade (trade objects are non-mutable: a new trade will be created, and the old trade
# will have its status changed to signify its termination)
@auth.requires_login()
def edit():
    coll_query = (db.objects.id == db.object_collection.object_id) & \
                 (db.object_collection.collection_id == db.collections.id)

    trade_id = request.vars.tradeid
    trader_username = request.vars.trader_username

    trade = db.trades(trade_id)

    # TradeId specified but non-existant,
    if trade is None:
        session.flash = {"status": "danger", "message": "Error: trade does not exist"}
        return redirect(URL('trade', 'index'))

    if (trade.status >= 1) & (trade.status <= 3):
        session.flash = {"status": "danger", "message": "Error: trade has already been completed!"}
        return redirect(URL('trade', 'index'))
    # or user is not permitted to view
    if (auth.user_id != trade.sender) & (auth.user_id != trade.receiver):
        session.flash = {"status": "danger", "message": "Error: cannot view a trade in which you do not participate"}
        return redirect(URL('trade', 'index'))

    trade_query_sender = db.trades_sending.trade_id == trade_id
    trade_query_sender &= db.trades_sending.sent_object_id == db.objects.id
    trade_query_sender &= db.objects.type_id == db.types.id

    # Get objects currently in trade from sender
    trade_objects2 = db(trade_query_sender & coll_query).select(db.objects.ALL, db.collections.ALL, db.types.name)

    trade_query_receiver = db.trades_receiving.trade_id == trade_id
    trade_query_receiver &= db.trades_receiving.recv_object_id == db.objects.id
    trade_query_receiver &= db.objects.type_id == db.types.id

    # Get objects currently in trade from receiver
    trade_objects1 = db(trade_query_receiver & coll_query).select(db.objects.ALL, db.collections.ALL, db.types.name)

    # Get other user's username
    if trade.sender == auth.user_id:
        receiver_id = trade.receiver
        trade_objects = [trade_objects2, trade_objects1]
    else:
        receiver_id = trade.sender
        trade_objects = [trade_objects1, trade_objects2]

    if trade.status != 0:
        session.flash = {"status": "danger",
                         "message": "Error: trade has been completed or superseeded, and cannot be edited."}
        return redirect(URL('trade', 'index'))

    if trader_username is None:
        trader_username = db(db.auth_user.id == receiver_id).select(db.auth_user.username)
        if len(trader_username) == 0:
            session.flash = {"status": "danger", "message": "Error: invalid user id"}
            return redirect(URL('trade', 'index'))
        trader_username = trader_username[0].username

    available_objects = [get_user_items(auth.user_id, True, trade_id), get_user_items(receiver_id, False, trade_id)]

    trade_objects[0] = compact_collection_names(trade_objects[0])
    trade_objects[1] = compact_collection_names(trade_objects[1])

    trade_profit = 0
    for obj in trade_objects[0]:
        obj.tradable = True
        add_object_tooltip(obj, True)
        trade_profit -= obj.objects.currency_value

    for obj in trade_objects[1]:
        obj.tradable = True
        add_object_tooltip(obj, True)
        trade_profit += obj.objects.currency_value
    collections = [get_user_collections_no_unfiled(auth.user_id), get_user_collections_no_unfiled(receiver_id)]
    return {"prevtrade": trade_id, "user_id": auth.user_id, "trader_id": receiver_id, "status": trade.status,
            "trader_username": trader_username, "trade_profit": trade_profit,
            "trade_objects": trade_objects, "available_objects": available_objects, "collections": collections}


# Method to create a new trade
@auth.requires_login()
def createNew():
    if (request.vars['youritems'] is None) | (request.vars['theiritems'] is None) | (
                request.vars['receiver_username'] is None):
        response.status = 400
        return 'Error 400: incomplete trade, please enter trade items'

    receiver_id = db(db.auth_user.username == request.vars['receiver_username']).select(db.auth_user.id)

    if len(receiver_id) == 0:
        response.status = 400
        return 'Error 400: invalid username, please select another user'
    receiver_id = receiver_id[0].id

    if request.vars['youritems'] != '':
        your_items = request.vars['youritems'].split(",")
    else:
        your_items = []

    if request.vars['theiritems'] != '':
        their_items = request.vars['theiritems'].split(",")
    else:
        their_items = []

    if (len(your_items) == 0) & (len(their_items) == 0):
        response.status = 400
        return 'Error 400: incomplete trade. You cannot initiate an empty trade. Please choose some items first.'

    sender_id = int(auth.user_id)

    # Verify all objects belong to correct user
    # Check user owns all objects he proposes
    if len(your_items) > 0:
        sender_objects_id = map(int, your_items)
        sender_objects = db(db.objects.id.belongs(sender_objects_id)).select(db.objects.owner_id, db.objects.status,
                                                                             db.objects.name)
        for row in sender_objects:
            if int(row.owner_id) != sender_id:
                response.status = 400
                return 'Error 400: invalid item ID, please refresh page'
            if int(row.status) != 2:
                response.status = 400
                return 'Error 400: Item not available for trade'

    # Check target user owns all objects proposed
    if len(their_items) > 0:
        receiver_objects_id = map(int, their_items)
        receiver_objects = db(db.objects.id.belongs(receiver_objects_id)).select(db.objects.owner_id, db.objects.status)

        for row in receiver_objects:
            if int(row.owner_id) != receiver_id:
                response.status = 400
                return 'Error 400: invalid item ID, please refresh page'
            if int(row.status) != 2:
                response.status = 400
                return 'Error 400: Item not available for trade'

    new_trade_id = db.trades.insert(sender=sender_id, receiver=receiver_id, status=0, seen=False)

    if len(your_items) > 0:
        for itemId in sender_objects_id:
            db.trades_sending.insert(trade_id=new_trade_id, sent_object_id=itemId)
    if len(their_items) > 0:
        for itemId in receiver_objects_id:
            db.trades_receiving.insert(trade_id=new_trade_id, recv_object_id=itemId)

    receiver_username = db(db.auth_user.id == receiver_id).select(db.auth_user.username).column()[0]

    db(db.auth_user.id == receiver_id).update(notifications=True)

    if request.vars.prevtrade is not None:
        db(db.trades.id == int(request.vars.prevtrade)).update(status=4, superseded_by=new_trade_id)

    session.flash = {"status": "success", "message": "Sent a trade proposal to " + receiver_username}
    redirect(URL('trade', 'index'), client_side=True)


# Method for a receiver of a trade proposal to accept a change and exchange the trade's items
@auth.requires_login()
def accept():
    tradeid = request.vars.tradeid
    if (tradeid is None) | (not isinstance(tradeid, str)):
        session.flash = {"status": "danger", "message": "Error: trade does not exist"}
        return redirect(URL('trade', 'index'))
    trade = db.trades[tradeid]

    if trade is None:
        session.flash = {"status": "danger", "message": "Error: trade does not exist"}
        return redirect(URL('trade', 'index'))

    if trade.receiver != auth.user_id:
        session.flash = {"status": "danger", "message": "Error: you cannot accept a trade that wasn't sent to you"}
        return redirect(URL('trade', 'index'))

    # Ids of items to be given to the sender from the receiver
    new_sender_objects = map(int, db(db.trades_receiving.trade_id == tradeid).select(
        db.trades_receiving.recv_object_id).column())
    db(db.objects.id.belongs(new_sender_objects)).update(owner_id=trade.sender)

    # Ids of items to be given to the receiver from the sender
    new_receiver_objects = map(int, db(db.trades_sending.trade_id == tradeid).select(
        db.trades_sending.sent_object_id).column())
    db(db.objects.id.belongs(new_receiver_objects)).update(owner_id=trade.receiver)

    # Remove all items from user's previous collections
    db(db.object_collection.object_id.belongs(new_sender_objects + new_receiver_objects)).delete()

    unfiled_sender = get_unfiled_collection(trade.sender).id

    for id in new_sender_objects:
        db.object_collection.insert(object_id=id, collection_id=unfiled_sender)

    unfiled_receiver = get_unfiled_collection(trade.receiver).id

    for id in new_receiver_objects:
        db.object_collection.insert(object_id=id, collection_id=unfiled_receiver)

    # Mark as Accepted
    db(db.trades.id == tradeid).update(status=3)
    session.flash = {"status": "success", "message": "Trade was successfully accepted"}
    return redirect(URL('trade', 'index'), client_side=True)


# Method to delete/cancel a trade
@auth.requires_login()
def delete():
    trade_id = request.vars.tradeid

    if (trade_id is None) | (not isinstance(trade_id, str)):
        session.flash = {"status": "danger", "message": "Error: trade does not exist"}
        return redirect(URL('trade', 'index'))
    trade = db(db.trades.id == trade_id).select(db.trades.receiver, db.trades.sender).first()

    if trade is None:
        session.flash = {"status": "danger", "message": "Error: trade does not exist"}
        return redirect(URL('trade', 'index'))
    if (trade.receiver != auth.user_id) & (trade.sender != auth.user_id):
        session.flash = {"status": "danger", "message": "Error: cannot delete a trade you didn't participate in"}
        return redirect(URL('trade', 'index'))

    # Mark as rejected or cancelled
    if auth.user_id == trade.sender:
        session.flash = {"status": "success", "message": "Trade was cancelled."}

        db(db.trades.id == trade_id).update(status=1)
    else:
        session.flash = {"status": "success", "message": "Trade was rejected."}
        db(db.trades.id == trade_id).update(status=2)

    redirect(URL('trade', 'index'), client_side=True)


# Method to display a user's trade home
@auth.requires_login()
def index():
    db(db.auth_user.id == auth.user_id).update(notifications=False)

    trades_query = (db.trades.sender == auth.user_id) & (db.auth_user.id == db.trades.receiver)
    trades_query |= (db.trades.receiver == auth.user_id) & (db.auth_user.id == db.trades.sender)
    # Select all of a user's trades, before organising them into incoming/sent/completed trades
    trades = db(trades_query).select(db.trades.ALL, db.auth_user.username)
    incoming = []
    sent = []
    completed = []

    for trade in trades:
        # Add details of items related to each trade
        sent_items = db(db.trades_sending.trade_id == trade.trades.id).count()
        received_items = db(db.trades_receiving.trade_id == trade.trades.id).count()

        if trade.trades.sender != auth.user_id:
            a = received_items
            received_items = sent_items
            sent_items = a
        trade.sentItems = sent_items
        trade.receivedItems = received_items
        trade.trades.status = int(trade.trades.status)

        if (trade.trades.status == 1) | (trade.trades.status == 2) | (trade.trades.status == 3):
            completed.append(trade)
        elif trade.trades.sender == auth.user_id:
            sent.append(trade)
        elif (trade.trades.receiver == auth.user_id) & (trade.trades.superseded_by is None):
            incoming.append(trade)

        if trade.trades.sender == auth.user_id:
            trade.trades.otheruser = trade.trades.receiver
        else:
            trade.trades.otheruser = trade.trades.sender
        trade.trades.otheruser = db(db.auth_user.id == trade.trades.otheruser).select(db.auth_user.username).column()[0]
    completed.sort(key=lambda x: x.trades.date_created, reverse=True)

    return {"incoming": incoming, "sent": sent, "completed": completed[:5], "user_id": auth.user_id}


# Method to retrieve the log of all trades (modifications, accepted and rejected/modified trades)
@auth.requires_login()
def log():
    num_per_page = 20
    if request.vars.index is None:
        min_index = 0
    else:
        min_index = int(request.vars.index)

    trades_query = (db.trades.sender == auth.user_id) & (db.auth_user.id == db.trades.receiver)
    trades_query |= (db.trades.receiver == auth.user_id) & (db.auth_user.id == db.trades.sender)

    trades = db(trades_query).select(db.trades.ALL, db.auth_user.username,
                                     limitby=(min_index, min_index + num_per_page),
                                     orderby=translate_sortby(request.vars.sort, db.trades))

    trade_count = db(trades_query).count()

    for trade in trades:
        # Add details of items associated to each trade
        sent_items = db(db.trades_sending.trade_id == trade.trades.id).count()
        received_items = db(db.trades_receiving.trade_id == trade.trades.id).count()

        if trade.trades.sender != auth.user_id:
            a = received_items
            received_items = sent_items
            sent_items = a
        trade.sentItems = sent_items
        trade.receivedItems = received_items
        trade.trades.status = int(trade.trades.status)

        if trade.trades.sender == auth.user_id:
            trade.trades.otheruser = trade.trades.receiver
        else:
            trade.trades.otheruser = trade.trades.sender
        trade.trades.otheruser = db(db.auth_user.id == trade.trades.otheruser).select(db.auth_user.username).column()[0]
    return {"trades": trades,
            "user_name": db(db.auth_user.id == auth.user_id).select(db.auth_user.username).first().username,
            "user_id": auth.user_id, "hasPrevPage": min_index > 0,
            "hasNextPage": trade_count > min_index + num_per_page, "minIndex": min_index, "numPerPage": num_per_page}


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
