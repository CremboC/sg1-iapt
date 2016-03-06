@auth.requires_login()
def create():
    form = SQLFORM(db.objects)
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

    return dict(form=form, types=types, collections=collections)


@auth.requires_login()
def show():
    item_id = request.args[0] or redirect(URL('default', 'index'))
    item = db(db.objects.id == item_id).select().first()

    return dict(item=item)
