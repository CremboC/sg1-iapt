# coding=utf-8
import json


@auth.requires_login()
def view():
    # Todo: implement view with completed trades
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
        (db.trades_sending.trade_id == trade_id) & (db.trades_sending.sent_object_id == db.objects.id)).select(
        db.objects.ALL)

    # Get objects currently in trade from receiver
    trade_objects_from_receiver = db(
        (db.trades_receiving.trade_id == trade_id) & (db.trades_receiving.recv_object_id == db.objects.id)).select(
        db.objects.ALL)

    # Get other user's username
    if trade.sender == auth.user_id:
        trader_id = trade.receiver
        trade_objects = [trade_objects_from_sender, trade_objects_from_receiver]
    else:
        trader_id = trade.sender
        trade_objects = [trade_objects_from_receiver, trade_objects_from_sender]

    # Verify whether trade is editable
    editable = (trade.status == 0) | (trade.status == 4)
    if trader_username is None:
        trader_username = db(db.auth_user.id == trader_id).select(db.auth_user.username).column()[0]
    return {"user_is_receiver": auth.user_id == trade.receiver, "tradeid": trade_id, "trader_id": trader_id,
            "status": trade.status, "trader_username": trader_username,
            "editable": editable,
            "trade_objects": trade_objects}


@auth.requires_login()
def new():
    receiver_username = request.vars.receiver_username
    receiver_id = request.vars.receiver_id
    item_id = request.vars.item_id
    if (receiver_username is None) & (receiver_id is not None):
        receiver_username = db(db.auth_user.id == receiver_id).select(db.auth_user.username).column()[0]

    object = None
    if item_id is not None:
        object = db((db.objects.id == item_id) & (db.types.id == db.objects.type_id)).select(db.objects.ALL,
                                                                                             db.types.name)[0]
        object.string = format_string(object)
        receiver_username = db(db.auth_user.id == object.objects.owner_id).select(
            db.auth_user.username).column()[0]

    if receiver_username is None:
        return {"user_id": auth.user_id, "trader_id": "", "trader_username": None,
                "available_objects": [get_available_user_items(auth.user_id)], "wanted_object": object}
    elif receiver_username == db(db.auth_user.id == auth.user_id).select(db.auth_user.username).column()[0]:
        session.flash = {"status": "danger", "message": "Error: you can't trade with yourself!"}
        return redirect(URL('trade', 'index'))
    else:
        receiver_id = db(db.auth_user.username == receiver_username).select(db.auth_user.id).column()[0]
        available_items = [get_available_user_items(auth.user_id), get_available_user_items(receiver_id)]
        return {"user_id": auth.user_id, "trader_id": receiver_id, "trader_username": receiver_username,
                "available_objects": available_items, "wanted_object": object}


@auth.requires_login()
def edit():
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
    trade_objects2 = db(trade_query_sender).select(db.objects.ALL, db.types.name)

    for obj in trade_objects2:
        obj.string = format_string(obj)

    trade_query_receiver = db.trades_receiving.trade_id == trade_id
    trade_query_receiver &= db.trades_receiving.recv_object_id == db.objects.id
    trade_query_receiver &= db.objects.type_id == db.types.id

    # Get objects currently in trade from receiver
    trade_objects1 = db(trade_query_receiver).select(db.objects.ALL, db.types.name)

    for obj in trade_objects1:
        obj.string = format_string(obj)

    # Get other user's username
    if trade.sender == auth.user_id:
        trader_id = trade.receiver
        trade_objects = [trade_objects2, trade_objects1]
    else:
        trader_id = trade.sender
        trade_objects = [trade_objects1, trade_objects2]

    # Verify whether trade is editable
    editable = (trade.status == 0)
    if trader_username is None:
        trader_username = db(db.auth_user.id == trader_id).select(db.auth_user.username).column()[0]

    available_objects = [get_available_user_items(auth.user_id), get_available_user_items(trader_id)]
    return {"prevtrade": trade_id, "user_id": auth.user_id, "trader_id": trader_id, "status": trade.status,
            "trader_username": trader_username,
            "editable": editable,
            "trade_objects": trade_objects, "available_objects": available_objects
            }


def getobjectdata():
    object_ids = request.vars.ids.split(",")
    object_ids = map(int, object_ids)
    objects = db(db.objects.id.belongs(object_ids)).select()
    for row in objects:
        if row.image is not None:
            row.image = URL('download', args=row.image)
        else:
            row.image = URL('static', 'images/missing-image.png')
    return objects.json()


