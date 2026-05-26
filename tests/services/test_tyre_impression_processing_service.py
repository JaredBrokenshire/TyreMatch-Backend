from random import random, randint
from unittest.mock import patch

import pytest

from database.models.data_types import TyreImpressionStatus
from database.repositories import TyreImpressionRepository, TyreImpressionProcessingRepository
from domain import ModelNotFoundError, DatabaseError
from preprocessing import TyreImpressionProcessingPipeline
from tests.helpers.factories import TyreImpressionFactory, TyreImpressionProcessingFactory
from services.tyre_impression_processing_service import TyreImpressionProcessingService


def test_get_by_tyre_impression_id_invalid_id():
    service = TyreImpressionProcessingService()

    with pytest.raises(ModelNotFoundError, match="Error getting tyre impression processing by tyre impression id 999"):
        service.get_by_tyre_impression_id(999)


def test_get_by_tyre_impression_id():
    service = TyreImpressionProcessingService()

    tyre_impression_1 = TyreImpressionFactory().create()
    tyre_impression_2 = TyreImpressionFactory().create()
    tyre_impression_processing_1 = TyreImpressionProcessingFactory().create(tyre_impression_1.id)
    tyre_impression_processing_2 = TyreImpressionProcessingFactory().create(tyre_impression_2.id)

    result = service.get_by_tyre_impression_id(tyre_impression_1.id)

    assert result.id == tyre_impression_processing_1.id
    assert result.tyre_impression_id == tyre_impression_processing_1.tyre_impression_id
    assert result.id != tyre_impression_processing_2.id
    assert result.tyre_impression_id != tyre_impression_processing_2.tyre_impression_id


def test_process_tyre_impression_invalid_id():
    service = TyreImpressionProcessingService()


    with patch.object(TyreImpressionProcessingService, "_get_tyre_impression", side_effect=ModelNotFoundError("test error")):
        with pytest.raises(
                ModelNotFoundError,
                match="Error getting tyre impression in processing service with id 999: test error"):
            service.process_tyre_impression(999)


def test_process_tyre_impression_database_error_from_set_tyre_impression_status_processing():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create()

    with patch.object(
        TyreImpressionProcessingService,
        "_set_tyre_impression_status",
        side_effect=DatabaseError("test error")
    ):
        with pytest.raises(
            DatabaseError,
            match=f"Error setting tyre impression status `{TyreImpressionStatus.processing}` in processing service: test error"
        ):
            service.process_tyre_impression(tyre_impression.id)


# TODO: Update when exceptions have been defined in pipeline
def test_process_tyre_impression_error_from_pipeline():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create()

    with patch.object(
        TyreImpressionProcessingPipeline,
        "process",
        side_effect=Exception("test error")
    ):
        with pytest.raises(Exception, match="test error"):
            service.process_tyre_impression(tyre_impression.id)


def test_process_tyre_impression_database_error_from_upsert_processing_record():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create()

    mock_results = {
        "grayscale_path": "/files/tyre_impressions/grayscale/test.jpg",
        "binary_path": "/files/tyre_impressions/binary/test.jpg",
        "skeleton_path": "/files/tyre_impressions/skeleton/test.jpg",
        "features": {
            "edge_density": random(),
            "void_ratio": random(),
            "groove_count": randint(1,10),
        },
        "preprocessing_version": 2,
    }

    with patch.object(
        TyreImpressionProcessingService,
        "_upsert_processing_record",
        side_effect=DatabaseError("test error")
    ):
        with patch.object(
            TyreImpressionProcessingPipeline,
            "process",
            result=mock_results
        ):
            with pytest.raises(
                DatabaseError,
                match="Error upserting tyre impression processing record in processing service: test error"
            ):
                service.process_tyre_impression(tyre_impression.id)


def test_process_tyre_impression_database_error_from_set_tyre_impression_status_processed():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create(
        status=TyreImpressionStatus.processing,
    )

    mock_results = {
        "grayscale_path": "/files/tyre_impressions/grayscale/test.jpg",
        "binary_path": "/files/tyre_impressions/binary/test.jpg",
        "skeleton_path": "/files/tyre_impressions/skeleton/test.jpg",
        "features": {
            "edge_density": random(),
            "void_ratio": random(),
            "groove_count": randint(1,10),
        },
        "preprocessing_version": 2,
    }

    with patch.object(
            TyreImpressionProcessingService,
            "_set_tyre_impression_status",
            side_effect=[
                tyre_impression,
                DatabaseError("test error")
            ]  # List needed here to prevent _set_tyre_impression_status from raising an error the first time its invoked
    ):
        with patch.object(
            TyreImpressionProcessingPipeline,
            "process",
            return_value=mock_results
        ):
            with pytest.raises(
                    DatabaseError,
                    match=f"Error setting tyre impression status `{TyreImpressionStatus.processed}` in processing service: test error"
            ):
                service.process_tyre_impression(tyre_impression.id)


