@auth.requires_login()
def index():
    tags = db(db.tags.owner_id == auth.user.id).select()
    return dict(tags=tags)


def show():
    user_id = request.vars.user
    tags = db(db.tags.owner_id == user_id).select()
    user = db(db.auth_user.id == user_id).select()[0]

    return dict(tags=tags, user=user)

