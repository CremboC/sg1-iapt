# Returns users for auto-complete feature
def index():
    query = db.auth_user.id > 0
    if auth.is_logged_in():
        query = db.auth_user.id != int(request.vars.ignore)

    return dict(users=db(query).select(db.auth_user.id, db.auth_user.username))
