from database.models.tyre_model import TyreModel
from database.repositories.base_repository import BaseRepository


class TyreModelRepository(BaseRepository[TyreModel]):

    def __init__(self):
        super().__init__(TyreModel)


