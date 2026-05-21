import http
import uuid
from database.repositories import TyreImpressionRepository


def test_get_all(client, database_session):
    repo = TyreImpressionRepository()

    tyre_impression_1 = repo.create(uuid=uuid.uuid4(), file_path="/files/images/tyre_impressions")
    tyre_impression_2 = repo.create(uuid=uuid.uuid4(), file_path="/some/different/filepath")

    response = client.get("/tyre-impressions")

    # Can get status 200
    assert response.status_code == http.HTTPStatus.OK

    data = response.get_json()

    # Can return data and metadata
    assert "data" in data
    assert "total_count" in data
    assert data["total_count"] == 2

    tyre_impressions = data["data"]
    # Can return all items
    assert len(tyre_impressions) == 2

    first = tyre_impressions[0]
    second = tyre_impressions[1]

    # Can return all data
    assert first["id"] == tyre_impression_1.id
    assert str(first["uuid"]) == str(tyre_impression_1.uuid)
    assert first["file_path"] == tyre_impression_1.file_path
    assert first["status"] == tyre_impression_1.status.value
    assert first["created_at"] == tyre_impression_1.created_at.isoformat()

    assert second["id"] == tyre_impression_2.id
    assert str(second["uuid"]) == str(tyre_impression_2.uuid)
    assert second["file_path"] == tyre_impression_2.file_path
    assert second["status"] == tyre_impression_2.status.value
    assert second["created_at"] == tyre_impression_2.created_at.isoformat()

def test_get_all_empty(client):
    response = client.get("/tyre-impressions")

    # Can return status 200
    assert response.status_code == http.HTTPStatus.OK

    data = response.get_json()

    # Can return empty dataset
    assert data["total_count"] == 0
    assert data["data"] == []

def test_get_all_pagination(client, database_session):
    repo = TyreImpressionRepository()

    repo.create(uuid=uuid.uuid4(), file_path="/files/images/tyre_impressions")
    tyre_impression_2 = repo.create(uuid=uuid.uuid4(), file_path="/some/different/filepath")
    repo.create(uuid=uuid.uuid4(), file_path="/another/unique/filepath")

    response = client.get("/tyre-impressions?page_size=1&page=2")

    data = response.get_json()

    # Can return correct number of items
    assert data["total_count"] == 3
    assert len(data["data"]) == 1

    # Can correctly offset response
    assert str(data["data"][0]["uuid"]) == str(tyre_impression_2.uuid)

def test_upload(client, database_session, monkeypatch):
    pass
