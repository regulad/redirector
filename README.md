# redirector

A simple redirection tool that can be used to redirect users to a different page, as well as logging IP addresses.

## Hosting

Docker is the preferred way to host an instance of the API.

Environment Variables:

* `REDIRECT_PORT`: Configures the webserver port. Default is `8081`.
* `REDIRECT_HOST`: Configures the webserver host. Default is `0.0.0.0`.
* `REDIRECT_URI`: MongoDB connection URI. Default is `mongodb://mongo`.
* `REDIRECT_DB`: MongoDB database name. Default is `REDIRECT`.
* `REDIRECT_DISCORD_WEBHOOK`: Discord webhook URL. You can make one yourself, or omit it and not use it.

## API

### Limiting

To protect against abuse and optimize performance, the API enforces some rate-limits.

**Every hour**:

* You may make 90 requests.
* Each request may be 20 megabytes in size or smaller.

If you exceed your 90 requests per hour, you will be unable to make any more requests until time expires.

Three headers are sent back in each response:

* `X-RateLimit-Limit`: The maximum amount of requests you can make in one period. By defualt, this is 90.
* `X-RateLimit-Remaining`: The remaining requests in the current period.
* `X-RateLimit-Reset`: Time until the end of the period, in seconds.

### Privacy

IP addresses are stored in the `users` collection of the database.

No other sensitive information is stored with this IP address, besides information critical to operation like basic
metrics and rate limit data.

## Use

You can post to `/{id}` with a JSON body containing the following fields:

```json
{
    "to": "https://example.com/"
}
```

Now, when you get to `/{id}`, you will get a redirect to `https://example.com/`.
