from database.models import TyreImpressionProcessing
from database.repositories.base_repository import BaseRepository


class TyreImpressionProcessingRepository(BaseRepository[TyreImpressionProcessing]):

    def __init__(self):
        super().__init__(TyreImpressionProcessing)


    def get_by_tyre_impression_id(self, tyre_impression_id: int) -> TyreImpressionProcessing:
        return self.db.query(self.model).filter(self.model.tyre_impression_id == tyre_impression_id).first()


