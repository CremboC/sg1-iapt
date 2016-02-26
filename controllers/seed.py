def index():
    db.auth_user.truncate()
    db.auth_user.insert(first_name="first", last_name="last", email="A@A.com", username="username1",
		password="pbkdf2(1000,20,sha512)$9faa1d46cb1f1519$6111cb586aaeae66958fc9b521cf4efda7d72443")
    db.auth_user.insert(first_name="second", last_name="last", email="A@A.com", username="username2",
		password="pbkdf2(1000,20,sha512)$a5eabdb2efc9cdad$9360417c8ad0de06e013a827664abea802fb78de")

    db.types.truncate()
    db.types.insert(name='General')
    db.types.insert(name='Comics')

    db.objects.truncate()
    db.objects.insert(owner_id=1, type_id=1, status=2, private=False, name='object1a', summary='Summary',
		description='Description', currency_value=5.0)
    db.objects.insert(owner_id=2, type_id=1, status=2, private=False, name='object2a', summary='Summary',
		description='Description', currency_value=4.0)

    db.objects.insert(owner_id=1, type_id=1, status=2, private=False, name='object1b', summary='Summary',
		description='Description', currency_value=5.0)
    db.objects.insert(owner_id=2, type_id=1, status=2, private=False, name='object2b', summary='Summary',
		description='Description', currency_value=4.0)

    db.objects.insert(owner_id=2, type_id=2, status=2, private=False, name='comic2a', summary='Summary',
		description='Description', currency_value=10.0)

    db.trades.truncate()
    db.trades.insert(sender=1, receiver=2, status=0)

    db.trades_sending.truncate()
    db.trades_sending.insert(trade_id=1, sent_object_id=1)

    db.trades_receiving.truncate()
    db.trades_receiving.insert(trade_id=1, recv_object_id=2)
    response.flash = T("Truncated and re-inserted database.")
    return {}