# aiohttp-mongodb-base

A base for aiohttp applications using MongoDB.

## Hosting

Docker is the preferred way to host an instance of the API.

Environment Variables:

* `EXAMPLE_PORT`: Configures the webserver port. Default is `8081`.
* `EXAMPLE_HOST`: Configures the webserver host. Default is `0.0.0.0`.
* `EXAMPLE_URI`: MongoDB connection URI. Default is `mongodb://mongo`.
* `EXAMPLE_DB`: MongoDB database name. Default is `EXAMPLE`.

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

No other sensitive information is stored with this IP address, besides information critical to operation like basic metrics and rate limit data.
