from database.models import TyreModel


class MockTyreModelService:
    def __init__(self):
        self.create_calls = []
        self.create_error = None
        self.create_response = None

    def create(self, tyre_model: TyreModel):
        self.create_calls.append(tyre_model)

        if self.create_error:
            raise self.create_error

        return self.create_response

    def reset(self):
        self.create_calls = []
        self.create_error = None
        self.create_response = None
