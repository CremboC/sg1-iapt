def index():
    user_id = next(iter(request.args), auth.user_id)
    is_me = user_id == auth.user_id
    user = db(db.auth_user.id == user_id).select().first()

    collection_query = db.collections.owner_id == user_id
    if not is_me:
        collection_query &= db.collections.private == False

    collections = db(collection_query).select(orderby=translate_sortby(request.vars.sort, db.collections))

    return dict(collections=collections, is_me=is_me, user=user)


@auth.requires_login()
def quick_create():
    if (request.vars.col_name is None) | (request.vars.col_name == ""):
        return str(-1)
    else:
        if request.vars.col_private is None:
            id = db.collections.insert(owner_id=auth.user_id, name=request.vars.col_name, private=False)
        else:
            id = db.collections.insert(owner_id=auth.user_id, name=request.vars.col_name, private=True)
        return str(id)


@auth.requires_login()
def create():
    # Additional sub-method to handle collection creation from create/edit items
    form = SQLFORM(db.collections)

    if form.process().accepted:
        session.flash = {"status": "success", "message": "Collection successfully created."}
        return redirect(URL('collections', 'show', args=form.vars.id))

    return dict(form=form)


def show():
    collection_id = request.args[0] or redirect(URL('collections', 'index'))

    collection = db.collections[collection_id]
    if not collection:
        session.flash = {"status": "danger", "message": "Error: collection does not exist"}
        return redirect(URL('collections', 'index'))

    user = db.auth_user[collection.owner_id]
    is_owner = user.id == auth.user_id
    if collection.private and not is_owner:
        session.flash = {"status": "danger",
                         "message": "Error: you cannot view a collection that is private and doesn't belong to you"}
        return redirect(URL('collections', 'index'))

    if request.vars.sort:
        objects = collection.objects(translate_sortby(request.vars.sort, db.objects))
    else:
        objects = collection.objects()

    for object in objects:
        add_in_trade_field(object)

    obj_query = db.objects.owner_id == auth.user_id
    obj_query &= ~db.objects.id.belongs([col.id for col in objects])
    other_objects = db(obj_query).select(orderby=db.objects.name)

    return dict(collection=collection, user=user, is_owner=is_owner, items=objects, other_objects=other_objects)


@auth.requires_login()
def edit():
    if request.args[0] is None:
        session.flash = {"status": "danger", "message": "Error: collection does not exist"}
        return redirect(URL('collections', 'index'))

    collection_id = request.args[0]

    collection = db(db.collections.id == collection_id).select().first()

    if collection.owner_id != auth.user_id:
        session.flash = {"status": "danger", "message": "Error: Cannot edit a collection that doesn't belong to you"}
        return redirect(URL('collections', 'index'))

    if request.vars.sort:
        objects_in_collection = collection.objects(translate_sortby(request.vars.sort, db.objects))
    else:
        objects_in_collection = collection.objects()

    is_unfiled = collection.name == "Unfiled"

    if is_unfiled:
        db.collections.name.writable = False
        db.collections.private.writable = False

    form = SQLFORM(db.collections, record=collection, showid=False, deletable=True, submit_button='Update')

    if form.process().accepted:
        if not is_unfiled and form.vars.delete_this_record:
            # cleanup linking table
            query = db.object_collection.collection_id == form.vars.id
            db(query).delete()

            # move all items in this collection to the unfiled
            unfiled = get_unfiled_collection()
            for obj in objects_in_collection:
                link_object_collections(obj.id, unfiled.id)

            session.flash = dict(status='success', message='Successfully deleted collection.')
            return redirect(URL('collections', 'index'))

        session.flash = dict(status='success', message='Successfully updated collection.')
        return redirect(URL('collections', 'show', args=form.vars.id))

    for object_id in objects_in_collection:
        add_in_trade_field(object_id)

    return dict(collection=collection, form=form,
                objects_in_collection=objects_in_collection, is_unfiled=is_unfiled)


@auth.requires_login()
def add_items():
    if not request.vars.id:
        return redirect(URL("collections", "index"))

    collection_id = int(request.vars.id)

    if request.vars.new_objects:
        for obj_id in maybe_list(request.vars.new_objects):
            link_object_collections(obj_id, collection_id)

        session.flash = dict(status='success', message='Successfully updated collection with new items.')

    return redirect(URL('collections', 'show', args=collection_id))


@auth.requires_login()
def remove_items():
    if not request.vars.id:
        return redirect(URL("collections", "index"))

    collection_id = int(request.vars.id)

    if request.vars.objects_to_remove:
        objects_to_remove = maybe_list(request.vars.objects_to_remove)

        query = db.object_collection.object_id.belongs(objects_to_remove)
        db(query).delete()

        for object_id in objects_to_remove:
            num_cols = len(db(db.object_collection.object_id == object_id).select())
            if num_cols == 0:
                owner_id = get_owner_id(object_id)
                unfiled_col_id = get_unfiled_collection(owner_id)
                link_object_collections(object_id, unfiled_col_id)
        session.flash = dict(status='success', message='Successfully removed items from collection.')

    return redirect(URL('collections', 'show', args=collection_id))