@auth.requires_login()
def createNew():
    print request.vars
    if (request.vars['youritems'] is None) | (request.vars['theiritems'] is None):
        print 'Incomplete trade'
        response.status = 400
        return 'Error 400: incomplete trade, please enter trade items or select other user'

    youritems = request.vars['youritems'].split(",")
    theiritems = request.vars['theiritems'].split(",")
    if (youritems == ['']) | (theiritems == ['']):
        print 'Incomplete trade2'
        response.status = 400
        return 'Error 400: incomplete trade, please enter trade items or select other user'

    senderId = int(auth.user_id)
    # Check user owns all objects he proposes

    # Check target user owns all objects proposed
    # Verify all objects belong to correct user
    senderobjectIds = map(int, youritems)
    senderobjects = db(db.objects.id.belongs(senderobjectIds)).select(db.objects.owner_id, db.objects.status, db.objects.name)
    for row in senderobjects:
        print row
        if int(row.owner_id) != senderId:
            response.status = 400
            print 'Invalid ID'
            return 'Error 400: invalid item ID, please refresh page'
        if int(row.status) != 2:
            response.status = 400
            print 'Unavailable item'
            return 'Error 400: Item not available for trade'
    receiverobjectIds = map(int, theiritems)
    receiverobjects = db(db.objects.id.belongs(receiverobjectIds)).select(db.objects.owner_id, db.objects.status)

    receiverId = receiverobjects[0].owner_id
    for row in receiverobjects:
        if int(row.owner_id) != receiverId:
            response.status = 400
            return 'Error 400: invalid item ID, please refresh page'
        if int(row.status) != 2:
            response.status = 400
            return 'Error 400: Item not available for trade'

    if request.vars.prevtrade is not None:
        newTradeId = db.trades.insert(sender=senderId, receiver=receiverId, status=4, seen=False)
    else:
        newTradeId = db.trades.insert(sender=senderId, receiver=receiverId, status=0, seen=False)

    for itemId in senderobjectIds:
        db.trades_sending.insert(trade_id=newTradeId, sent_object_id=itemId)
    for itemId in receiverobjectIds:
        db.trades_receiving.insert(trade_id=newTradeId, recv_object_id=itemId)

    receiver_username = db(db.auth_user.id == receiverId).select(db.auth_user.username).column()[0]
    session.flash = T('Successfully created trade with ' + receiver_username)

    db(db.auth_user.id == receiverId).update(notifications=True)

    if request.vars.prevtrade is not None:
        db(db.trades.id == int(request.vars.prevtrade)).update(status=4, superseded_by=newTradeId)

    redirect(URL('trade', 'index'), client_side=True)


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

    new_sender_objects = map(int, db(db.trades_receiving.trade_id == tradeid).select(
        db.trades_receiving.recv_object_id).column())
    db(db.objects.id.belongs(new_sender_objects)).update(owner_id=trade.sender)

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
    session.flash = T("Trade was accepted")
    return redirect(URL('trade', 'index'), client_side=True)


@auth.requires_login()
def delete():
    trade_id = request.vars.tradeid

    if (trade_id is None) | (not isinstance(trade_id, str)):
        session.flash = {"status": "danger", "message": "Error: trade does not exist"}
        return redirect(URL('trade', 'index'))
    trade = db(db.trades.id == trade_id).select(db.trades.receiver, db.trades.sender)[0]

    if trade is None:
        session.flash = {"status": "danger", "message": "Error: trade does not exist"}
        return redirect(URL('trade', 'index'))
    if (trade.receiver != auth.user_id) & (trade.sender != auth.user_id):
        session.flash = {"status": "danger", "message": "Error: cannot delete a trade you didn't participate in"}
        return redirect(URL('trade', 'index'))

    # Mark as rejected or cancelled
    if auth.user_id == trade.sender:
        session.flash = T("Trade was cancelled")
        db(db.trades.id == trade_id).update(status=1)
    else:
        session.flash = T("Trade was deleted")
        db(db.trades.id == trade_id).update(status=2)

    redirect(URL('trade', 'index'), client_side=True)


