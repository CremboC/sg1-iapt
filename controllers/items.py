@auth.requires_login()
def create():
    form = SQLFORM(db.objects)
    types = db(db.types.id > 0).select()

    if form.process().accepted:
        response.flash = {"status": "success", "message": "Item successfully saved"}
    elif form.errors:
        response.flash = {"status": "danger", "message": "An error has occured. See below."}

    return dict(form=form, types=types)


@auth.requires_login()
def show():
    item_id = request.vars[0] or redirect(URL('default', 'index'))
    item = db(db.objects.id == item_id).select().first()

    return dict(item=item)
