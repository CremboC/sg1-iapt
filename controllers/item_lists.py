

# Controller to display a user's items for trade page
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

    # Retrieve objects for trade by user
    query = (db.objects.owner_id == user_id) & (db.objects.status == 2)
    query &= (db.object_collection.object_id == db.objects.id)

    query &= (db.object_collection.collection_id == db.collections.id)
    query &= (db.collections.private == False)

    objects = db(query).select(
        db.objects.ALL,
        orderby=translate_sortby(request.vars.sort, db.objects),
        groupby=db.objects.id)

    response.view = "item_lists/view.html"
    # Add data for status icon in object partial
    for obj in objects:
        add_in_trade_field(obj)
    return {"is_want": False, "user_id": user_id, "username": user, "items": objects}


# Controller to display a user's wishlist
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

    # Retrieve all wished items by this user
    query = (db.objects.owner_id == user_id) & (db.objects.status == 1)
    objects = db(query).select(
        db.objects.ALL,
        orderby=translate_sortby(request.vars.sort, db.objects),
        groupby=db.objects.id)

    response.view = "item_lists/view.html"

    # Add data for status icon in object partial
    for object in objects:
        add_in_trade_field(object)
    return {"is_want": True, "user_id": user_id, "username": user, "items": objects}
