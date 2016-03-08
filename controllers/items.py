@auth.requires_login()
def create():
    form = SQLFORM(db.objects)
    types = db(db.types.id > 0).select()
    collections = db(db.collections.owner_id == auth.user_id).select()
    if request.vars.collection is not None:
        selected_collection = int(request.vars.collection)
    else:
        selected_collection = None

    if form.process().accepted:
        if request.vars.collections is not None:
            chosen_cols = [int(col) for col in request.vars.collections] or [request.vars.collections]
            for col in chosen_cols:
                db.object_collection.insert(object_id=form.vars.id, collection_id=col)

        session.flash = {"status": "success", "message": "Item successfully saved"}
        return redirect(URL('items', 'show', args=form.vars.id))
    elif form.errors:
        response.flash = {"status": "danger", "message": "An error has occured. See below."}

    return dict(form=form, types=types, collections=collections, selected_collection=selected_collection)


@auth.requires_login()
def edit():
    object_id = request.args[0] or redirect(URL('items', 'index'))

    obj = db(db.objects.id == object_id).select().first()
    object_collections = [col.id for col in obj.collections()]

    if obj.owner_id != auth.user_id:
        return redirect(URL('items', 'index'))

    form = SQLFORM(db.objects, record=obj, showid=False, deletable=True, submit_button='Update')
    types = db(db.types.id > 0).select()
    collections = db(db.collections.owner_id == auth.user_id).select()

    if form.process().accepted:
        chosen_cols = [int(col) for col in request.vars.collections] or [request.vars.collections]

        for col in chosen_cols:
            db.object_collection.insert(object_id=form.vars.id, collection_id=col)

        session.flash = {"status": "success", "message": "Item successfully saved"}
        return redirect(URL('items', 'show', args=form.vars.id))
    elif form.errors:
        response.flash = {"status": "danger", "message": "An error has occured. See below."}

    return dict(object=obj, form=form, types=types, collections=collections, object_collections=object_collections)


@auth.requires_login()
def show():
    item_id = request.args[0] or redirect(URL('default', 'index'))
    item = db(db.objects.id == item_id).select().first()
    user = db(db.auth_user.id == item.owner_id).select().first()

    is_owner = user.id == auth.user_id

    return dict(item=item, is_owner=is_owner, user=user)
