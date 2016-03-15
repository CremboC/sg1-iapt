def add_in_trade_field(object):

    in_trade_query = (((db.trades_receiving.recv_object_id == object.id) & (db.trades_receiving.trade_id == db.trades.id))
                          | ((db.trades_sending.sent_object_id == object.id) & (db.trades_sending.trade_id == db.trades.id))) \
                         & ~(db.trades.status.belongs([1,2,3]))
    object.in_trade = len(db(in_trade_query).select()) > 0
    return object

