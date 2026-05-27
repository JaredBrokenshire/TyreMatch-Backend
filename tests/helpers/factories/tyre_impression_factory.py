from datetime import datetime
from database.models.data_types.tyre_impression_status import TyreImpressionStatus
from database.repositories.tyre_impression_repository import TyreImpressionRepository


class TyreImpressionFactory:
    counter = 0

    @classmethod
    def create(cls, **kwargs):
        repo = TyreImpressionRepository()

        cls.counter += 1

        defaults = {
            "uuid": f"{cls.counter}-uuid",
            "status": TyreImpressionStatus.uploaded,
            "created_at": datetime.now(),
        }

        defaults.update(kwargs)

        return repo.create(**defaults)