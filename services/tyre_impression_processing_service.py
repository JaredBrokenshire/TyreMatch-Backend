from flask import current_app
from database.extensions import db
from database.unit_of_work import UnitOfWork
from domain import ModelNotFoundError, DatabaseError
from preprocessing import TyreImpressionProcessingPipeline
from database.models.data_types import TyreImpressionStatus
from database.models import TyreImpressionProcessing, TyreImpression
from database.repositories import TyreImpressionRepository, TyreImpressionProcessingRepository


class TyreImpressionProcessingService():
    def __init__(self):
        self.pipeline = TyreImpressionProcessingPipeline()
        self.tyre_impression_processing_repository = TyreImpressionProcessingRepository()
        self.tyre_impression_repository = TyreImpressionRepository()


    def get_by_tyre_impression_id(self, tyre_impression_id: int) -> TyreImpressionProcessing:
        tyre_impression_processing = self.tyre_impression_processing_repository.get_by_tyre_impression_id(tyre_impression_id)

        if not tyre_impression_processing:
            current_app.logger.error(f"Error getting tyre impression processing by tyre impression id {tyre_impression_id}: {e}")
            raise ModelNotFoundError(f"Error getting tyre impression processing by tyre impression id {tyre_impression_id}: {e}")

        return tyre_impression_processing


    def process_tyre_impression(self, tyre_impression_id: int) -> TyreImpressionProcessing:
        with UnitOfWork(db.session):
            # Load DB record
            try:
                tyre_impression = self._get_tyre_impression(tyre_impression_id)
            except ModelNotFoundError as e:
                current_app.logger.error(f"Error getting tyre impression in processing service with id {tyre_impression_id}: {e}")
                raise ModelNotFoundError(f"Error getting tyre impression in processing service with id {tyre_impression_id}: {e}")

            # Set status -> preprocessing
            try:
                tyre_impression = self._set_tyre_impression_status(tyre_impression, TyreImpressionStatus.preprocessing)
            except DatabaseError as e:
                current_app.logger.error(f"Error setting tyre impression status `{TyreImpressionStatus.preprocessing}` in processing service: {e}")
                raise DatabaseError(f"Error setting tyre impression status `{TyreImpressionStatus.preprocessing}` in processing service: {e}")

            # Run pipeline
            try:
                results = self.pipeline.process(tyre_impression.file_path)
            except Exception as e:
                current_app.logger.error(f"Error processing tyre impression: {e}")
                raise e

            # Save outputs
            tyre_impression_processing = self._upsert_processing_record(tyre_impression, results)

            # Set status processed
            try:
                self._set_tyre_impression_status(tyre_impression, TyreImpressionStatus.preprocessed)
            except DatabaseError as e:
                current_app.logger.error(f"Error setting tyre impression status `{TyreImpressionStatus.preprocessed}` in processing service: {e}")
                raise DatabaseError(f"Error setting tyre impression status `{TyreImpressionStatus.preprocessed}` in processing service: {e}")

            return tyre_impression_processing


    def _get_tyre_impression(self, tyre_impression_id: int) -> TyreImpression:
        tyre_impression = self.tyre_impression_repository.get_by_id(tyre_impression_id)

        if not tyre_impression:
            current_app.logger.error(f"Error getting tyre impression with id {tyre_impression_id}: {e}")
            raise ModelNotFoundError(f"Error getting tyre impression with id {tyre_impression_id}: {e}")

        return tyre_impression


    def _set_tyre_impression_status(self, tyre_impression: TyreImpression, status: TyreImpressionStatus) -> TyreImpression:
        try:
            updated_tyre_impression = self.tyre_impression_repository.update(tyre_impression, status=status)
        except DatabaseError as e:
            current_app.logger.error(f"Error setting tyre impression status: {e}")
            raise DatabaseError(f"Error setting tyre impression status: {e}")

        return updated_tyre_impression


    def _upsert_processing_record(self, tyre_impression: TyreImpression, results: dict) -> TyreImpressionProcessing:
        processing = self.get_by_tyre_impression_id(tyre_impression.id)
        if not processing:
            processing = TyreImpressionProcessing(
                tyre_impression_id=tyre_impression.id,
            )
            self.tyre_impression_processing_repository.create(
                tyre_impression=processing.tyre_impression_id,
            )

        processing.grayscale_path = results.get("grayscale_path")
        processing.binary_path = results.get("binary_path")
        processing.skeleton_path = results.get("skeleton_path")

        features = results.get("features", {})

        processing.edge_density = features.get("edge_density")
        processing.void_ratio = features.get("void_ratio")
        processing.groove_count = features.get("groove_count")

        processing.preprocessing_version = results.get(
            "preprocessing_version",
            1
        )

        return processing


