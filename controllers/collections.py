@auth.requires_login()
def index():
    tags = db(db.tags.owner_id == auth.user.id).select()
    return dict(tags=tags)


def show():

    return dict()

