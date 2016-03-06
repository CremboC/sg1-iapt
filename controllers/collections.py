@auth.requires_login()
def index():
    user_id = request.vars.user or auth.user_id
    collections = db(db.collections.owner_id == user_id).select()
    return dict(collections=collections)


@auth.requires_login()
def show():
    collection_id = request.args[0] or redirect(URL('collections', 'index'))
    collection = db(db.collections.id == collection_id).select().first()
    user = db(db.auth_user.id == collection.owner_id).select().first()
    is_owner = user.id == auth.user_id

    return dict(collection=collection, user=user, is_owner=is_owner)


@auth.requires_login()
def edit():
    collection_id = request.args[0] or redirect(URL('collections', 'index'))

    collection = db(db.collections.id == collection_id).select().first()

    if collection.owner_id != auth.user_id:
        return redirect(URL('collections', 'index'))

    form = SQLFORM(db.collections, record=collection, showid=False, deletable=True, submit_button='Update')

    return dict(collection=collection, form=form)
