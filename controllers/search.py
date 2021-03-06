from collections import namedtuple


def index():
    query_string = request.vars.query or ''
    page = request.vars.page or 'items'
    filtered = request.vars.filtered == "true" or False

    returns = dict()

    if page == 'items':
        (search_query, selected_statuses, selected_types, types, statuses) = _items(query_string, filtered)
        results = db(search_query).select(orderby=translate_sortby(request.vars.sort, db.objects))

        # check if item is not private
        results = [result for result in results
                   if not item_is_private(result) or (auth.user_id and result.owner_id == auth.user_id)]
        for item in results:
            add_in_trade_field(item)

        returns = dict(
            results=results,
            types=types, statuses=statuses,
            selected_types=selected_types, selected_statuses=selected_statuses
        )

    elif page == 'collections':
        (search_query) = _collections(query_string, filtered)
        results = db(search_query).select(orderby=translate_sortby(request.vars.sort, db.collections))

        returns = dict(results=results)

    elif page == 'users':
        (search_query) = _users(query_string)

        results = db(search_query).select()

        returns = dict(results=results)

    returns.update(dict(page=page, filtered=filtered))
    return returns


def _items(query_string, filtered):
    selected_types = []
    selected_statuses = []
    StatusRecord = namedtuple('Status', 'id name')

    statuses = [
        StatusRecord(id=0, name='Non-Tradable'),
        StatusRecord(id=1, name='Wish List'),
        StatusRecord(id=2, name='For Trade'),
    ]

    # fill filters
    types = db(db.types.id > 0).select()

    search_query = db.objects.name.contains(query_string)  # search by the query
    search_query &= db.objects.status != -1

    if filtered:
        if request.vars.types:
            selected_types = maybe_list(request.vars.types)
            search_query &= db.objects.type_id.belongs(selected_types)

        if request.vars.user:
            user = db(db.auth_user.username == request.vars.user).select(db.auth_user.ALL).first()
            if user:
                search_query &= db.objects.owner_id == user.id
            else:
                search_query &= db.objects.owner_id == -1

        if request.vars.min_value and request.vars.min_value != "0":
            search_query &= db.objects.currency_value >= request.vars.min_value

        if request.vars.max_value and request.vars.min_value != "0":
            search_query &= db.objects.currency_value <= request.vars.max_value

        if request.vars.statuses:
            selected_statuses = maybe_list(request.vars.statuses)
            search_query &= db.objects.status.belongs(selected_statuses)

        if request.vars.only_other:
            search_query &= ~(db.objects.owner_id == auth.user_id)

    return search_query, selected_statuses, selected_types, types, statuses


def _collections(query_string, filtered):
    search_query = db.collections.name.contains(query_string)
    search_query &= db.collections.private == False

    if filtered:
        if request.vars.user:
            user = db(db.auth_user.username == request.vars.user).select(db.auth_user.ALL).first()
            if user:
                search_query &= db.collections.owner_id == user.id
            else:
                search_query &= db.collections.owner_id == -1

        if request.vars.only_other:
            search_query &= ~(db.collections.owner_id == auth.user_id)

    return search_query


def _users(query_string):
    search_query = db.auth_user.username.contains(query_string)

    return search_query
