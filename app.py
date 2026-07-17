from fastapi import FastAPI, HTTPException

from scraper import (
    get_books,
    get_categories,
    get_category_page_count,
    get_books_by_category,
)

app = FastAPI(
    title="BooksToScrape API",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "BooksToScrape API",
        "endpoints": [
            "/categories",
            "/books?page=1",
            "/categories/{category}/pages",
        ],
    }


@app.get("/categories")
def categories():
    return {
        "count": len(get_categories()),
        "categories": get_categories(),
    }


@app.get("/books")
def books(page: int = 1):

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page number must be greater than zero.",
        )

    try:
        books = get_books(page)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Page not found.",
        )

    return {
        "page": page,
        "count": len(books),
        "books": books,
    }


@app.get("/categories/{category}/pages")
def category_pages(category: str):

    pages = get_category_page_count(category)

    if pages is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found.",
        )

    return {
        "category": category,
        "total_pages": pages,
    }

@app.get("/categories/{category}/books")
def books_by_category(
    category: str,
    page: int = 1,
):

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than zero.",
        )

    total_pages = get_category_page_count(category)

    if total_pages is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found.",
        )

    if page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"Page exceeds available pages ({total_pages}).",
        )

    books = get_books_by_category(category, page)

    return {
        "category": category,
        "page": page,
        "total_pages": total_pages,
        "count": len(books),
        "books": books,
    }