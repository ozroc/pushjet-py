Getting started
===============

First of all, install the Pushjet Python client. This can be done by simply running ``pip install pushjet``. Then ``import pushjet``, and you're all set to start. Something you should know is that "message" is Pushjet's term for a notification, since they're generic and could just as well be presented as... well... not notifications.

Creating and using a service
----------------------------

All communication with devices is done through services. These can be created frivolously without problem. It's fairly simple, check it out::

    service = pushjet.Service("Cool name", "http://example.com/icon.png")
    # At this point, service.public_key can be used to subscribe to it.
    service.send(
        "Hey, check it out, there's a sale on!", # Message
        "SALE!",                                 # Title
        "http://example.com/item_on_sale.html"   # Link
    )

    # To later retrieve the service, store the service.secret_key somewhere
    # and initialize the service as following.
    service = pushjet.Service(secret_key)

More methods and properties can be found in the reference for the :class:`~pushjet.Service` class.

Subscribing to a service and getting messages
---------------------------------------------

Devices can subscribe to services using the :class:`~pushjet.Device` class. These don't need to be registered - you can simply start using a random ID at any time. Common usage of the class looks like this::

    import uuid
    device = pushjet.Device(uuid.uuid4())

    # Both of these work just fine.
    device.subscribe(service)
    device.subscribe("43c2-9317cc-eb3c7a3c4854-3e9b6-59e9e5a10")

    for message in device.get_messages():
        print("Message from {service}:".format(service=message.service.name))
        if message.title:
            print(message.title)
        print(message.message)
        if message.link:
            print(message.link)

For complete information (for example on getting the services a device is subscribed to), see the reference for the :class:`~pushjet.Device`, :class:`~pushjet.Subscription`, and :class:`~pushjet.Message` classes.

Notes on using a custom API instance
------------------------------------

If you want to use another Pushjet server, the module lets you do that too. Simply use the :class:`~pushjet.Api` class and use all the other classes as members of it, as following::

    api = pushjet.Api("https://mypushjetapi.example.com/")
    # You can then use:
    api.Service("e1d669b8963b2f52a3e23581126365d2")
    api.Device("036a256d-1fb7-453a-aa56-f6720ef7fd6c")

