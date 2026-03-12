import pytest
from fastapi import status

from src.models.books import Book
from src.models.sellers import Seller

API_V1_URL_PREFIX = "/api/v1/books"


@pytest.mark.asyncio()
async def test_create_book(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov_books@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 2025,
        "seller_id": seller.id,
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_book_id = result_data.pop("id", None)
    assert resp_book_id is not None, "Book id not returned from endpoint"

    assert result_data == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
        "seller_id": seller.id,
    }


@pytest.mark.asyncio()
async def test_create_book_with_old_year(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov_old_year@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 1986,
        "seller_id": seller.id,
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio()
async def test_get_books(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov_get_books@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2021, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mziri", year=2021, pages=108, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.commit()
    await db_session.refresh(book)
    await db_session.refresh(book_2)

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["books"]) == 2

    assert response.json() == {
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2021,
                "id": book.id,
                "pages": 104,
                "seller_id": seller.id,
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 2021,
                "id": book_2.id,
                "pages": 108,
                "seller_id": seller.id,
            },
        ]
    }


@pytest.mark.asyncio()
async def test_get_single_book(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov_single_book@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mziri", year=1997, pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.commit()
    await db_session.refresh(book)
    await db_session.refresh(book_2)

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "pages": 104,
        "id": book.id,
        "seller_id": seller.id,
    }


@pytest.mark.asyncio()
async def test_get_single_book_with_wrong_id(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov_wrong_id@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    response = await async_client.get(f"{API_V1_URL_PREFIX}/426548")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_update_book(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov_update_book@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    data = {
        "title": "Mziri",
        "author": "Lermontov",
        "pages": 250,
        "year": 2024,
        "id": book.id,
        "seller_id": seller.id,
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{book.id}",
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK

    book_id = book.id
    seller_id = seller.id

    db_session.expire_all()
    res = await db_session.get(Book, book_id)

    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.pages == 250
    assert res.year == 2024
    assert res.id == book_id
    assert res.seller_id == seller_id


@pytest.mark.asyncio()
async def test_delete_book(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov_delete_book@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)

    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    book_id = book.id
    db_session.expire_all()
    res = await db_session.get(Book, book_id)
    assert res is None


@pytest.mark.asyncio()
async def test_delete_book_with_invalid_book_id(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov_delete_invalid@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)

    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{book.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND