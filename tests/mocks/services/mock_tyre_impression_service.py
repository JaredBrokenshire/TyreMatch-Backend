class MockTyreImpressionService:
    def __init__(self):
        self.upload_impression_image_calls = []
        self.upload_impression_image_response = None
        self.upload_impression_image_error = None

    def upload_impression_image(self, file):
        self.upload_impression_image_calls.append(file)

        if self.upload_impression_image_error:
            raise self.upload_impression_image_error

        return self.upload_impression_image_response

    def reset(self):
        self.upload_impression_image_calls = []
        self.upload_impression_image_response = None
        self.upload_impression_image_error = None