@auth.requires_login()
def index():
    db(db.auth_user.id == auth.user_id).update(notifications=False)

    trades_query = (db.trades.sender == auth.user_id) & (db.auth_user.id == db.trades.receiver)
    trades_query |= (db.trades.receiver == auth.user_id) & (db.auth_user.id == db.trades.sender)

    trades = db(trades_query).select(db.trades.ALL, db.auth_user.username)
    incoming = []
    sent = []
    completed = []

    for trade in trades:
        sent_items = db(db.trades_sending.trade_id == trade.trades.id).count()
        sent_item_value = map(int, db((db.trades_sending.trade_id == trade.trades.id) & (
            db.objects.id == db.trades_sending.sent_object_id)).select(db.objects.currency_value).column())
        received_items = db(db.trades_receiving.trade_id == trade.trades.id).count()
        received_item_value = map(int, db((db.trades_receiving.trade_id == trade.trades.id) & (
            db.objects.id == db.trades_receiving.recv_object_id)).select(db.objects.currency_value).column())

        trade.value = sum(sent_item_value) + sum(received_item_value)

        if trade.trades.sender != auth.user_id:
            a = received_items
            received_items = sent_items
            sent_items = a
        trade.sentItems = sent_items
        trade.receivedItems = received_items
        trade.trades.status = int(trade.trades.status)

        if trade.trades.superseded_by is not None:
            completed.append(trade)
        elif (trade.trades.status == 1) | (trade.trades.status == 2) | (trade.trades.status == 3):
            completed.append(trade)
        elif trade.trades.sender == auth.user_id:
            sent.append(trade)
        else:
            incoming.append(trade)

        if trade.trades.sender == auth.user_id:
            trade.trades.otheruser = trade.trades.receiver
        else:
            trade.trades.otheruser = trade.trades.sender
        trade.trades.otheruser = db(db.auth_user.id == trade.trades.otheruser).select(db.auth_user.username).column()[0]
    completed.sort(key=lambda x: x.trades.date_created, reverse=True)

    return {"incoming": incoming, "sent": sent, "completed": completed[:5], "user_id": auth.user_id}


# Get items that are not currently in any trade
def get_available_user_items(userid):
    excludedobjects1 = map(int, db(
        (db.objects.owner_id == userid) &
        (db.trades_receiving.recv_object_id == db.objects.id) &
        (db.trades_receiving.trade_id == db.trades.id) &
        (db.trades.status == 0)).select(
        db.objects.id).column())
    excludedobjects2 = map(int, db(
        (db.objects.owner_id == userid) &
        (db.trades_sending.sent_object_id == db.objects.id) &
        (db.trades_sending.trade_id == db.trades.id) &
        (db.trades.status == 0)).select(
        db.objects.id).column())
    available_objects = db((db.objects.owner_id == userid) & (db.objects.status == 2) & ~db.objects.id.belongs(
        excludedobjects1) & ~db.objects.id.belongs(
        excludedobjects2) & (db.types.id == db.objects.type_id) & (db.objects.id == db.object_collection.object_id) & (db.object_collection.collection_id == db.collections.id) & (db.collections.private == 'F')).select(
        db.objects.id, db.types.name,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)

    for obj in available_objects:
        obj.string = format_string(obj)
    return available_objects


def format_string(object):
    name = object.objects.name + "  "
    name + "{:0,.2f}".format(object.objects.currency_value)

    return name


@auth.requires_login()
def history():
    num_per_page = 20
    if request.vars.index is None:
        min_index = 0
    else:
        min_index = int(request.vars.index)

    trades_query = (db.trades.sender == auth.user_id) & (db.auth_user.id == db.trades.receiver)
    trades_query |= (db.trades.receiver == auth.user_id) & (db.auth_user.id == db.trades.sender)
    trades_query &= db.trades.status.belongs([1, 2, 3])

    trades = db(trades_query).select(db.trades.ALL, db.auth_user.username,
                                     limitby=(min_index, min_index + num_per_page))

    trade_count = db(trades_query).count()

    for trade in trades:
        sent_items = db(db.trades_sending.trade_id == trade.trades.id).count()
        sent_item_value = map(int, db((db.trades_sending.trade_id == trade.trades.id) & (
            db.objects.id == db.trades_sending.sent_object_id)).select(db.objects.currency_value).column())
        received_items = db(db.trades_receiving.trade_id == trade.trades.id).count()
        received_item_value = map(int, db((db.trades_receiving.trade_id == trade.trades.id) & (
            db.objects.id == db.trades_receiving.recv_object_id)).select(db.objects.currency_value).column())

        trade.value = sum(sent_item_value) + sum(received_item_value)

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
    return {"trades": trades, "user_id": auth.user_id, "hasPrevPage": min_index > 0,
            "hasNextPage": trade_count > min_index + num_per_page, "minIndex": min_index, "numPerPage": num_per_page}


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
