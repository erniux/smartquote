class ApiClient:
    def __init__(self, request):
        self.request = request

    def get(self, path, **kwargs):
        return self.request.get(path, **kwargs)

    def post(self, path, data=None, json=None, **kwargs):
        return self.request.post(path, data=data, json=json, **kwargs)
