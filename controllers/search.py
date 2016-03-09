from collections import namedtuple


# TODO: Check privacy of items before returning
def index():
    query_string = request.vars.query or ''
    page = request.vars.page or 'items'
    filtered = request.vars.filtered == "true" or False

    returns = dict()

    if page == 'items':
        (search_query, selected_statuses, selected_types, types, statuses) = _items(query_string, filtered)
        results = db(search_query).select()

        returns = dict(
            results=results,
            types=types, statuses=statuses,
            selected_types=selected_types, selected_statuses=selected_statuses
        )

    elif page == 'collections':
        (search_query) = _collections(query_string, filtered)
        results = db(search_query).select()

        returns = dict(results=results)

    elif page == 'users':
        (search_query) = _users(query_string, filtered)

        results = db(search_query).select()

        returns = dict(results=results)

    returns.update(dict(page=page, filtered=filtered))
    return returns


def _items(query_string, filtered):
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

    if filtered:
        if request.vars.types:
            selected_types = [int(type) for type in request.vars.types] or [request.vars.types]
            search_query &= db.objects.type_id.belongs(selected_types)

        if request.vars.user_id:
            search_query &= db.objects.owner_id == request.vars.user_id

        if request.vars.min_value:
            search_query &= db.objects.currency_value >= request.vars.min_value

        if request.vars.max_value:
            search_query &= db.objects.currency_value <= request.vars.max_value

        if request.vars.statuses:
            selected_statuses = [int(status) for status in request.vars.statuses] or [request.vars.statuses]
            search_query &= db.objects.status.belongs(selected_statuses)

    return search_query, selected_statuses, selected_types, types, statuses


def _collections(query_string, filtered):
    search_query = db.collections.name.contains(query_string)
    search_query &= db.collections.private == False

    if filtered:
        if request.vars.user_id != '':
            search_query &= db.collections.owner_id == request.vars.user_id

    return search_query


def _users(query_string, filtered):
    search_query = db.auth_user.username.contains(query_string)

    return search_query
