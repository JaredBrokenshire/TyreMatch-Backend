from tests.helpers.factories.tyre_impression_factory import TyreImpressionFactory
from tests.helpers.factories.tyre_impression_processing_factory import TyreImpressionProcessingFactory


def test_repr(database_session):
    tyre_impression = TyreImpressionFactory().create()
    tyre_impression_processing = TyreImpressionProcessingFactory().create(tyre_impression.id)

    res = tyre_impression_processing.__repr__()
    assert res == f"<TyreImpressionProcessing {tyre_impression_processing.id} v{tyre_impression_processing.pipeline_version}>"