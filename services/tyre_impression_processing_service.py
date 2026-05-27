import logging
from database.extensions import db
from database.unit_of_work import UnitOfWork
from database.models.tyre_impression import TyreImpression
from domain.exceptions import ModelNotFoundError, DatabaseError
from database.models.tyre_impression_processing import TyreImpressionProcessing
from database.models.data_types.tyre_impression_status import TyreImpressionStatus
from database.repositories.tyre_impression_repository import TyreImpressionRepository
from pipelines.tyre_impression_processing_pipeline import TyreImpressionProcessingPipeline
from database.repositories.tyre_impression_processing_repository import TyreImpressionProcessingRepository

logger = logging.getLogger(__name__)


class TyreImpressionProcessingService:
    def __init__(self):
        self.pipeline = TyreImpressionProcessingPipeline()
        self.tyre_impression_processing_repository = TyreImpressionProcessingRepository()
        self.tyre_impression_repository = TyreImpressionRepository()


    def get_by_tyre_impression_id(self, tyre_impression_id: int) -> TyreImpressionProcessing:
        tyre_impression_processing = self.tyre_impression_processing_repository.get_by_tyre_impression_id(tyre_impression_id)

        if not tyre_impression_processing:
            logger.error(f"Error getting tyre impression processing by tyre impression id {tyre_impression_id}")
            raise ModelNotFoundError(f"Error getting tyre impression processing by tyre impression id {tyre_impression_id}")

        return tyre_impression_processing


    def process_tyre_impression(self, tyre_impression_id: int):
        with UnitOfWork(db.session):
            # Load DB record
            try:
                tyre_impression = self._get_tyre_impression(tyre_impression_id)
            except ModelNotFoundError as e:
                logger.error(f"Error getting tyre impression in processing service with id {tyre_impression_id}: {e}")
                raise ModelNotFoundError(f"Error getting tyre impression in processing service with id {tyre_impression_id}: {e}")

            # Set status -> processing
            try:
                tyre_impression = self._set_tyre_impression_status(tyre_impression, TyreImpressionStatus.processing)
            except DatabaseError as e:
                logger.error(f"Error setting tyre impression status `{TyreImpressionStatus.processing}` in processing service: {e}")
                raise DatabaseError(f"Error setting tyre impression status `{TyreImpressionStatus.processing}` in processing service: {e}")

            # Run pipeline
            try:
                self.pipeline.process(tyre_impression.processing.id)
            except Exception as e:
                logger.error(f"Error processing tyre impression: {e}")
                raise e


    def _get_tyre_impression(self, tyre_impression_id: int) -> TyreImpression:
        tyre_impression = self.tyre_impression_repository.get_by_id(tyre_impression_id)

        if not tyre_impression:
            logger.error(f"Error getting tyre impression with id {tyre_impression_id}")
            raise ModelNotFoundError(f"Error getting tyre impression with id {tyre_impression_id}")

        return tyre_impression


    def _set_tyre_impression_status(self, tyre_impression: TyreImpression, status: TyreImpressionStatus) -> TyreImpression:
        try:
            updated_tyre_impression = self.tyre_impression_repository.update(tyre_impression, status=status)
        except DatabaseError as e:
            logger.error(f"Error setting tyre impression status: {e}")
            raise DatabaseError(f"Error setting tyre impression status: {e}")

        return updated_tyre_impression

