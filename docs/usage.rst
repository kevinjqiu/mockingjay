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

--------------
Assert request 
--------------

Mockingjay also has the ability to automatically assert certain aspects of the request.  For example, if your application is talking to the Stripe API, and you want to mock out the charge endpoint.  As shown above, it's easy to do so with the ``should_return_*`` methods to build up the response, but you may also want to assert that the request is made with certain authentication headers or the request body, so that you know your code is calling the external API with the right parameters and so on.

To use the automatic request assertion, you can specify what the request should look like during the endpoint building stage::

    service.endpoint('POST /v1/charge') \
        .expect_request_user('sk_test_BQokikJOvBiI2HlWgH4olfQ2') \
        .expect_request_body('amount=400&currency=usd') \
        .register()
    service.assert_requests_matched()

``assert_requests_matched`` call will look at the requests made while httpretty is activated, find the matching requests based on the URI and check if the body matches the expected.
