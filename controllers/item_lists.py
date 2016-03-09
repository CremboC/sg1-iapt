def view():
    want = request.vars.want == 'true'
    user_id = request.vars.user_id
    if user_id is None:
        user_id = auth.user_id
    if user_id is None:
        if want:
            redirect(URL('default', 'user/login', vars={'_next':URL('item_lists', 'view', vars={"want": "true"})}))
        else:
            redirect(URL('default', 'user/login', vars={'_next':URL('item_lists', 'view', vars={"want": "false"})}))

    username = db(db.auth_user.id == user_id).select(db.auth_user.username).column()
    if len(username) == 0:
        raise HTTP(404, "Error 404: Invalid request, userid does not exist")
    else:
        username = username[0]
    if want:
        items = db((db.objects.owner_id == auth.user_id) & (db.objects.status == 0)).select()
    else:
        items = db((db.objects.owner_id == auth.user_id) & (db.objects.status == 1)).select()
    # print items
    return {"is_want": want,
            "user_id": user_id, "username": username, "items": items}
