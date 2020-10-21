class User:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.token = data['token']
        self.sid = data['sid']


    def get(self):
        return dict(id=self.id, name=self.name)
