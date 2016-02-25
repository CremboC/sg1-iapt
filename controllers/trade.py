def index():
    # if auth.user_id is None:
    ## Todo: error redirection if user not logged in
    # print ''

    tradeid = request.vars.tradeid
    # if tradeid is None:
    ## Todo: error redirection if tradeid is invalid
    # print ''

    trade = db.trades(tradeid)
    # if (auth.user_id != trade.sender) | (auth.user_id != trade.receiver):
    ## Todo: error redirection if user not permitted to view trade
    ##print ''


    # Get objects currently in trade from sender
    send_trade_objects = db(
        (db.trades_sending.trade_id == tradeid) & (db.trades_sending.sent_object_id == db.objects.id)).select(
        db.objects.id,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)

    send_object_ids = map(int, db(
        (db.trades_sending.trade_id == tradeid) & (db.trades_sending.sent_object_id == db.objects.id)).select(
        db.objects.id).column())


    # Get objects currently in trade from receiver
    recv_trade_objects = db(
        (db.trades_receiving.trade_id == tradeid) & (db.trades_receiving.recv_object_id == db.objects.id)).select(
        db.objects.id,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)

    recv_object_ids = map(int, db(
        (db.trades_receiving.trade_id == tradeid) & (db.trades_receiving.recv_object_id == db.objects.id)).select(
        db.objects.id).column())


    # Get objects not currently in trade from sender
    # TODO: verify whether we want objects to be available to multiple trades
    # TODO: remove rows with id not
    send_ava_objects = db((db.objects.owner_id == trade.sender) & (db.objects.status == 2) & ~db.objects.id.belongs(
        send_object_ids)).select(
        db.objects.id,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)


    # Get objects not currently in trade from sender
    # TODO: verify whether we want objects to be available to multiple trades
    recv_ava_objects = db((db.objects.owner_id == trade.receiver) & (db.objects.status == 2) & ~db.objects.id.belongs(
        recv_object_ids)).select(
        db.objects.id,
        db.objects.name,
        db.objects.currency_value,
        db.objects.image,
        db.objects.summary)

    # Order usernames to display current user on left in usernames, trade_objects and available_objects
    if auth.user_id == trade.sender:
        usernames = [trade.sender, trade.receiver]
        trade_objects = [send_trade_objects, recv_trade_objects]
        available_objects = [send_ava_objects, recv_ava_objects]
    else:
        usernames = [trade.receiver, trade.sender]
        trade_objects = [recv_trade_objects, send_trade_objects]
        available_objects = [recv_ava_objects, send_ava_objects]

    # Verify whether trade is editable
    editable = (trade.status == 0) | (trade.status == 4)

    return {"usernames": usernames, "editable": editable, "trade_objects": trade_objects,
            "available_objects": available_objects}


def home():
    return dict()


def history():
    # if auth.user_id is None:
    ## Todo: error redirection if user not logged in
    # print ''

    trades = db((db.trades.sender == auth.user_id) | (db.trades.receiver == auth.user_id)
             ).select(db.trades.id, db.trades.date_created, db.trades.sender, db.trades.receiver, db.trades.status, db.trades.superseded_by)
    for trade in trades:
        itemcount = db(db.trades_receiving.trade_id == trade.id).count()
        itemcount += db(db.trades_sending.trade_id == trade.id).count()
        trade.itemcount = itemcount
    return {"trades": trades}
