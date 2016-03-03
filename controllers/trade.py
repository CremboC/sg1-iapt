# note: don't trade wanted items

@auth.requires_login()
def index():
    print 'a'


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
    editable = (trade.status == 0)
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

    # or user is not permitted to view
    if (auth.user_id != trade.sender) & (auth.user_id != trade.receiver):
        raise HTTP(404, "Error 404: Invalid request, trade does not exist")

    # Todo check trade is not completed, if so redirect to view
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
    print trade_objects[1]

    print get_available_user_items(trade.receiver)
    return {"user_id": auth.user_id, "trader_id": trader_id, "status": trade.status, "trader_username": trader_username,
            "editable": editable,
            "trade_objects": trade_objects,
            "available_objects": [get_available_user_items(auth.user_id), get_available_user_items(trader_id)]}


@auth.requires_login()
def createNew():
    print request.vars
    if (request.vars['receiverObjects'] is None) | (request.vars['senderObjects'] is None):
        response.status = 400
        return 'Error: incomplete trade, please enter trade items or select other user'

    senderId = int(auth.user_id)
    # Check user owns all objects he proposes

    # Check target user owns all objects proposed

    # Verify all objects belong to correct user
    senderobjectIds = map(int, request.vars['senderObjects'])
    senderobjects = db(db.objects.id.belongs(senderobjectIds)).select(db.objects.owner_id).column()
    for string in senderobjects:
        if string != senderId:
            response.status = 400
            return 'Error: invalid item ID, please refresh page'

    receivedobjectIds = map(int, request.vars['receiverObjects'])
    receivedobjects = db(db.objects.id.belongs(receivedobjectIds)).select(db.objects.owner_id).column()
    receiverId = receivedobjects[0].id

    for string in receivedobjects:
        if string != receiverId:
            response.status = 400
            return 'Error: invalid item ID, please refresh page'

    newTradeId = db.trades.insert(sender=senderId, receiver=receiverId, status=0, seen=False)
    # Link to previous trade
    if request.vars.prevTrade is not None:
        db(db.trades.id == int(request.vars.prevTrade)).update(superseded_by=newTradeId, status=4)

    for itemId in senderobjectIds:
        db.trades_sending.insert(trade_id=newTradeId, sent_object_id=itemId)
    for itemId in receivedobjectIds:
        db.trades_receiving.insert(trade_id=newTradeId, recv_object_id=itemId)
    receiver_username = db(db.auth_user.id == receiverId).select(db.auth_user.username).column()[0]
    session.flash = T(
        'Successfully created trade with ' + receiver_username if receiver_username is not None else 'unknown')
    redirect(URL('trade', 'home'), client_side=True)


@auth.requires_login()
def accept():
    tradeid = request.vars.tradeid
    if (tradeid is None) | (type(tradeid) is not (int | long)):
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
        db(db.trades.id == tradeid).update(status=1)
    else:
        db(db.trades.id == tradeid).update(status=2)
    redirect(URL('trade', 'home'))

@auth.requires_login()
def history():
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
        if (trade.trades.status == 1) | (trade.trades.status == 2) | (trade.trades.status == 3):
            completed.append(trade)
        elif trade.trades.sender == auth.user_id:
            sent.append(trade)
        else:
            incoming.append(trade)
    print incoming
    print sent
    print completed
    return {"incoming": incoming, "sent": sent, "completed": completed}


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
