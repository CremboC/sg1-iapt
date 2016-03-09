@auth.requires_login()
def create():
    form = SQLFORM(db.objects)
    types = db(db.types.id > 0).select()
    collections = db(db.collections.owner_id == auth.user_id).select()
    selected_collection = request.vars.collection or -1

    if form.process().accepted:
        if request.vars.collections is not None:
            chosen_cols = [int(col) for col in request.vars.collections] or [request.vars.collections]
            for col in chosen_cols:
                db.object_collection.insert(object_id=form.vars.id, collection_id=col)

        session.flash = {"status": "success", "message": "Item successfully saved"}
        return redirect(URL('items', 'show', args=form.vars.id))
    elif form.errors:
        response.flash = {"status": "danger", "message": "An error has occured. See below."}

    return dict(form=form, types=types, collections=collections, selected_collection=int(selected_collection))


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
        if request.vars.collections:
            chosen_cols = [int(col) for col in request.vars.collections] or [request.vars.collections]

            # remove from collections
            removed_collections = list(set(object_collections) - set(chosen_cols))
            for col in removed_collections:
                db((db.object_collection.collection_id == col) & (
                    db.object_collection.object_id == form.vars.id)).delete()

            # add to new collections
            for col in chosen_cols:
                link_object_collections(form.vars.id, col)
        else:
            # remove from all collections it was previously in
            for col in object_collections:
                db((db.object_collection.collection_id == col) & (
                    db.object_collection.object_id == form.vars.id)).delete()

            # since the item must be in a collection, re-add to the unfiled for simplicity
            col = get_unfiled_collection()
            link_object_collections(form.vars.id, col.id)

        session.flash = {"status": "success", "message": "Item successfully saved"}
        return redirect(URL('items', 'show', args=form.vars.id))
    elif form.errors:
        response.flash = {"status": "danger", "message": "An error has occured. See below."}

    return dict(object=obj, form=form, types=types, collections=collections, object_collections=object_collections)


def show():
    item_id = request.args[0] or redirect(URL('default', 'index'))
    item = db.objects[item_id]
    user = db.auth_user[item.owner_id]

    is_owner = user.id == auth.user_id

    # Item doesn't exist or is private
    if not item or not is_owner and item_is_private(item_id):
        raise HTTP(404, "Error 404: Invalid request, item does not exist")

    return dict(item=item, is_owner=is_owner, user=user)
