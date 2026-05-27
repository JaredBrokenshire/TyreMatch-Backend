from sqlalchemy.orm import joinedload
from database.models import TyreImpression
from database.repositories.base_repository import BaseRepository


class TyreImpressionRepository(BaseRepository[TyreImpression]):

    def __init__(self):
        super().__init__(TyreImpression)

    def get_by_id(self, id_: int):
        return (
            self.db.query(TyreImpression)
            .options(joinedload(TyreImpression.processing))
            .filter(TyreImpression.id == id_)
            .first()
        )


