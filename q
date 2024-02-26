* [33m7b81c4c[m[33m ([m[1;36mHEAD -> [m[1;32mtelephone_number[m[33m, [m[1;31morigin/telephone_number[m[33m)[m fixed telephone number for user and auth on telephone number so we have the right format
[31m|[m * [33m54eec16[m[33m ([m[1;32mmain[m[33m)[m fungerar inte något fett konstigt
[31m|[m[31m/[m  
[31m|[m *   [33m0f01160[m[33m ([m[1;31morigin/event_update[m[33m, [m[1;32mevent_update[m[33m)[m fixed merge conflict
[31m|[m [33m|[m[34m\[m  
[31m|[m [33m|[m * [33m79f9dbe[m Just formatting
[31m|[m * [34m|[m   [33mf2ca6b3[m fixed the request
[31m|[m [35m|[m[31m\[m [34m\[m  
[31m|[m [35m|[m[31m/[m [34m/[m  
[31m|[m[31m/[m[35m|[m [34m|[m   
[31m|[m * [34m|[m [33me452592[m fixed the problems in the issue
[31m|[m [34m|[m[34m/[m  
[31m|[m * [33mba93efc[m Funkar att updatera event nu
[31m|[m [36m|[m *   [33mf97487c[m[33m ([m[1;31morigin/post-create[m[33m, [m[1;32mpost-create[m[33m)[m fixed merge conflict
[31m|[m [36m|[m [1;31m|[m[1;32m\[m  
[31m|[m [36m|[m [1;31m|[m * [33mf436bca[m I only changed the * import to explicit
[31m|[m [36m|[m * [1;32m|[m [33m4a27b8c[m fixed 404 httpexception
[31m|[m [36m|[m [1;32m|[m[1;32m/[m  
[31m|[m [36m|[m *   [33m62c0762[m Merge branch 'main' into post-create
[31m|[m [36m|[m [1;33m|[m[1;34m\[m  
[31m|[m [36m|[m * [1;34m|[m [33mf89db77[m Create klar, funkar när man använder sig av ett councel_id som finns men inte annars, alltså måste den vara knuten till en council för att få finnas
[31m|[m [36m|[m * [1;34m|[m [33md7805b6[m Något konstigt med authorize när jag kallar på create_post from fastapi
[31m|[m [36m|[m[36m/[m [1;34m/[m  
[31m|[m [36m|[m [1;34m|[m * [33m1e62d7b[m[33m ([m[1;31morigin/automated-testing[m[33m)[m Create python-app.yml
[31m|[m [36m|[m[31m_[m[1;34m|[m[31m/[m  
[31m|[m[31m/[m[36m|[m [1;34m|[m   
* [36m|[m [1;34m|[m [33m401bd63[m[33m ([m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m)[m add ordering to GET all news. also created_at_column was giving value instead of function to insert_default
* [36m|[m [1;34m|[m [33m8e173cf[m making news.author_id non-optional
* [36m|[m [1;34m|[m [33mb268665[m Created news as described by #17 (#27)
* [36m|[m [1;34m|[m [33m7b860f9[m remove some commented code
* [36m|[m [1;34m|[m [33mac28913[m helpful comment on UserCreate
* [36m|[m [1;34m|[m [33mecf35b0[m Clarify how to reopen project in README
[1;35m|[m [36m|[m [1;34m|[m * [33m9077f44[m[33m ([m[1;31morigin/photographer_priority[m[33m)[m Något liknande detta kan vara en start för prioriteringssystemet!
[1;35m|[m [36m|[m[1;35m_[m[1;34m|[m[1;35m/[m  
[1;35m|[m[1;35m/[m[36m|[m [1;34m|[m   
* [36m|[m [1;34m|[m [33mc716764[m update readme
[1;34m|[m [36m|[m[1;34m/[m  
[1;34m|[m[1;34m/[m[36m|[m   
* [36m|[m [33m3bc3e1d[m Enabling windows subsystem for linux readme step
* [36m|[m [33mcf42e01[m POST-delete (#18)
[36m|[m[36m/[m  
[36m|[m * [33mfa7d417[m[33m ([m[1;31morigin/post_delete[m[33m)[m Fixad så att den inte krashar
[36m|[m * [33mb5f1c79[m Något konstigt är det när jag ska ta bort user-post kopplingarna
[36m|[m * [33m7e370b7[m Skapat en delete_post route som tar bort posten samt alla kopplingar till den
[36m|[m[36m/[m  
* [33m0749c77[m[33m ([m[1;31morigin/post-delete[m[33m)[m move back settings
* [33m52b6c76[m temp disable test
* [33m176843a[m debugging works outta the box!
* [33m0649a4a[m remove library tests, starting own tests
* [33m4cb7307[m update deps. not generating docs for prod
* [33meb5e53e[m starting with env vars
* [33m4a1574c[m Updating docs, changed a little in the first lessson to be closer to a real-life scenario.
* [33m12778db[m improved event_service, also fixed editor settings were wrong
* [33m6b3ef92[m Edit a comment and typo in docs
* [33m23b1e17[m Small stuff
* [33m3c25bfe[m Line length 120, event/signup/signup
* [33m2592b1e[m Halved size of image, changed to newer DBAPI psycopg, changed to python venv due to pip problems
* [33m3d384db[m moved database start to run on container start
* [33me4efa2f[m Update README.md
* [33m232f32a[m Update README
*   [33m25bf19b[m merging user-stuff
[32m|[m[33m\[m  
[32m|[m * [33m035102b[m automatic line changes, it did this auto when opening in container
[32m|[m * [33m53d61e6[m more on event signup, some rename
[32m|[m * [33m1daca0d[m event signup and more
[32m|[m * [33m2674dab[m event router, add and delete
[32m|[m * [33m9eb6564[m Now can create and assign permissions
[32m|[m * [33m9341bdb[m Changed session to sync in fastapi-users-db-sqlalchemy
[32m|[m * [33m9af370c[m checkpoint before trying going sync from async
[32m|[m * [33m93788db[m restored some lost files
[32m|[m * [33m665f2e7[m forking fastapi-users
[32m|[m * [33mbb37c7f[m switching branch
[32m|[m * [33md43d095[m checkpoint
[32m|[m * [33m243be64[m i forgor
[32m|[m * [33m69fee78[m dynamic import all, switching to the better association object pattern using association proxy extension of SQLAlchemy
[32m|[m * [33m0d423cc[m continuatio
[32m|[m * [33mb0693e0[m trying to get rid of type errors
* [33m|[m [33m06a8465[m moooooore line length!!
[33m|[m[33m/[m  
*   [33m2f38bf6[m Merge remote-tracking branch 'origin/main'
[34m|[m[35m\[m  
[34m|[m * [33m0bff1fa[m Created document with placeholder naming conventions
[34m|[m *   [33m0efa13c[m Merge pull request #4 from fsek/docs-clarifications
[34m|[m [36m|[m[1;31m\[m  
[34m|[m [36m|[m * [33m0bc1fbe[m[33m ([m[1;31morigin/docs-clarifications[m[33m)[m Small clarifications in docs
[34m|[m [36m|[m[36m/[m  
* [36m/[m [33macaf769[m black formatter line length to 100
[36m|[m[36m/[m  
* [33m6be7017[m Created some core database models
* [33m383e23a[m[33m ([m[1;31morigin/exam[m[33m)[m I forgor
* [33m5736a35[m fix typo
[1;31m|[m * [33m37bd113[m[33m ([m[1;31morigin/book[m[33m)[m update vscode setting
[1;31m|[m *   [33m9cdd8df[m Merge branch 'main' of https://github.com/fsek/WebWebWeb into book
[1;31m|[m [1;33m|[m[1;34m\[m  
[1;31m|[m * [1;34m|[m [33mf593ac5[m fix forgot extend
[1;31m|[m * [1;34m|[m   [33mc65312f[m Merge branch 'main' into book
[1;31m|[m [1;35m|[m[1;36m\[m [1;34m\[m  
[1;31m|[m * [1;36m|[m [1;34m|[m [33m1e2c668[m changed starting point
[1;31m|[m [1;36m|[m [1;36m|[m [1;34m|[m * [33mf7716c3[m[33m ([m[1;31morigin/tobbexam[m[33m)[m spagetti spagotti
[1;31m|[m [1;36m|[m[1;31m_[m[1;36m|[m[1;31m_[m[1;34m|[m[1;31m/[m  
[1;31m|[m[1;31m/[m[1;36m|[m [1;36m|[m [1;34m|[m   
* [1;36m|[m [1;36m|[m [1;34m|[m [33m762a804[m list of background tasks
* [1;36m|[m [1;36m|[m [1;34m|[m [33m45979e2[m rm link
* [1;36m|[m [1;36m|[m [1;34m|[m [33mef7a637[m exam done
* [1;36m|[m [1;36m|[m [1;34m|[m   [33m856692c[m Merge branch 'main' into exam
[32m|[m[33m\[m [1;36m\[m [1;36m\[m [1;34m\[m  
[32m|[m * [1;36m\[m [1;36m\[m [1;34m\[m   [33m9c3300c[m Merge branch 'main' of https://github.com/fsek/WebWebWeb
[32m|[m [34m|[m[35m\[m [1;36m\[m [1;36m\[m [1;34m\[m  
[32m|[m * [35m|[m [1;36m|[m [1;36m|[m [1;34m|[m [33m6f1a46d[m Changed unused imports to a warning instead of error
[32m|[m * [35m|[m [1;36m|[m [1;36m|[m [1;34m|[m [33mfb45fae[m Changed unused imports to a warning instead of error
[32m|[m * [35m|[m [1;36m|[m [1;36m|[m [1;34m|[m [33m62928ce[m Created tasks, hints and solutions for pydantic schemas
* [35m|[m [35m|[m [1;36m|[m [1;36m|[m [1;34m|[m [33m9f8c533[m adding some import
[35m|[m [35m|[m[35m/[m [1;36m/[m [1;36m/[m [1;34m/[m  
[35m|[m[35m/[m[35m|[m [1;36m|[m [1;36m|[m [1;34m|[m   
* [35m|[m [1;36m|[m [1;36m|[m [1;34m|[m [33m638246a[m many-many docs
* [35m|[m [1;36m|[m [1;36m|[m [1;34m|[m [33me6ebf9e[m working on final test markdown
[35m|[m[35m/[m [1;36m/[m [1;36m/[m [1;34m/[m  
[35m|[m [1;36m|[m [1;36m|[m [1;34m|[m * [33m9b29164[m[33m ([m[1;31morigin/many-many[m[33m)[m moved to schemas
[35m|[m [1;36m|[m [1;36m|[m [1;34m|[m * [33mce97ff0[m starter point for many to many
[35m|[m [1;36m|[m[35m_[m[1;36m|[m[35m_[m[1;34m|[m[35m/[m  
[35m|[m[35m/[m[1;36m|[m [1;36m|[m [1;34m|[m   
* [1;36m|[m [1;36m|[m [1;34m|[m [33m157c30b[m added selecting vscode interpreter to README
[1;34m|[m [1;36m|[m[1;34m_[m[1;36m|[m[1;34m/[m  
[1;34m|[m[1;34m/[m[1;36m|[m [1;36m|[m   
* [1;36m|[m [1;36m|[m [33m7683da6[m Fixed typo
* [1;36m|[m [1;36m|[m   [33m12d480e[m Merge branch 'main' of https://github.com/fsek/WebWebWeb
[1;31m|[m[1;32m\[m [1;36m\[m [1;36m\[m  
[1;31m|[m * [1;36m|[m [1;36m|[m [33m5defdc4[m added docs for Pydantic schemas
[1;31m|[m [1;36m|[m [1;36m|[m[1;36m/[m  
[1;31m|[m [1;36m|[m[1;36m/[m[1;36m|[m   
* [1;36m|[m [1;36m|[m [33mc9d7f35[m Merge branch 'main' of https://github.com/fsek/WebWebWeb
[1;33m|[m[1;36m\[m[1;36m|[m [1;36m|[m 
[1;33m|[m * [1;36m|[m [33mba328dc[m Docs on database and relations
[1;33m|[m * [1;36m|[m [33m86b6b04[m Database models docs
[1;33m|[m * [1;36m|[m   [33mc6cfcfe[m Merge branch 'main' of https://github.com/fsek/web3.0
[1;33m|[m [1;35m|[m[1;36m\[m [1;36m\[m  
[1;33m|[m * [1;36m|[m [1;36m|[m [33m113a75a[m Typo fix in README
* [1;36m|[m [1;36m|[m [1;36m|[m   [33m073025f[m Merge branch 'book' of https://github.com/fsek/WebWebWeb
[1;36m|[m[1;36m\[m [1;36m\[m [1;36m\[m [1;36m\[m  
[1;36m|[m [1;36m|[m[1;36m_[m[1;36m|[m[1;36m/[m [1;36m/[m  
[1;36m|[m[1;36m/[m[1;36m|[m [1;36m|[m [1;36m/[m   
[1;36m|[m [1;36m|[m [1;36m|[m[1;36m/[m    
[1;36m|[m [1;36m|[m[1;36m/[m[1;36m|[m     
[1;36m|[m * [1;36m|[m [33m754e068[m book example
[1;36m|[m [1;36m|[m[1;36m/[m  
* [1;36m|[m [33mcd1c7f6[m Merge branch 'main' of github.com:fsek/WebWebWeb
[33m|[m[1;36m\[m[1;36m|[m 
[33m|[m * [33m1394575[m Starting point for database learning
[33m|[m * [33m1c76c10[m added sqlalchemy dependency
[33m|[m * [33me3afbe2[m database.py starter, update deps, sqlite extension in README, gitignore .sqlite files
[33m|[m * [33m635b3dd[m Added tasks, hints and solutions to POST route.md
[33m|[m *   [33mc475805[m Merge pull request #1 from fsek/master
[33m|[m [35m|[m[36m\[m  
[33m|[m [35m|[m *   [33m79aaa29[m Merge branch 'main' of https://github.com/fsek/web3.0
[33m|[m [35m|[m [1;31m|[m[35m\[m  
[33m|[m [35m|[m [1;31m|[m[35m/[m  
[33m|[m [35m|[m[35m/[m[1;31m|[m   
[33m|[m [35m|[m * [33m97c3ae8[m Fixed new GET-Route and Setup.md
* [35m|[m [1;32m|[m [33m969e977[m rename file
[35m|[m[35m/[m [1;32m/[m  
* [1;32m/[m [33m5f87d91[m Documentation for POST routes
[1;32m|[m[1;32m/[m  
* [33m6dc20d0[m Update README.md
* [33m5a3ae5d[m Added Swagger url in README
* [33mca68b49[m Added a basic docs to making GET route
*   [33m7fa039d[m Merge branch 'main' of https://github.com/fsek/web3.0
[1;33m|[m[1;34m\[m  
[1;33m|[m * [33m674a011[m Update README.md
* [1;34m|[m [33m3dd55f8[m Gitignore pycache, autoImport setting
[1;34m|[m[1;34m/[m  
* [33m12f69e6[m git yeet
