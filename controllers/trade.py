# note: don't trade wanted items

@auth.requires_login()
def index():
    tradeid = request.vars.tradeid
    trader_username = request.vars.trader_username


    # If no trade id specified assume new trade
    if tradeid is None:
        # If no trader specified create blank form
        if trader_username is None:
            return {"editable": True, "user_id": auth.user_id, "status": 0, "trader_username": "", "trader_id": "",
                    "available_objects": [get_available_user_items(auth.user_id), []], "trade_objects": [[], []]}
        else:
            # If trader specified pre-fill trade form
            if db(db.auth_user.username == trader_username).count() == 1:
                trader_id = db(db.auth_user.username == trader_username).select(db.auth_user.id).column()[0]
                if trader_id == auth.user_id:
                    response.flash = "You cannot trade with yourself!"
                    return {"editable": True, "user_id": auth.user_id, "status": 0, "trader_username": "", "trader_id": "",
                    "available_objects": [get_available_user_items(auth.user_id), []], "trade_objects": [[], []]}

                else:
                    return {"editable": True, "user_id": auth.user_id, "status": 0, "trader_id": trader_id,
                            "trader_username": trader_username,
                            "available_objects": [get_available_user_items(auth.user_id),
                                                  get_available_user_items(trader_id)], "trade_objects": [[], []]}
            else:
                raise HTTP(400, "Error 400: username does not exist")

    trade = db.trades(tradeid)

    # TradeId specified but non-existant, or user is not permitted to view
    if (trade is None):
        raise HTTP(404, "Error 404: Invalid request, trade does not exist")

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
    return {"user_id": auth.user_id, "trader_id": trader_id, "status": trade.status, "trader_username": trader_username,
            "editable": editable,
            "trade_objects": trade_objects,
            "available_objects": [get_available_user_items(auth.user_id), get_available_user_items(trader_id)]}

#TODO accept trade system

@auth.requires_login()
def newTrade():
    if (request.vars['receivedItems[]'] is None) | (request.vars['sentItems[]'] is None) | (
                request.vars.receivedId is None) | (request.vars.senderId is None):
        response.status = 400
        return 'Error: incomplete trade, please enter trade items or select other user'

    receiverId = int(request.vars.receivedId)
    senderId = int(request.vars.senderId)
    if int(auth.user_id) != senderId:
        response.status = 400
        return 'Error: not logged in for this trade'

    # Verify all objects belong to correct user
    senderobjectIds = map(int, request.vars['sentItems[]'])
    senderobjects = db(db.objects.id.belongs(senderobjectIds)).select(db.objects.owner_id).column()
    for string in senderobjects:
        if string != senderId:
            response.status = 400
            return 'Error: invalid item ID, please refresh page'

    receivedobjectIds = map(int, request.vars['receivedItems[]'])
    receivedobjects = db(db.objects.id.belongs(receivedobjectIds)).select(db.objects.owner_id).column()
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
    # print 'Username'
    receiver_username = db(db.auth_user.id == receiverId).select(db.auth_user.username).column()[0]
    session.flash = T(
        'Successfully created trade with ' + receiver_username if receiver_username is not None else 'unknown')
    redirect(URL('trade', 'home'), client_side=True)


# Get items that are not currently in any trade
def get_available_user_items(userid):
    excludedobjects = map(int, db(
        (db.objects.owner_id == userid) &
        ((db.trades_sending.trade_id == db.objects.id) | (db.trades_receiving.trade_id == db.objects.id))).select(
        db.objects.id).column())

    return db((db.objects.owner_id == userid) & (db.objects.status == 2) & ~db.objects.id.belongs(
        excludedobjects)).select(
        db.objects.id,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)

@auth.requires_login()
def home():
    return {}


def history():
    # if auth.user_id is None:
    ## Todo: error redirection if user not logged in
    # print ''

    trades = db((((db.trades.sender == auth.user_id) & (db.auth_user.id == db.trades.receiver)) | ((db.trades.receiver == auth.user_id) & (db.auth_user.id == db.trades.sender)))
                ).select(db.trades.id, db.trades.date_created, db.trades.sender, db.trades.receiver, db.trades.status,
                         db.trades.superseded_by, db.auth_user.username)

    for trade in trades:
        sentItems = db(db.trades_sending.trade_id == trade.trades.id).count()
        sentItemValue = db((db.trades_sending.trade_id == trade.trades.id) & (db.trades.id == db.trades_sending.sent_object_id)).select(db.objects.currency_value).column()
        receivedItems = db(db.trades_receiving.trade_id == trade.trades.id).count()
        recvItemValue = db((db.trades_receiving.trade_id == trade.trades.id) & (db.trades.id == db.trades_receiving.recv_object_id)).select(db.objects.currency_value).column()
        trade.value = sum(sentItemValue) + sum(recvItemValue)

        if trade.trades.sender != auth.user_id:
            a = receivedItems
            receivedItems = sentItems
            sentItems = a
        trade.sentItems = sentItems
        trade.receivedItems = receivedItems
    print type(trades[0].trades.date_created)
    return {"trades": trades}
