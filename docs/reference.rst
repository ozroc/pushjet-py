Reference
=========

Interface
---------

Note that all methods can raise :exc:`~pushjet.RequestError` if the server somehow becomes unavailable.

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

.. autoexception:: pushjet.PushjetError
.. autoexception:: pushjet.AccessError
.. autoexception:: pushjet.NonexistentError
.. autoexception:: pushjet.SubscriptionError
.. autoexception:: pushjet.RequestError()
