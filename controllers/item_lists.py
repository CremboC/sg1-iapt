def have():
    user_id = request.vars.user_id
    if user_id is None:
        user_id = auth.user_id
    if user_id is None:
        redirect(URL('default', 'user/login', vars={'_next':URL('item_lists', 'have')}))

    username = db(db.auth_user.id == user_id).select(db.auth_user.username).column()
    if len(username) == 0:
        raise HTTP(404, "Error 404: Invalid request, userid does not exist")
    else:
        username = username[0]
    have_items = db((db.objects.owner_id == auth.user_id) & (db.objects.status == 1)).select()

    return {"is_owner": user_id == auth.user_id, "user_id": user_id, "username": username, "items": have_items}


def want():
    user_id = request.vars.user_id
    if user_id is None:
        user_id = auth.user_id
    if user_id is None:
        redirect(URL('default', 'user/login', vars={'_next':URL('item_lists', 'want')}))

    username = db(db.auth_user.id == user_id).select(db.auth_user.username).column()
    if len(username) == 0:
        raise HTTP(404, "Error 404: Invalid request, userid does not exist")
    else:
        username = username[0]
    want_items = db((db.objects.owner_id == auth.user_id) & (db.objects.status == 0)).select()

    return {"is_owner": user_id == auth.user_id, "user_id": user_id, "username": username, "items": want_items}
