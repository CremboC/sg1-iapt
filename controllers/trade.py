import datetime


# todo: don't trade wanted items



@auth.requires_login()
def view():
    # Todo: implement view with completed trades
    tradeid = request.vars.tradeid
    trader_username = request.vars.trader_username

    trade = db.trades(tradeid)

    # TradeId specified but non-existant,
    if trade is None:
        raise HTTP(404, "Error 404: Invalid request, trade does not exist")

    # or user is not permitted to view
    if (auth.user_id != trade.sender) & (auth.user_id != trade.receiver):
        raise HTTP(404, "Error 404: Invalid request, trade does not exist")


    # Get objects currently in trade from sender
    trade_objects2 = db(
        (db.trades_sending.trade_id == tradeid) & (db.trades_sending.sent_object_id == db.objects.id)).select(
        db.objects.id,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)

    # Get objects currently in trade from receiver
    trade_objects1 = db(
        (db.trades_receiving.trade_id == tradeid) & (db.trades_receiving.recv_object_id == db.objects.id)).select(
        db.objects.id,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)

    # Get other user's username
    if trade.sender == auth.user_id:
        trader_id = trade.receiver
        trade_objects = [trade_objects2, trade_objects1]
    else:
        trader_id = trade.sender
        trade_objects = [trade_objects1, trade_objects2]


    # Verify whether trade is editable
    editable = (trade.status == 0) | (trade.status == 4)
    if trader_username is None:
        trader_username = db(db.auth_user.id == trader_id).select(db.auth_user.username).column()[0]
    return {"user_is_receiver": auth.user_id == trade.receiver, "tradeid": tradeid, "trader_id": trader_id,
            "status": trade.status, "trader_username": trader_username,
            "editable": editable,
            "trade_objects": trade_objects}


@auth.requires_login()
def new():
    receiver_id = request.vars.trader_id
    if receiver_id is None:
        return {"user_id": auth.user_id, "trader_id": "", "trader_username": None,
                "available_objects": [get_available_user_items(auth.user_id)]}
    elif receiver_id == auth.user_id:
        raise HTTP(404, "Cannot trade with yourself")
    else:
        receiver_username = db(db.auth_user.id == receiver_id).select(db.auth_user.username).column()[0]
        if receiver_username is None:
            raise HTTP(404, "Error 404: Invalid request, user id does not exist")
        else:
            available_items = [get_available_user_items(auth.user_id), get_available_user_items(receiver_id)]
            return {"user_id": auth.user_id, "trader_id": receiver_id, "trader_username": receiver_username,
                    "available_objects": available_items}


@auth.requires_login()
def edit():
    tradeid = request.vars.tradeid
    trader_username = request.vars.trader_username

    trade = db.trades(tradeid)

    # TradeId specified but non-existant,
    if trade is None:
        raise HTTP(404, "Error 404: Invalid request, trade does not exist")

    if (trade.status >= 1) & (trade.status <= 3):
        raise HTTP(403, "Error 403: Trade has already been completed")
    # or user is not permitted to view
    if (auth.user_id != trade.sender) & (auth.user_id != trade.receiver):
        raise HTTP(404, "Error 404: Invalid request, trade does not exist")

    # Get objects currently in trade from sender
    trade_objects2 = db(
        (db.trades_sending.trade_id == tradeid) & (db.trades_sending.sent_object_id == db.objects.id)).select(
        db.objects.id,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)


    # Get objects currently in trade from receiver
    trade_objects1 = db(
        (db.trades_receiving.trade_id == tradeid) & (db.trades_receiving.recv_object_id == db.objects.id)).select(
        db.objects.id,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)

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

    return {"prevtrade": tradeid, "user_id": auth.user_id, "trader_id": trader_id, "status": trade.status,
            "trader_username": trader_username,
            "editable": editable,
            "trade_objects": trade_objects,
            "available_objects": [get_available_user_items(auth.user_id), get_available_user_items(trader_id)]}


@auth.requires_login()
def createNew():

    if (request.vars['receiverObjects'] is None) | (request.vars['senderObjects'] is None):
        response.status = 400
        return 'Error 400: incomplete trade, please enter trade items or select other user'

    senderId = int(auth.user_id)
    # Check user owns all objects he proposes

    # Check target user owns all objects proposed

    # Verify all objects belong to correct user
    senderobjectIds = map(int, request.vars['senderObjects'])
    senderobjects = db(db.objects.id.belongs(senderobjectIds)).select(db.objects.owner_id).column()

    for string in senderobjects:
        if string != senderId:
            response.status = 400
            return 'Error 400: invalid item ID, please refresh page'

    receiverobjectIds = map(int, request.vars['receiverObjects'])
    receiverobjects = db(db.objects.id.belongs(receiverobjectIds)).select(db.objects.owner_id).column()


    receiverId = receiverobjects[0].id

    for string in receiverobjects:
        if string != receiverId:
            response.status = 400
            return 'Error 400: invalid item ID, please refresh page'

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

    if request.vars.prevtrade is not None:
        db(db.trades.id == int(request.vars.prevtrade)).update(status=4, superseded_by=newTradeId)

    redirect(URL('trade', 'index'), client_side=True)


