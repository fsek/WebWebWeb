# Naming conventions
## Functions
The python functions in a route definition should be named descriptively. The name of the function is used as a description in Swagger, which makes it easy to understand what a route is supposed to do in Swagger if named clearly. For example, a function named `create_example` will get the description 'Create Example' in Swagger. 

The function names should be written in snake_case.

## Schemas
For many different objects, a lot of basic schemas will be used for similar purposes. One common naming convention is to follow CRUD: Create, Read, Update and Delete, which describes how the most common schemas should be named. Let's say we want to create some schemas for an database model 'Example'. For the different routes, the schemas should ideally be named: 

- For the POST route: `ExampleCreate`,
- For the GET route: `ExampleRead`,
- For the PATCH route: `ExampleUpdate`,
- For the DELETE route: `ExampleDelete`.

All schemas should be written in PascalCase. 

## Database models
Database models should be written with PascalCase, with suffix _DB. For example, `CoolExample_DB`. The `__tablename__` property should be snake_case and end with _table, for example `cool_example_table`. 

## Association Tables
Association tables should be written with snake_case. An association table that relates cats and dogs should ideally be named `cat_dog_association`. The tablename should be the same, but with 'table' instead of 'association': `cat_dog_table`. 