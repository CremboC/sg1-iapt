def for_trade():
    user_id = request.vars.user_id or auth.user_id

    if user_id is None:
        redirect(URL('default', 'user/login', vars={'_next': URL('item_lists', 'for_trade')}))

    user = db.auth_user[user_id]

    if not user:
        session.flash = {"status": "danger", "message": "Error: user does not exist"}
        return redirect(URL('default', 'index'))
    else:
        user = user.username

    objects = db((db.objects.owner_id == user_id) & (db.objects.status == 2)).select(
        orderby=translate_sortby(request.vars.sort))

    response.view = "item_lists/view.html"

    for object in objects:
        object.in_trade = len(db((db.trades_receiving.recv_object_id == object.id) | (db.trades_sending.sent_object_id == object.id)).select())>0


    return {"is_want": False, "user_id": user_id, "username": user, "items": objects}


def wish_list():
    user_id = request.vars.user_id or auth.user_id

    if user_id is None:
        redirect(URL('default', 'user/login', vars={'_next': URL('item_lists', 'wish_list')}))

    user = db.auth_user[user_id]

    if not user:
        session.flash = {"status": "danger", "message": "Error: user does not exist"}
        return redirect(URL('default', 'index'))
    else:
        user = user.username

    objects = db((db.objects.owner_id == user_id) & (db.objects.status == 1)).select(
        orderby=translate_sortby(request.vars.sort))

    response.view = "item_lists/view.html"

    for object in objects:
        object.in_trade = len(db((db.trades_receiving.recv_object_id == object.id) | (db.trades_sending.sent_object_id == object.id)).select())>0

    return {"is_want": True, "user_id": user_id, "username": user, "items": objects}
