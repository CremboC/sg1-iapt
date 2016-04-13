# Controller to display the collections index page & view and create collections


# Index page to display all of a user's collections
def index():
    user_id = next(iter(request.args), auth.user_id)
    is_me = user_id == auth.user_id
    user = db(db.auth_user.id == user_id).select().first()

    collection_query = db.collections.owner_id == user_id
    if not is_me:
        # Do not display other user's private collections
        collection_query &= db.collections.private == False

    collections = db(collection_query).select(orderby=translate_sortby(request.vars.sort, db.collections))

    return dict(collections=collections, is_me=is_me, user=user)


# Method to quickly create a collection for use the item create/edit pages
@auth.requires_login()
def quick_create():
    # If collection name is not a string
    if (request.vars.col_name is None) | (request.vars.col_name == ""):
        return str(-1)
    else:
        if request.vars.col_private is None:
            id = db.collections.insert(owner_id=auth.user_id, name=request.vars.col_name, private=False)
        else:
            id = db.collections.insert(owner_id=auth.user_id, name=request.vars.col_name, private=True)
        return str(id)


# Method to create a collection
@auth.requires_login()
def create():
    form = SQLFORM(db.collections)

    if form.process().accepted:
        session.flash = {"status": "success", "message": "Collection successfully created."}
        return redirect(URL('collections', 'show', args=form.vars.id))

    return dict(form=form)


# Method to display an individual collection
def show():
    collection_id = request.args[0] or redirect(URL('collections', 'index'))

    collection = db.collections[collection_id]
    # If collection does not exist display error
    if not collection:
        session.flash = {"status": "danger", "message": "Error: collection does not exist"}
        return redirect(URL('collections', 'index'))

    user = db.auth_user[collection.owner_id]
    is_owner = user.id == auth.user_id
    # Do not allow users to view another user's private collection
    if collection.private and not is_owner:
        session.flash = {"status": "danger",
                         "message": "Error: you cannot view a collection that is private and doesn't belong to you"}
        return redirect(URL('collections', 'index'))

    # Apply a sort on the objects
    if request.vars.sort:
        objects = collection.objects(translate_sortby(request.vars.sort, db.objects))
    else:
        objects = collection.objects()

    # Add fields for object status icon in the object partial
    for object in objects:
        add_in_trade_field(object)

    # Query to retrieve all objects
    obj_query = db.objects.owner_id == auth.user_id
    obj_query &= ~db.objects.id.belongs([col.id for col in objects])
    other_objects = db(obj_query).select(orderby=db.objects.name)

    return dict(collection=collection, user=user, is_owner=is_owner, items=objects, other_objects=other_objects)


# Controller to edit a collection's name, privacy
@auth.requires_login()
def edit():
    # If collection name is invalid
    if request.args[0] is None:
        session.flash = {"status": "danger", "message": "Error: collection does not exist"}
        return redirect(URL('collections', 'index'))

    collection_id = request.args[0]

    collection = db(db.collections.id == collection_id).select().first()
    # Do not allow editing another user's collections
    if collection.owner_id != auth.user_id:
        session.flash = {"status": "danger", "message": "Error: Cannot edit a collection that doesn't belong to you"}
        return redirect(URL('collections', 'index'))

    # Apply a sort on objects
    if request.vars.sort:
        objects_in_collection = collection.objects(translate_sortby(request.vars.sort, db.objects))
    else:
        objects_in_collection = collection.objects()

    is_unfiled = collection.name == "Unfiled"
    # Do not allow editing of the unfiled collection
    if is_unfiled:
        session.flash = {"status": "danger", "message": "Error: Cannot edit the Unfiled collection."}
        return redirect(URL('collections', 'index'))

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

    # Add data for status icon in object partial
    for object_id in objects_in_collection:
        add_in_trade_field(object_id)

    return dict(collection=collection, form=form,
                objects_in_collection=objects_in_collection, is_unfiled=is_unfiled)

# Method to add items to a collection
@auth.requires_login()
def add_items():
    if not request.vars.id:
        session.flash = dict(status='danger', message='Error: no item ids specified')
        return redirect(URL("collections", "index"))

    collection_id = int(request.vars.id)

    if request.vars.new_objects:
        for obj_id in maybe_list(request.vars.new_objects):
            # Add each object to the collection
            link_object_collections(obj_id, collection_id)

        session.flash = dict(status='success', message='Successfully updated collection with new items.')

    return redirect(URL('collections', 'show', args=collection_id))


# Method to remove items from a collection
@auth.requires_login()
def remove_items():
    if not request.vars.id:
        session.flash = dict(status='danger', message='Error: no item ids specified')
        return redirect(URL("collections", "index"))

    collection_id = int(request.vars.id)

    if request.vars.objects_to_remove:
        objects_to_remove = maybe_list(request.vars.objects_to_remove)
        # Remove items from collections
        query = db.object_collection.object_id.belongs(objects_to_remove)
        db(query).delete()

        # If items are in no collections, add them to unfiled collection
        for object_id in objects_to_remove:
            num_cols = len(db(db.object_collection.object_id == object_id).select())
            if num_cols == 0:
                owner_id = get_owner_id(object_id)
                unfiled_col_id = get_unfiled_collection(owner_id)
                link_object_collections(object_id, unfiled_col_id)
        session.flash = dict(status='success', message='Successfully removed items from collection.')

    return redirect(URL('collections', 'show', args=collection_id))
