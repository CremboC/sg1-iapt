def index():
    query_string = request.vars.query or ''
    filtered = request.vars.filtered == "true" or False
    selected_types = []

    # fill filters
    types = db(db.types.id > 0).select()

    search_query = db.objects.name.contains(query_string)  # search by the query
    search_query &= db.objects.type_id == db.types.id  # join type info
    search_query &= db.objects.owner_id == db.auth_user.id  # join user info

    if filtered:
        if request.vars.types:
            selected_types = [int(type) for type in request.vars.types] or [request.vars.types]
            search_query &= db.objects.type_id.belongs(selected_types)

        if request.vars.user_id != '':
            search_query &= db.objects.owner_id == request.vars.user_id

        if request.vars.min_value != '':
            search_query &= db.objects.currency_value >= request.vars.min_value

        if request.vars.max_value != '':
            search_query &= db.objects.currency_value <= request.vars.max_value

    results = db(search_query).select()

    return dict(results=results, types=types, filtered=filtered, selected_types=selected_types)
