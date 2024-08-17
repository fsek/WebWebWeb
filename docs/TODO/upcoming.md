# Roadmap

Sketch database structure at https://app.quickdatabasediagrams.com/

Write the models.

Another DB abstraction layer can evolve naturally later. Working directly with the Session works ATM and is more explicit.

FastAPI Users nice library for handling auth. It provides login/reset password/register routes.
JWT

Divide routes using Routers. A router can have a dependency. That way, auth can be enforced for a group of paths.

Sentry for performance and error reporting.

## Background tasks

What are some background tasks we need?

Find and suggest a library or if FastAPI docs already cover it.

## Image processing

Images will have to be posted, compressed, thumbnailed.
Old web: Request placed temporary file on disk. Imagemagick put this into permanent directory on disk along processed copy.

# Överlämning från Gustav till Oscar

Vår roadmap så som den ser ut just nu är att vi håller på att göra milestones och issues i github för att göra vår backend fullt kompatibel med appen. Vi är inte klara med det än men planen är att vi ska bli klara till slutet av LP4. Under LP1 är målet att bli klara med att kunna köra en lokal instans av appen med en lokal instans av vår backen. Detta har fått sig ett försök i app-branchen konferens där vi har fixat med ip-addresser så att appen hittar ut från sin VM och kan göra requests till vår backend. I appen så använder man http://10.0.2.2:8000 vilket man kan hitta i filen abstractPython.service.dart i branchen konferens. 

Den nuvarande routen för att hantera bilder har just nu bara en path till lokalt på containern men det kommer vi vilja ändra på när vi har tillgång till mounted volumes. Den har inte heller 

Notiser har jag inte ens undersökt och inte heller mail server

Vi har väldigt inconsistent errorhandelning på backenden så som den är just nu

I LP2 hoppas vi att front-end ska ha hunnit göra tillräckligt mycket för att vi ska kunna göra klart det sista av backenden som inte finns i appen. Bland annat saker som bilbokningar och administration.

I LP3 och LP4 ska vi försöka få vår hemsida redo för release inför nollningen -25