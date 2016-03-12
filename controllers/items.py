@auth.requires_login()
def create():
    form = SQLFORM(db.objects)
    types = db(db.types.id > 0).select()
    collections = db(db.collections.owner_id == auth.user_id).select()
    selected_collection = request.vars.collection or -1

    if form.process().accepted:
        if request.vars.collections:
            chosen_cols = maybe_list(request.vars.collections)
            for col in chosen_cols:
                db.object_collection.insert(object_id=form.vars.id, collection_id=col)
        else:
            col = get_unfiled_collection()
            link_object_collections(form.vars.id, col.id)

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
        session.flash = {"status": "danger", "message": "Error: you cannot edit an item that doesn't belong to you"}
        return redirect(URL('default', 'index'))

    form = SQLFORM(db.objects, record=obj, showid=False, deletable=True, submit_button='Update')
    types = db(db.types.id > 0).select()
    collections = db(db.collections.owner_id == auth.user_id).select()

    if form.process().accepted:
        if request.vars.collections:
            chosen_cols = maybe_list(request.vars.collections)

            # remove from collections
            removed_collections = list(set(object_collections) - set(chosen_cols))
            for col in removed_collections:
                db((db.object_collection.collection_id == col) & (
                    db.object_collection.object_id == form.vars.id)).delete()

            new_collections = list(set(chosen_cols) - set(object_collections))

            # add to new collections
            for col in new_collections:
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
        response.flash = {"status": "danger", "message": "An error has occurred. See below."}

    return dict(object=obj, form=form, types=types, collections=collections, object_collections=object_collections)


def show():
    item_id = request.args[0] or redirect(URL('default', 'index'))
    item = db.objects[item_id]
    user = db.auth_user[item.owner_id]

    is_owner = user.id == auth.user_id

    if not item:
        session.flash = {"status": "danger", "message": "Error: this item does not exist"}
        return redirect(URL('default', 'index'))
    if not is_owner and item_is_private(item_id):
        session.flash = {"status": "danger", "message": "Error: you cannot view another user's private items"}
        return redirect(URL('default', 'index'))
    item.in_trade = len(db((db.trades_receiving.recv_object_id == item.id) | (db.trades_sending.sent_object_id == item.id)).select())>0

    return dict(item=item, is_owner=is_owner, user=user)


@auth.requires_login()
def wish():
    item_id = request.args[0] or redirect(URL('default', 'index'))
    item = db.objects[item_id]

    # duplicate all fields
    fields = db.objects._filter_fields(item)

    # set all the fields which need to be changed
    fields['owner_id'] = auth.user.id
    fields['status'] = 1  # wish list
    fields['created_on'] = request.now
    fields['updated_on'] = request.now

    new_item_id = db.objects.insert(**fields)

    link_object_collections(new_item_id, get_unfiled_collection().id)

    session.flash = {"status": "success", "message": "Item successfully added to your wish list."}

    return redirect(URL('items', 'show', args=item_id))
