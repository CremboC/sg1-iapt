@auth.requires_login()
def create():
    form = SQLFORM(db.objects)
    types = db(db.types.id > 0).select()
    collections = db(db.collections.owner_id == auth.user_id).select()
    selected_collection = request.vars.collection or get_unfiled_collection()

    if form.process().accepted:
        if (request.vars.collections is not None) & (request.vars.status!='1'):
            chosen_cols = maybe_list(request.vars.collections)
            for col in chosen_cols:
                db.object_collection.insert(object_id=form.vars.id, collection_id=col)
        elif request.vars.status != '1':
            col = get_unfiled_collection()
            link_object_collections(form.vars.id, col.id)

        session.flash = {"status": "success", "message": "Item successfully saved"}
        return redirect(URL('items', 'show', args=form.vars.id))
    elif form.errors:
        response.flash = {"status": "danger", "message": "An error has occured. See below."}

    return dict(form=form, types=types, collections=collections, selected_collection=int(selected_collection))

@auth.requires_login()
def delete():
    if request.args is None:
        session.flash = {"status": "danger", "message": "Error: no item selected for deletion"}
        redirect(URL('items', 'index'))
    object_id = request.args[0]

    obj = db(db.objects.id == object_id).select().first()

    if obj.owner_id != auth.user_id:
        session.flash = {"status": "danger", "message": "Error: you cannot edit an item that doesn't belong to you"}
        return redirect(URL('default', 'index'))

    if obj.status == -1:
        session.flash = {"status": "danger", "message": "Error: this item was already deleted"}
        return redirect(URL('default', 'index'))

    return delete_item(object_id)



@auth.requires_login()
def edit():
    if request.args is None:
        session.flash = {"status": "danger", "message": "Error: no item selected for editing"}
        redirect(URL('items', 'index'))

    object_id = request.args[0]

    obj = db(db.objects.id == object_id).select().first()
    if obj.status == -1:
        session.flash = {"status": "danger", "message": "Error: this item was deleted"}
        return redirect(URL('default', 'index'))

    object_collections = [col.id for col in obj.collections()]

    if obj.owner_id != auth.user_id:
        session.flash = {"status": "danger", "message": "Error: you cannot edit an item that doesn't belong to you"}
        return redirect(URL('default', 'index'))

    form = SQLFORM(db.objects, record=obj, showid=False, deletable=True, submit_button='Update')
    types = db(db.types.id > 0).select()
    collections = db(db.collections.owner_id == auth.user_id).select()

    if form.process().accepted:
        if request.vars.delete == 'yes':
            return delete_item(object_id)

        if request.vars.status!='1':
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
        else:
            db(db.object_collection.object_id == form.vars.id).delete()

        session.flash = {"status": "success", "message": "Item successfully saved"}
        return redirect(URL('items', 'show', args=form.vars.id))
    elif form.errors:
        response.flash = {"status": "danger", "message": "An error has occurred. See below."}

    return dict(object=obj, form=form, types=types, collections=collections, object_collections=object_collections)


def show():
    obj_id = request.args[0] or redirect(URL('default', 'index'))
    obj = db.objects[obj_id]
    if obj.status == -1:
        session.flash = {"status": "danger", "message": "Error: this item was deleted"}
        return redirect(URL('default', 'index'))

    user = db.auth_user[obj.owner_id]

    is_owner = user.id == auth.user_id

    if not obj:
        session.flash = {"status": "danger", "message": "Error: this item does not exist"}
        return redirect(URL('default', 'index'))
    if not is_owner and item_is_private(obj_id):
        session.flash = {"status": "danger", "message": "Error: you cannot view another user's private items"}
        return redirect(URL('default', 'index'))

    add_in_trade_field(obj)

    return dict(item=obj, is_owner=is_owner, user=user)


@auth.requires_login()
def wish():
    obj_id = request.args[0] or redirect(URL('default', 'index'))

    obj = db.objects[obj_id]
    if obj.status == -1:
        session.flash = {"status": "danger", "message": "Error: this item was deleted"}
        return redirect(URL('default', 'index'))

    # duplicate all fields
    fields = db.objects._filter_fields(obj)

    # set all the fields which need to be changed
    fields['owner_id'] = auth.user.id
    fields['status'] = 1  # wish list
    fields['created_on'] = request.now
    fields['updated_on'] = request.now

    new_item_id = db.objects.insert(**fields)

    session.flash = {"status": "success", "message": "Item successfully added to your wish list."}

    return redirect(URL('item_lists', 'wish_list', args=auth.user_id))
