

# Controller used to re-set the database for the TBUE and later evaluation by examiners
def index():
    db.auth_user.truncate()
    db.collections.truncate()
    db.objects.truncate()
    db.object_collection.truncate()
    db.trades.truncate()
    db.trades_sending.truncate()
    db.trades_receiving.truncate()

    db.auth_user.insert(first_name="Annie", last_name="last", email="A@A.com", username="annie",
                        password="pbkdf2(1000,20,sha512)$86b33bd0d2e7802d$a58055d25c9586c5977d60ae8682baf8fb8b0b6b")

    db.auth_user.insert(first_name="Bob", last_name="last", email="A@A.com", username="bob",
                        password="pbkdf2(1000,20,sha512)$86b33bd0d2e7802d$a58055d25c9586c5977d60ae8682baf8fb8b0b6b")

    db.auth_user.insert(first_name="Jack", last_name="last", email="A@A.com", username="jack",
                        password="pbkdf2(1000,20,sha512)$86b33bd0d2e7802d$a58055d25c9586c5977d60ae8682baf8fb8b0b6b")

    db.types.truncate()
    db.types.insert(name='General') #1
    db.types.insert(name='Advertising & brands') #2
    db.types.insert(name='Architectural') #3
    db.types.insert(name='Art') #4
    db.types.insert(name='Books, Magazines & prints') #5
    db.types.insert(name='Clothing, fabric & textiles') #6
    db.types.insert(name='Coins, currency & stamps') #7
    db.types.insert(name='Film & Television') #8
    db.types.insert(name='Glass and pottery') #9
    db.types.insert(name='Household items') #10
    db.types.insert(name='Memorabilia') #11
    db.types.insert(name='Music') #12
    db.types.insert(name='Nature & Animals') #13
    db.types.insert(name='Sports') #14
    db.types.insert(name='Technology') #15
    db.types.insert(name='Themed') #16
    db.types.insert(name='Toys and Games') #17

    db.collections.insert(owner_id=1, name="old clothes", private=False) #4
    db.collections.insert(owner_id=3, name="media", private=False) #5
    db.collections.insert(owner_id=3, name="gadgets", private=False) #6
    db.collections.insert(owner_id=1, name="vases", private=False) #7


    #Annie objects
    db.objects.insert(owner_id=1, type_id=6, status=2, name='Red Dress', currency_value=30.0, summary='Red party dress',
                      description='strapless red dress from french connection', image='objects.image.80fb30d10234f5eb.7265642064726573732e6a706567.jpeg')
    db.object_collection.insert(object_id=1, collection_id=4)

    db.objects.insert(owner_id=1, type_id=6, status=0, name='Blue Jeans', currency_value=10.0, summary='blue skinny jeans',
                      description='some cheap blue skinny jeans from new look', image='objects.image.b97f08e575344d77.626c75656a65616e732e6a7067.jpg')
    db.object_collection.insert(object_id=2, collection_id=4)

    db.objects.insert(owner_id=1, type_id=6, status=2, name='Grey cardigan', currency_value=20.0, summary='knitted grey cardigan',
                      description='a knitted grey cardigan, hand-knitted by my grandmother', image='objects.image.8871bb1135128ede.6772657920636172646967616e2e6a706567.jpeg')
    db.object_collection.insert(object_id=3, collection_id=4)

    db.objects.insert(owner_id=1, type_id=15, status=2, name='iPhone 5', currency_value=150.0, summary='white 32gb iphone 5',
                      description='white iphone 5 which is fully working with a 32gb memory and no scratches on the screen or casing', image='objects.image.85b1a73ffaebf95e.6970686f6e6520352e6a706567.jpeg')
    db.object_collection.insert(object_id=4, collection_id=4)

    db.objects.insert(owner_id=1, type_id=9, status=0, name='Antique vase', currency_value=65, summary='old vase', description='gold coloured antique vase - very rare', image='objects.image.813196559b058f09.766173652e6a7067.jpg')
    db.object_collection.insert(object_id=5, collection_id=7)

    db.objects.insert(owner_id=1, type_id=9, status=2, name='Glass vase', currency_value=3, summary='modern glass vase', description='plain glass vase, not too heavy perfect for medium sized arrangements', image='objects.image.9ae4cf51673c0a92.676c61737320766173652e6a7067.jpg')
    db.object_collection.insert(object_id=6, collection_id=7)

    #Bob
    db.objects.insert(owner_id=2, type_id=10, status=2, name='Desk chair', currency_value=70.0, summary='chair for computer desk',
                      description='The seat height of the chair can be adjusted from 440mm -520mm, allowing you to adjust the chair to give you the optimum working height. It is a dark red colour and is perfect for use in front of a computer', image='objects.image.903db7462241a973.6465736b2063686169722e6a706567.jpeg')
    db.object_collection.insert(object_id=7, collection_id=2)

    db.objects.insert(owner_id=2, type_id=10, status=2, name='Coffee table', currency_value=120.0, summary='wooden coffee table',
                      description='wooden coffee table which looks great in any living room', image='objects.image.b8b5db81540cdfdb.636f66666565207461626c652e6a706567.jpeg')
    db.object_collection.insert(object_id=8, collection_id=2)

    #Jack

    db.objects.insert(owner_id=3, type_id=8, status=2, name='Friends blu ray box set', currency_value=30.0, summary='10 friends blu ray discs',
                      description='Synopsis: All 10 Seasons. 236 original broadcast episodes on 21 discs completely remastered. Includes 2 Hours of all-new bonus content featuring: Unaired footage, New one-hour documentary, New interviews, Never before released cast appearances and more. Over 20 total hours of extras. ', image='objects.image.803de930ba7dbcdc.667269656e647320626f78207365742e6a7067.jpg')
    db.object_collection.insert(object_id=9, collection_id=5)

    db.objects.insert(owner_id=3, type_id=8, status=2, name='Star wars: a new hope dvd', currency_value=10.0, summary='dvd of a new hope',
                      description='The Imperial Forces -- under orders from cruel Darth Vader (David Prowse) -- hold Princess Leia (Carrie Fisher) hostage, in their efforts to quell the rebellion against the Galactic Empire. Luke Skywalker (Mark Hamill) and Han Solo (Harrison Ford), captain of the Millennium Falcon, work together.', image='objects.image.92ec11fe45d7c23f.7374617220776172732061206e657720686f70652e6a706567.jpeg')
    db.object_collection.insert(object_id=10, collection_id=5)

    db.objects.insert(owner_id=3, type_id=8, status=2, name='Toy story dvd', currency_value=5.0, summary='dvd of the first toy story film',
                      description='pixar\'s first full length animated feature', image='objects.image.b2f0850ff0ac6915.746f792073746f7279206476642e6a706567.jpeg')
    db.object_collection.insert(object_id=11, collection_id=5)

    db.objects.insert(owner_id=3, type_id=12, status=2, name='Adele 25 cd', currency_value=5.5, summary='25 cd',
                      description='music cd of Adele\'s latest album, 25', image='objects.image.a4d37fb614b7c41d.6164656c652032352063642e6a706567.jpeg')
    db.object_collection.insert(object_id=12, collection_id=5)

    db.objects.insert(owner_id=3, type_id=15, status=2, name='iPhone 5', currency_value=180, summary='black 16gb iphone 5',
                      description='black iphone 5 which is fully working with a 16gb memory and no scratches', image='objects.image.94b52f157eb86559.6970686f6e65203520626c61636b2e6a7067.jpg')
    db.object_collection.insert(object_id=13, collection_id=6)

    db.objects.insert(owner_id=3, type_id=15, status=2, name='Cassette player', currency_value=60, summary='silver tape player',
                      description='retro audio cassette player straight from 1997', image='objects.image.b4c56ddbaa2e5920.636173736574746520706c617965722e6a7067.jpg')
    db.object_collection.insert(object_id=14, collection_id=6)

    db.objects.insert(owner_id=3, type_id=15, status=2, name='Samsung S6 Edge', currency_value=300, summary='s6 edge in black',
                      description='black samsung s6 with curved edge screen', image='objects.image.a846284e45b69cc2.733620656467652e6a7067.jpg')
    db.object_collection.insert(object_id=15, collection_id=6)

    # db.objects.insert(owner_id=, type_id=, status=, name=, currency_value=, summary=,
    #                   description=, image=)
    # db.object_collection.insert(object_id=, collection_id=)

    db.trades.insert(sender=3, receiver=1, status=3)
    db.trades_sending.insert(trade_id=1, sent_object_id=1)
    db.trades_receiving.insert(trade_id=1, recv_object_id=9)


    db.trades.insert(sender=3, receiver=1, status=0, seen=False)
    db.trades_sending.insert(trade_id=2, sent_object_id=9)
    db.trades_receiving.insert(trade_id=2, recv_object_id=1)

    db.trades.insert(sender=3, receiver=1, status=0, seen=False)
    db.trades_sending.insert(trade_id=3, sent_object_id=14)
    db.trades_receiving.insert(trade_id=3, recv_object_id=6)

    response.flash = T("Truncated & re-inserted database.")
    return {}