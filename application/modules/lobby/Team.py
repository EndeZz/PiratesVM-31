class Team:
    def __init__(self, data):
        self.teamId = data['teamId']
        self.name = data['name']
        self.players = data['players']
        self.password = data['password'] if 'password' in data else ''
        self.isPrivate = data['isPrivate'] if 'isPrivate' in data else False
        self.roomId = data['roomId']

    def get(self):
        return dict(teamId=self.teamId,
                    name=self.name,
                    players=self.players,
                    isPrivate= self.isPrivate
                    )

    def getSelf(self):
        return dict(teamId=self.teamId,
                    name=self.name,
                    players=self.players,
                    password=self.password,
                    isPrivate= self.isPrivate,
                    roomId=self.roomId
                    )
