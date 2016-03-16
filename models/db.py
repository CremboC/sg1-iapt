# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig

## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(
        myconf.take('db.uri'),
        pool_size=myconf.take('db.pool_size',
                              cast=int),
        check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

    ## by default give a view/generic.extension to all actions from localhost
    ## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*']
## choose a style for forms
response.formstyle = myconf.take(
    'forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take(
    'smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.register_onaccept.append(
    lambda form: db.collections.insert(owner_id=form.vars.id, name='Unfiled', private=True))

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

auth.settings.extra_fields["auth_user"] = [
    Field("notifications", "boolean",
          default=False)
]
auth.define_tables(username=True, signature=False)

db.define_table("types",
                Field("name", "string")
                )

# Autoform Safe
db.define_table("objects",
                Field("owner_id", "reference auth_user",
                      readable=False,
                      writable=False,
                      default=auth.user_id),
                Field("type_id", "reference types",
                      required=True,
                      label="Type",
                      comment="What best describes your object?"),
                # -1: Deleted
                # 0: Own (InCol)
                # 1: Wish List
                # 2: Own, Willing to Trade (For Trade)
                Field("status", "integer",
                      default=0,
                      requires=IS_IN_SET([-1, 0, 1, 2])),  # TODO: Nice label
                Field("name", "string",
                      required=True,
                      requires=[IS_NOT_EMPTY(
                          error_message="An item must have a name assigned to it.")]),
                Field("currency_value", "float", label="Monetary value:", default=0.0, required=True,
                      comment="Your own assigned value in Great British Sterling"),
                Field("description", "text"),
                Field("summary", "string"),
                Field("image", "upload"),
                Field('created_on', 'datetime', default=request.now, writable=False,
                      readable=False),
                Field('updated_on', 'datetime', default=request.now, update=request.now, writable=False,
                      readable=False),
                )

db.objects.owner = Field.Lazy(
    'owner',
    lambda row: db.auth_user[row.objects.owner_id]
)

db.objects.type = Field.Lazy(
    'type',
    lambda row: db.types[row.objects.type_id]
)

db.objects.collections = Field.Lazy(
    'collections',
    lambda row: collections_and_objects(db.objects.id == row.objects.id).select(db.collections.ALL)
)

db.define_table("collections",
                Field("owner_id", "reference auth_user",
                      required=True, writable=False, readable=False, default=auth.user_id),
                Field("name", "string",
                      required=True),
                Field("private", "boolean",
                      default=False, label="Check this box to make the collection visible only to you."),
                Field('created_on', 'datetime', default=request.now, writable=False,
                      readable=False),
                Field('updated_on', 'datetime', default=request.now, update=request.now, writable=False,
                      readable=False),
                )


db.auth_user._after_insert.append(
    lambda row, id: db.collections.insert(owner_id=id, name='Unfiled', private=True))

db.collections.objects = Field.Method(
    'objects',
    lambda row, orderby=~db.objects.updated_on: collections_and_objects(
        (db.collections.id == row.collections.id) & (db.objects.status != -1)).select(db.objects.ALL, orderby=orderby)
)

db.collections.owner = Field.Lazy(
    'owner',
    lambda row: db.auth_user[row.collections.owner_id]
)

db.collections.name.requires = IS_NOT_EMPTY()


def move_items(s):
    id = (s.as_dict()['query']).as_dict()['second']
    db(db.object_collection.collection_id == id).update(collection_id=get_unfiled_collection(auth.user_id))

db.collections._before_delete.append(lambda s : move_items(s))


db.define_table("object_collection",
                Field("object_id", "reference objects",
                      required=True),
                Field("collection_id", "reference collections",
                      required=True)
                )

db.define_table("trades",
                Field("sender", "reference auth_user",
                      required=True),
                Field("receiver", "reference auth_user",
                      required=True),
                # 0: Pending
                # 1: Cancelled
                # 2: Rejected
                # 3: Accepted
                # 4: Modified
                Field("status", "integer",
                      required=True),
                Field("date_created", "datetime",
                      default=request.now),
                Field("superseded_by", "reference trades"),
                Field("seen", "boolean",
                      default=False),
                Field('created_on', 'datetime', default=request.now, writable=False,
                      readable=False),
                Field('updated_on', 'datetime', default=request.now, update=request.now, writable=False,
                      readable=False),
                )

# Note: Trade & Object should be unique, but this isn't
# inserted by users, so it'd be pointless to add a
# validator.
db.define_table("trades_sending",
                Field("trade_id", "reference trades",
                      required=True),
                Field("sent_object_id", "reference objects")
                )

db.define_table("trades_receiving",
                Field("trade_id", "reference trades",
                      required=True),
                Field("recv_object_id", "reference objects")
                )

collections_and_objects = db(
    (db.collections.id == db.object_collection.collection_id) & (db.objects.id == db.object_collection.object_id))
