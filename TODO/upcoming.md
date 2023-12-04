# Roadmap

Sketch database structure at https://app.quickdatabasediagrams.com/#/d/4IsUDl

Write the models.

Another DB abstraction layer can evolve naturally later. Working directly with the Session works ATM and is more explicit.

FastAPI Users nice library for handling auth. It provides login/reset password/register routes.
JWT

Divide routes using Routers. A router can have a dependency. That way, auth can be enforced for a group of paths.

Sentry for performance and error reporting