@auth.requires_login()
def accept():
    tradeid = request.vars.tradeid
    if (tradeid is None) | (not isinstance(tradeid, str)):
        raise HTTP(400, "Error 400: Trade id invalid or does not exist")
    trade = db.trades[tradeid]
    if trade is None:
        raise HTTP(400, "Error 400: Trade id invalid or does not exist")

    if trade.receiver != auth.user_id:
        raise HTTP(403, "Error 400: not permitted to accept trade")

    newSenderObjects = map(int, db(db.trades_receiving.trade_id == tradeid).select(
        db.trades_receiving.recv_object_id).column())
    db(db.objects.id.belongs(newSenderObjects)).update(owner_id=trade.sender)

    newReceiverObjects = map(int, db(db.trades_sending.trade_id == tradeid).select(
        db.trades_sending.sent_object_id).column())
    db(db.objects.id.belongs(newReceiverObjects)).update(owner_id=trade.receiver)

    # Mark as Accepted
    db(db.trades.id == tradeid).update(status=3)
    session.flash = T("Trade was accepted")
    redirect(URL('trade', 'index'), client_side=True)


@auth.requires_login()
def delete():
    tradeid = request.vars.tradeid

    if (tradeid is None) | (not isinstance(tradeid, str)):
        raise HTTP(400, "Error 400: Trade id invalid or does not exist")
    trade = db(db.trades.id == tradeid).select(db.trades.receiver, db.trades.sender)[0]

    if trade is None:
        raise HTTP(400, "Error 400: Trade id invalid or does not exist")
    print trade
    if (trade.receiver != auth.user_id) & (trade.sender != auth.user_id):
        raise HTTP(403, "Error 400: not permitted to accept trade")

    # Mark as rejected or cancelled
    if auth.user_id == trade.sender:
        session.flash = T("Trade was cancelled")
        db(db.trades.id == tradeid).update(status=1)
    else:
        session.flash = T("Trade was deleted")
        db(db.trades.id == tradeid).update(status=2)

    redirect(URL('trade', 'index'), client_side=True)


@auth.requires_login()
def index():
    trades = db((((db.trades.sender == auth.user_id) & (db.auth_user.id == db.trades.receiver)) | (
        (db.trades.receiver == auth.user_id) & (db.auth_user.id == db.trades.sender)))
                ).select(db.trades.id, db.trades.date_created, db.trades.sender, db.trades.receiver, db.trades.status,
                         db.trades.superseded_by, db.auth_user.username)
    incoming = []
    sent = []
    completed = []
    # 0: Pending
    # 1: Cancelled
    # 2: Rejected
    # 3: Accepted
    # 4: Modified
    for trade in trades:
        sentItems = db(db.trades_sending.trade_id == trade.trades.id).count()
        sentItemValue = db((db.trades_sending.trade_id == trade.trades.id) & (
            db.trades.id == db.trades_sending.sent_object_id)).select(db.objects.currency_value).column()
        receivedItems = db(db.trades_receiving.trade_id == trade.trades.id).count()
        recvItemValue = db((db.trades_receiving.trade_id == trade.trades.id) & (
            db.trades.id == db.trades_receiving.recv_object_id)).select(db.objects.currency_value).column()


        trade.value = sum(sentItemValue) + sum(recvItemValue)

        if trade.trades.sender != auth.user_id:
            a = receivedItems
            receivedItems = sentItems
            sentItems = a
        trade.sentItems = sentItems
        trade.receivedItems = receivedItems
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
        (db.trades_receiving.recv_object_id == db.objects.id)).select(
        db.objects.id).column())
    excludedobjects2 = map(int, db(
        (db.objects.owner_id == userid) &
        (db.trades_sending.sent_object_id == db.objects.id)).select(
        db.objects.id).column())

    return db((db.objects.owner_id == userid) & (db.objects.status == 2) & ~db.objects.id.belongs(
        excludedobjects1) & ~db.objects.id.belongs(
        excludedobjects2)).select(
        db.objects.id,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)
