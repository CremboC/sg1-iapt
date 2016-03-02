@auth.requires_login()
def index():
    collections = db(db.collections.owner_id == auth.user.id).select()
    return dict(collections=collections)


def show():
    user_id = request.vars.user
    collections = db(db.collections.owner_id == user_id).select()
    user = db(db.auth_user.id == user_id).select()[0]

    return dict(collections=collections, user=user)

