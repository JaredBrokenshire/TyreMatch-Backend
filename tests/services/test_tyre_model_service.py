import pytest
from unittest.mock import patch
from domain import DatabaseError
from services import TyreModelService
from database.repositories import TyreModelRepository


def test_create():
    service = TyreModelService()

    # Can not create is there is an error from the repo
    with patch.object(TyreModelRepository, "create", side_effect=Exception("test repo error")):
        with pytest.raises(DatabaseError, match="Error creating tyre_model record: test repo error"):
            service.create({
                "manufacturer": "Michelin",
                "model_name": "Pilot Sport"
            })

    # Can create tyre model
    response = service.create({
        "manufacturer": "Michelin",
        "model_name": "Pilot Sport"
    })
    assert response.manufacturer == "Michelin"
    assert response.model_name == "Pilot Sport"
