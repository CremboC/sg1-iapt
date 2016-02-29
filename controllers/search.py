from collections import namedtuple

def index():
    query_string = request.vars.query or ''
    filtered = request.vars.filtered == "true" or False
    selected_types = []
    selected_statuses = []

    StatusRecord = namedtuple('Status', 'id name')

    statuses = [
        StatusRecord(id=0, name='Wanted'),
        StatusRecord(id=1, name='Had'),
        StatusRecord(id=2, name='InCol'),
    ]

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

        if request.vars.statuses:
            selected_statuses = [int(status) for status in request.vars.statuses] or [request.vars.statuses]
            search_query &= db.objects.status.belongs(selected_statuses)

    results = db(search_query).select()

    return dict(results=results,
                types=types, statuses=statuses,
                filtered=filtered,
                selected_types=selected_types, selected_statuses=selected_statuses)
