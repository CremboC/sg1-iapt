def index():
    query_string = request.vars.query
    filtered = request.vars.filtered == "true" or False

    # fill filters
    types = db(db.types.id > 0).select()

    search_query = db.objects.name.contains(query_string)  # search by the query
    search_query &= db.objects.type_id == db.types.id  # join type info
    search_query &= db.objects.owner_id == db.auth_user.id  # join user info

    if filtered:
        if request.vars.types:
            search_query &= db.objects.type_id.belongs(request.vars.types)

    results = db(search_query).select()

    return dict(results=results, types=types, filtered=filtered)
