def index():
    db.auth_user.truncate()
    db.auth_user.insert(first_name="first", last_name="last", email="A@A.com", username="username1",
        password="pbkdf2(1000,20,sha512)$9faa1d46cb1f1519$6111cb586aaeae66958fc9b521cf4efda7d72443")
    db.auth_user.insert(first_name="second", last_name="last", email="A@A.com", username="username2",
        password="pbkdf2(1000,20,sha512)$a5eabdb2efc9cdad$9360417c8ad0de06e013a827664abea802fb78de")

    db.types.truncate()
    db.types.insert(name='General')
    db.types.insert(name='Advertising & brands')
    db.types.insert(name='Architectural')
    db.types.insert(name='Art')
    db.types.insert(name='Books, Magazines & prints')
    db.types.insert(name='Clothing, fabric & textiles')
    db.types.insert(name='Coins, currency & stamps')
    db.types.insert(name='Film & Television')
    db.types.insert(name='Glass and pottery')
    db.types.insert(name='Household items')
    db.types.insert(name='Memorabilia')
    db.types.insert(name='Music')
    db.types.insert(name='Nature & Animals')
    db.types.insert(name='Sports')
    db.types.insert(name='Technology')
    db.types.insert(name='Themed')
    db.types.insert(name='Toys and Games')

    db.collections.truncate()
    db.collections.insert(owner_id=1, name='Carrots', private=False)
    db.collections.insert(owner_id=1, name='Coins', private=True)
    db.collections.insert(owner_id=2, name='Collection Three', private=False)
    db.collections.insert(owner_id=2, name='Collection', private=True)

    db.objects.truncate()
    db.object_collection.truncate()
    #Not tradable
    db.objects.insert(owner_id=1, type_id=1, status=1, name='Golden Carrot', summary='A magical carrot found down a rabbit hole',
        description='You\'l need some belief for this one, this carrot is filled with magical powers! A great addition to any collection', currency_value=500.0, image='objects.image.817cd3ab9d568442.636172726f742e6a7067.jpg')
    db.object_collection.insert(object_id=1, collection_id=1)

    db.objects.insert(owner_id=1, type_id=1, status=2, name='A carrot', summary='A normal carrot',
        description='A more natural carrot, but you can eat this one!', currency_value=1.0, image='objects.image.817cd3ab9d568442.636172726f742e6a7067.jpg')
    db.object_collection.insert(object_id=2, collection_id=1)


    db.objects.insert(owner_id=1, type_id=7, status=1, name='A common pound coin', summary='A pound coin from the British Mint.',
        description='This is an unbelievably common coin, yet I still collect thousands of these!', currency_value=5.0, image='objects.image.a89ad6219dfb0f20.636f696e312e6a7067.jpg')


    db.objects.insert(owner_id=2, type_id=5, status=2, name='Comic book artists', summary='A short collection of great graphic art.',
        description='A collection of the best of the golden era\'s graphic art.', currency_value=4.0, image='objects.image.add0002dc8d85839.636f6d6963312e6a7067.jpg')

    db.objects.insert(owner_id=1, type_id=1, status=0, name='A carrot', summary='A normal carrot',
        description='I\'m trying to find a golden magic carrot, does anyone have any to trade?', currency_value=1.0, image='objects.image.817cd3ab9d568442.636172726f742e6a7067.jpg')


    db.trades.truncate()
    db.trades.insert(sender=1, receiver=2, status=0)

    db.trades_sending.truncate()
    db.trades_sending.insert(trade_id=1, sent_object_id=1)

    db.trades_receiving.truncate()
    db.trades_receiving.insert(trade_id=1, recv_object_id=2)
    response.flash = T("Truncated & re-inserted database.")
    return {}
