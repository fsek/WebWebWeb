from fastapi import FastAPI
from schemas import book, bookBrowse

app = FastAPI()

libary_list: list[book] = []

@app.post("/add_book", response_model=book)
def add_book(bok: book):
    libary_list.append(bok)
    return bok

@app.get("/get_books", response_model=list[bookBrowse])
def get_books():
    return libary_list

@app.get("/book/{ISBN}", response_model=book)
def get_book(ISBN: int):
    for bok in libary_list:
        if bok.ISBN == ISBN:
            return bok
    return {"error": "Book not found"}