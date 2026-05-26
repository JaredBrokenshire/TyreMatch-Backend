import policies
from flask import current_app
from database.extensions import db
from database.models import TyreImpression
from database.unit_of_work import UnitOfWork
from services.file_service import FileService
from database.repositories import TyreImpressionRepository
from domain import InvalidFileTypeError, FileSaveError, DatabaseError
from services.tyre_impression_task_service import  TyreImpressionTaskService


class TyreImpressionService:
    def __init__(self):
        self.tyre_impression_repository = TyreImpressionRepository()
        self.file_service = FileService()

    def get_all(self, page=1, page_size=20) -> (list[TyreImpression], int):
        return self.tyre_impression_repository.get_all(page=page, page_size=page_size)

    def upload_impression_image(self, file) -> TyreImpression:
        if not file:
            raise InvalidFileTypeError("No file provided")

        if not file.filename:
            raise InvalidFileTypeError("No filename provided")

        uuid, filename = policies.uuid_filename(file)
        file.filename = filename

        with UnitOfWork(db.session):
            try:
                tyre_impression = self.tyre_impression_repository.create(uuid=uuid, file_path="temp_file_path")
            except DatabaseError as e:
                current_app.logger.exception(e)
                raise DatabaseError(f"Error creating tyre impression record: {e}")

            try:
                path = self.file_service.save_file(
                    file,
                    f"/tyre_match/files/tyre_impressions/{tyre_impression.id}/raw",
                    ["png", "jpg", "jpeg", "webp"]
                )
            except InvalidFileTypeError as e:
                current_app.logger.error(f"Invalid file type error: {e}")
                raise InvalidFileTypeError(f"Error saving file: {e}")
            except PermissionError as e:
                current_app.logger.error(f"Permission error: {e}")
                raise FileSaveError(f"Error saving file: {e}")
            except OSError as e:
                current_app.logger.error(f"OS error: {e}")
                raise FileSaveError(f"Error saving file: {e}")

            try:
                tyre_impression = self.tyre_impression_repository.update(
                    tyre_impression,
                    uuid=uuid,
                    file_path=path,
                )
            except DatabaseError as e:
                current_app.logger.exception(e)
                raise DatabaseError(f"Error updating tyre impression record: {e}")

        # Trigger async processing task
        TyreImpressionTaskService.process(tyre_impression.id)

        return tyre_impression
