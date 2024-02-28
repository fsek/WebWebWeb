from fastapi import FastAPI
from schemas import Book, BookBrowse

app = FastAPI()

library: list[Book] = []


@app.post("/book", response_model=Book)
def addBook(book: Book):
    library.append(book)
    return book


@app.get("/catalogue", response_model=list[BookBrowse])
def getCatalogue():
    return library


@app.get("/book/{ISBN}", response_model=Book)
def getBook(ISBN: int):
    for book in library:
        if book.ISBN == ISBN:
            return book
