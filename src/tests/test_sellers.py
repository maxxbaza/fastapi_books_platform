import pytest
from fastapi import status

from src.models.books import Book
from src.models.sellers import Seller

API_V1_URL_PREFIX = "/api/v1/seller"


@pytest.mark.asyncio()
async def test_create_seller(async_client):
    data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "ivanov@test.ru",
        "password": "qwerty123",
    }

    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()

    assert result["id"] is not None
    assert result == {
        "id": result["id"],
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "ivanov@test.ru",
    }

@pytest.mark.asyncio()
async def test_get_all_sellers(db_session, async_client):
    seller_1 = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov@test.ru",
        password="123456",
    )
    seller_2 = Seller(
        first_name="Petr",
        last_name="Petrov",
        e_mail="petrov@test.ru",
        password="abcdef",
    )

    db_session.add_all([seller_1, seller_2])
    await db_session.commit()
    await db_session.refresh(seller_1)
    await db_session.refresh(seller_2)

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "sellers": [
            {
                "id": seller_1.id,
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "email": "ivanov@test.ru",
            },
            {
                "id": seller_2.id,
                "first_name": "Petr",
                "last_name": "Petrov",
                "email": "petrov@test.ru",
            },
        ]
    }


@pytest.mark.asyncio()
async def test_get_single_seller_with_books(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    book_1 = Book(
        title="Clean Code",
        author="Robert Martin",
        year=2024,
        pages=300,
        seller_id=seller.id,
    )
    book_2 = Book(
        title="DDD",
        author="Eric Evans",
        year=2024,
        pages=500,
        seller_id=seller.id,
    )

    db_session.add_all([book_1, book_2])
    await db_session.commit()
    await db_session.refresh(book_1)
    await db_session.refresh(book_2)

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": seller.id,
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "ivanov@test.ru",
        "books": [
            {
                "id": book_1.id,
                "title": "Clean Code",
                "author": "Robert Martin",
                "year": 2024,
                "pages": 300,
                "seller_id": seller.id,
            },
            {
                "id": book_2.id,
                "title": "DDD",
                "author": "Eric Evans",
                "year": 2024,
                "pages": 500,
                "seller_id": seller.id,
            },
        ],
    }

@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    data = {
        "first_name": "Petr",
        "last_name": "Petrov",
        "e_mail": "petrov@test.ru",
    }

    response = await async_client.put(f"{API_V1_URL_PREFIX}/{seller.id}", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": seller.id,
        "first_name": "Petr",
        "last_name": "Petrov",
        "email": "petrov@test.ru",
    }


@pytest.mark.asyncio()
async def test_delete_seller_cascade_books(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivanov@test.ru",
        password="123456",
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)

    book = Book(
        title="Clean Code",
        author="Robert Martin",
        year=2024,
        pages=300,
        seller_id=seller.id,
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    seller_id = seller.id
    book_id = book.id

    db_session.expire_all()
    deleted_seller = await db_session.get(Seller, seller_id)
    deleted_book = await db_session.get(Book, book_id)

    assert deleted_seller is None
    assert deleted_book is None