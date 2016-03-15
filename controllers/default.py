def index():
    trades = db((((db.trades.sender == auth.user_id) & (db.auth_user.id == db.trades.receiver)) | (
        (db.trades.receiver == auth.user_id) & (db.auth_user.id == db.trades.sender))) &
                db.trades.status.belongs([1, 2, 3])).select(db.trades.id, db.trades.date_created, db.trades.sender,
                                                            db.trades.receiver, db.trades.status,
                                                            db.trades.superseded_by, db.auth_user.username,
                                                            orderby=~db.trades.date_created, limitby=(0, 3))

    for trade in trades:
        sent_items = db(db.trades_sending.trade_id == trade.trades.id).count()
        sent_item_value = map(int, db((db.trades_sending.trade_id == trade.trades.id) & (
            db.objects.id == db.trades_sending.sent_object_id)).select(db.objects.currency_value).column())
        received_items = db(db.trades_receiving.trade_id == trade.trades.id).count()
        recv_item_value = map(int, db((db.trades_receiving.trade_id == trade.trades.id) & (
            db.objects.id == db.trades_receiving.recv_object_id)).select(db.objects.currency_value).column())

        trade.value = sum(sent_item_value) + sum(recv_item_value)

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
        trade.otheruser = db(db.auth_user.id == trade.trades.otheruser).select(db.auth_user.username).column()[0]
        trade.other_user_id = trade.trades.otheruser
    # newest_items = db((db.object_collection.object_id == db.objects.id) & (db.collections.private == 'F')).select(db.objects.id, orderby=~db.objects.created_on, limitby=(0,9))
    newest_items = db((db.objects.id == db.object_collection.object_id) & (
    db.object_collection.collection_id == db.collections.id) & (db.collections.private == 'F') & (
                      db.objects.status != -1)).select(db.objects.ALL, orderby=~db.objects.created_on, limitby=(0, 9))

    for item in newest_items:
        add_in_trade_field(item)

    count = db.object_collection.object_id.count()
    collections = db((db.collections.id > 0) & (db.collections.id == db.object_collection.collection_id)).select(db.collections.ALL, count, orderby=~count, limitby=(0,3), groupby=db.collections.id)

    return {"auth_id": auth.user_id, "auth_logged_in": auth.is_logged_in(), "trades": trades,
            "newest_items": newest_items, "largest_collections": collections}


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
