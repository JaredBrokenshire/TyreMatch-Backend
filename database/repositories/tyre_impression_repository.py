from database.models import TyreImpression
from database.repositories.base_repository import BaseRepository


class TyreImpressionRepository(BaseRepository[TyreImpression]):

    def __init__(self):
        super().__init__(TyreImpression)