def test_process_tyre_impression():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create()

    mock_results = {
        "grayscale_path": "/files/tyre_impressions/grayscale/test.jpg",
        "binary_path": "/files/tyre_impressions/binary/test.jpg",
        "skeleton_path": "/files/tyre_impressions/skeleton/test.jpg",
        "features": {
            "edge_density": random(),
            "void_ratio": random(),
            "groove_count": randint(1,10),
        },
        "preprocessing_version": 2,
    }

    with patch.object(TyreImpressionProcessingPipeline, "process", return_value=mock_results):
        result = service.process_tyre_impression(tyre_impression.id)

        assert result.id is not None
        assert result.tyre_impression_id == tyre_impression.id
        assert result.grayscale_path == mock_results.get("grayscale_path")
        assert result.binary_path == mock_results.get("binary_path")
        assert result.skeleton_path == mock_results.get("skeleton_path")
        assert result.edge_density == mock_results.get("features").get("edge_density")
        assert result.void_ratio == mock_results.get("features").get("void_ratio")
        assert result.groove_count == mock_results.get("features").get("groove_count")
        assert result.preprocessing_version == mock_results.get("preprocessing_version")


def test_get_tyre_impression_invalid_id():
    service = TyreImpressionProcessingService()

    with pytest.raises(ModelNotFoundError, match="Error getting tyre impression with id 999"):
        service._get_tyre_impression(999)


def test_get_tyre_impression():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create()

    result = service._get_tyre_impression(tyre_impression.id)
    assert result is not None
    assert result.id == tyre_impression.id


def test_set_tyre_impression_status_database_error_from_repo():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create()

    with patch.object(TyreImpressionRepository, "update", side_effect=DatabaseError("test error")):
        with pytest.raises(DatabaseError, match="Error setting tyre impression status: test error"):
            service._set_tyre_impression_status(tyre_impression, TyreImpressionStatus.processing)


def test_set_tyre_impression_status():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create()

    result = service._set_tyre_impression_status(tyre_impression, TyreImpressionStatus.processing)
    assert result is not None
    assert result.id == tyre_impression.id
    assert result.status == TyreImpressionStatus.processing


def test_upsert_processing_record_database_error_from_repo():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create()

    with patch.object(TyreImpressionProcessingRepository, "update", side_effect=DatabaseError("test error")):
        with pytest.raises(DatabaseError, match="Error upserting tyre impression processing: test error"):
            service._upsert_processing_record(tyre_impression, {})


def test_upsert_processing_record_not_exist():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create()

    result = service._upsert_processing_record(tyre_impression, {
        "grayscale_path": "/files/tyre_impressions/grayscale/test.jpg",
        "binary_path": "/files/tyre_impressions/binary/test.jpg",
        "skeleton_path": "/files/tyre_impressions/skeleton/test.jpg",
        "features": {
            "edge_density": random(),
            "void_ratio": random(),
            "groove_count": randint(1,10),
        }
    })

    # Ensure only one tyre impression processing record was created
    tyre_impression_processing_records, total_count = TyreImpressionProcessingRepository().get_all()
    assert 1 == len(tyre_impression_processing_records)
    assert 1 == total_count
    assert result == tyre_impression_processing_records[0]
    assert result.tyre_impression_id == tyre_impression.id


def test_upsert_processing_record_existing_record():
    service = TyreImpressionProcessingService()

    tyre_impression = TyreImpressionFactory().create()
    tyre_impression_processing = TyreImpressionProcessingFactory().create(tyre_impression.id)

    result = service._upsert_processing_record(tyre_impression, {
        "grayscale_path": "/files/tyre_impressions/grayscale/test.jpg",
        "binary_path": "/files/tyre_impressions/binary/test.jpg",
        "skeleton_path": "/files/tyre_impressions/skeleton/test.jpg",
        "features": {
            "edge_density": random(),
            "void_ratio": random(),
            "groove_count": randint(1,10),
        }
    })

    # Ensure no new tyre impression processing records were created
    tyre_impression_processing_records, total_count = TyreImpressionProcessingRepository().get_all()
    assert 1 == len(tyre_impression_processing_records)
    assert 1 == total_count
    assert result == tyre_impression_processing_records[0]
    assert tyre_impression_processing.id == result.id == tyre_impression_processing_records[0].id
    assert result.tyre_impression_id == tyre_impression.id


