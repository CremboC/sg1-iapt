@auth.requires_login()
def index():
    user_id = next(iter(request.args), auth.user_id)
    is_me = user_id == auth.user_id
    user = db(db.auth_user.id == user_id).select().first()

    collection_query = db.collections.owner_id == user_id
    if not is_me:
        collection_query &= db.collections.private == False

    collections = db(collection_query).select()

    return dict(collections=collections, is_me=is_me, user=user)


@auth.requires_login()
def show():
    collection_id = request.args[0] or redirect(URL('collections', 'index'))

    collection = db(db.collections.id == collection_id).select().first()
    user = db(db.auth_user.id == collection.owner_id).select().first()
    is_owner = user.id == auth.user_id

    if collection.private and not is_owner:
        raise HTTP(404, "Error 404: Invalid request, collection does not exist")

    # TODO: Ask to log in / Redirect if collection not found / collection private

    return dict(collection=collection, user=user, is_owner=is_owner)


@auth.requires_login()
def edit():
    collection_id = request.args[0] or redirect(URL('collections', 'index'))

    collection = db(db.collections.id == collection_id).select().first()

    if collection.owner_id != auth.user_id:
        return redirect(URL('collections', 'index'))

    objects_in_collection = collection.objects()

    obj_query = db.objects.owner_id == auth.user_id
    obj_query &= ~db.objects.id.belongs([col.id for col in objects_in_collection])
    objects = db(obj_query).select()

    form = SQLFORM(db.collections, record=collection, showid=False, deletable=True, submit_button='Update')

    if form.process().accepted:
        if request.vars.objects_to_remove:
            objects_to_remove = [int(obj) for obj in request.vars.objects_to_remove] or [request.vars.objects_to_remove]

            query = db.object_collection.object_id.belongs(objects_to_remove)
            db(query).delete()

        if request.vars.new_objects:
            objects_to_add = [int(obj) for obj in request.vars.new_objects] or [request.vars.new_objects]

            for obj_id in objects_to_add:
                db.object_collection.insert(object_id=obj_id, collection_id=form.vars.id)

        session.flash = dict(status='success', message='Successfully updated collection.')
        return redirect(URL('collections', 'show', args=form.vars.id))

    return dict(collection=collection, form=form, objects=objects, objects_in_collection=objects_in_collection)
