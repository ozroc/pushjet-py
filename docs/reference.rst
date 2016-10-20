Reference
=========

Interface
---------

Note that all methods can raise :exc:`~pushjet.RequestError` if the server somehow becomes unavailable. They can also raise :exc:`~pushjet.ServerError` if there's a bug in the server, but that's fairly unpredictable and in a perfect world would never be able to happen.

.. autoclass:: pushjet.Service
    :members:
.. autoclass:: pushjet.Device
    :members:
.. autoclass:: pushjet.Subscription()
    :members:
.. autoclass:: pushjet.Message()
    :members:

Custom API instances
--------------------

.. autoclass:: pushjet.Api
    :members:

Exceptions
----------

.. autoexception:: pushjet.PushjetError()
.. autoexception:: pushjet.AccessError()
.. autoexception:: pushjet.NonexistentError()
.. autoexception:: pushjet.SubscriptionError()
.. autoexception:: pushjet.RequestError()
.. autoexception:: pushjet.ServerError()
