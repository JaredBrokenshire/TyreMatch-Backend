from tests.helpers.factories.tyre_impression_factory import TyreImpressionFactory
from database.repositories.tyre_impression_repository import TyreImpressionRepository
from tests.helpers.factories.tyre_impression_processing_factory import TyreImpressionProcessingFactory


def test_get_by_id_invalid_id():
    repo = TyreImpressionRepository()

    result = repo.get_by_id(1000)

    assert result is None


def test_get_by_id_valid_id():
    repo = TyreImpressionRepository()

    tyre_impression = TyreImpressionFactory().create()

    result = repo.get_by_id(tyre_impression.id)
    assert tyre_impression == result


def test_get_by_id_join_tyre_impression_processing():
    repo = TyreImpressionRepository()

    tyre_impression = TyreImpressionFactory().create()
    tyre_impression_processing = TyreImpressionProcessingFactory.create(tyre_impression.id)

    result = repo.get_by_id(tyre_impression.id)
    assert tyre_impression == result
    assert tyre_impression_processing == result.processing