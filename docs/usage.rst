========
Usage
========

To use mockingjay in a project::

    import mockingjay


---------------------
Create a mock service
---------------------

To create a mock service::

    service = mockingjay.MockService('https://api.stripe.com')

Then you can mock the endpoints using the builder::

    service.endpoint('GET /v1/tokens/some_token') \  # this creates a mock builder
        .should_return(200, {}, "{}")             \  # specify what it should return in one call
        .register()                                  # register the mock

After this is setup, you are able to make a request to the endpoint using any Python HTTP libraries::

    import requests

    response = requests.get('https://api.stripe.com/v1/tokens/some_token')
    print(response.text)    # should print out '{}'

You can also build up the mock in multiple steps using the fluent interface::

    service.endpoint('GET /v1/tokens/some_token') \
        .should_return_code(200)  \
        .should_return_header('content-type', 'application/json') \
        .should_return_body('{}') \
        .register()

------------------
Mock response body
------------------

You have a few options to specify the return body.

^^^^^^^^^^
Plain text
^^^^^^^^^^

The simplest way is to use plain text::

    service.endpoint('GET /v1/tokens/some_token') \
        .should_return_body('{}') \
        .register()

^^^^
JSON
^^^^

Use ``.should_return_json`` method if you want the response to be the json representation of a Python dictionary::

    service.endpoint('GET /v1/tokens/some_token') \
        .should_return_json({"id": "tok_166TGW2jyvokPAPl2u7xKy0v"}) \
        .register()

^^^^^^^^^^^^^^^^
Fixture Template
^^^^^^^^^^^^^^^^

The most flexible way to mock response is to use a template.  To use it, you first need to tell the mock service where to locate the response templates::

    service = mockingjay.MockService('https://api.stripe.com', fixture_root='/path/to/fixtures')

Then create your template.  Mockingjay supports Jinja2 templates out of the box, but it's just as easy to hook up with your favourite templating library.

A sample template::

    {
        "id": "{{ id }}"
    }

Mock the response using the template::

    service.endpoint('GET /v1/tokens/some_token') \
        .should_return_body_from_fixture('token.json', id="tok_166TGW2jyvokPAPl2u7xKy0v") \
        .register()
