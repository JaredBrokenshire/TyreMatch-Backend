from io import BytesIO


class MockFile:
    def __init__(self, filename, content=b"Some test data"):
        self.filename = filename
        self.stream = BytesIO(content)

    def save(self, path):
        # Simulate file.save()
        with open(path, 'wb') as f:
            f.write(self.stream.getvalue())