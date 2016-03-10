def view():
    want = request.vars.want == 'true'
    user_id = request.vars.user_id or auth.user_id

    if user_id is None:
        if want:
            redirect(URL('default', 'user/login', vars={'_next': URL('item_lists', 'view', vars={"want": "true"})}))
        else:
            redirect(URL('default', 'user/login', vars={'_next': URL('item_lists', 'view', vars={"want": "false"})}))

    user = db.auth_user[user_id]

    if not user:
        session.flash = {"status": "danger", "message": "Error: user does not exist"}
        return redirect(URL('default', 'index'))
    else:
        user = user.username

    if want:
        items = db((db.objects.owner_id == auth.user_id) & (db.objects.status == 0)).select(
            orderby=translate_sortby(request.vars.sort))
    else:
        items = db((db.objects.owner_id == auth.user_id) & (db.objects.status == 1)).select(
            orderby=translate_sortby(request.vars.sort))

    return {"is_want": want, "user_id": user_id, "username": user, "items": items}
