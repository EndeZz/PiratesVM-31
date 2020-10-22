class Player:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.readyToStart = data['readyToStart'] if data['readyToStart'] else False


    def get(self):
        return dict(id=self.id, name=self.name, readyToStart=self.readyToStart)
