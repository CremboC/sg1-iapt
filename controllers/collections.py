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

    form = SQLFORM(db.collections, record=collection, showid=False, deletable=True, submit_button='Update')

    if form.process().accepted:
        if request.vars.objects:
            objects_to_remove = [int(obj) for obj in request.vars.objects] or [request.vars.objects]

            query = db.object_collection.object_id.belongs(objects_to_remove)
            db(query).delete()

        session.flash = dict(status='success', message='Successfully updated collection.')
        return redirect(URL('collections', 'show', args=form.vars.id))

    return dict(collection=collection, form=form)
