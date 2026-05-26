from tasks import process_tyre_impression_task


class TyreImpressionTaskService:

    @staticmethod
    def process(tyre_impression_id: int):
        process_tyre_impression_task.delay(tyre_impression_id)