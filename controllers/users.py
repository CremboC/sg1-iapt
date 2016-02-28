@auth.requires_login()
def index():
    return dict(users=db(db.auth_user.id > 0).select(db.auth_user.id, db.auth_user.username))
