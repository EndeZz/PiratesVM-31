from application.modules.BaseManager import BaseManager
# генерация пароля для лобби и roomId
from application.modules.common.Common import Common
from .Player import Player
from .Team import Team


class LobbyManager(BaseManager):
    def __init__(self, mediator, sio, MESSAGES):
        super().__init__(mediator=mediator, sio=sio, MESSAGES=MESSAGES)
        self.__team = Team
        self.__player = Player
        self.__teams = {}

        self.__teams[1] = self.__team(dict(
            teamId=1,
            name='QQWWE',
            password='12312',
            isPrivate=True,
            players=[
                self.__player(dict(id=1, name='1231')),
                self.__player(dict(id=2, name='1231', readyToStart=True))],
            roomId="333"
        ))

        self.__teams[2] = self.__team(dict(
            teamId=2,
            name='44343',
            password='123324312',
            isPrivate=True,
            players=[
                self.__player(dict(id=2, name='1231')),
                self.__player(dict(id=3, name='1231', readyToStart=True))],
            roomId="333"
        ))


        #TRIGGERS
        #получение user по token
        #EVENTS
        # Если чел дисконектнулся, тогда вызывать leaveTeam и вызывать событие logout
        self.mediator.subscribe(self.EVENTS['USER_LOGOUT'], self.leaveTeam)

        self.sio.on(self.MESSAGES['CREATE_TEAM'], self.createTeam)
        self.sio.on(self.MESSAGES['TEAM_LIST'])
        self.sio.on(self.MESSAGES['KICK_FROM_TEAM'], self.kickFromTeam)
        self.sio.on(self.MESSAGES['LEAVE_TEAM'], self.leaveTeam)
        self.sio.on(self.MESSAGES['READY_TO_START'], self.readyToStart)
        self.sio.on(self.MESSAGES['JOIN_TO_TEAM'], self.joinToTeam)
        self.sio.on(self.MESSAGES['INVITE_TO_TEAM'], self.inviteToTeam)

    def __deleteEmptyTeams(self):
        for key in self.__teams:
            team = self.__teams[key].getSelf()
            users = team['players']
            if len(users) == 0:
                del self.__teams[team['teamId']]
                return

    def __deleteUserFromTeam(self, userId, team):
        users = team['players']
        for user in users:
            if user.get()['id'] == userId:
                users.remove(user)
                return
        return None

    def __deleteUserFromAllTeams(self, userId, sid):
        for key in self.__teams:
            team = self.__teams[key].getSelf()
            for user in team['players']:
                if user.get()['id'] == userId:
                    self.sio.leave_room(sid, team['roomId'])
                    if userId == team['teamId']:
                        del self.__teams[userId]
                    self.__deleteUserFromTeam(userId=userId, team=team)
                    continue
        self.__deleteEmptyTeams()

    def __getTeamByUserId(self, userId):
        for key in self.__teams:
            team = self.__teams[key]
            users = team.getSelf()['players']
            for user in users:
                if userId == user.get()['id']:
                    return team
        return False

    def __findPlayerInTeam(self, userId, team):
        players = team.getSelf()['players']
        for player in players:
            if player.get()['id'] == userId:
                return player.get()
        return False

    def __checkTeamIsReady(self, team):
        players = team['players']
        for player in players:
            if not player.get()['readyToStart']:
                return False
        return True

    def __isOwner(self, userId):
        for key in self.__teams:
            team = self.__teams[key].getSelf()
            if userId == team['teamId']:
                return True
        return False

    def __findTeamByPassword(self, password):
        for key in self.__teams:
            team = self.__teams[key]
            if password == team.getSelf()['password']:
                return team
        return None

    def __updateTeamList(self, team):

        return

    async def createTeam(self, sid, data):
        owner = self.mediator.get(self.TRIGGERS['GET_USER_BY_TOKEN'], data)
        if owner:
            if self.__isOwner(userId=owner['id']):# если уже создал свою команду
                    await self.sio.emit(self.MESSAGES['CREATE_TEAM'], False, room=sid)
                    return
            self.__deleteUserFromAllTeams(userId=owner['id'], sid=sid)
            common = Common()
            roomId = common.getRoomId()
            passwordTeam = common.generatePasswordForLobby()# генерируется из больших англ. букв длиной 7
            self.__teams[owner['id']] = self.__team(dict(
                                        teamId=owner['id'],
                                        name=data['name'],
                                        players=self.__player(dict(id=owner['id'], name=owner['name'])).get(),#преобразовать в JSON
                                        password=passwordTeam if data['isPrivate'] else '',
                                        isPrivate=data['isPrivate'],
                                        roomId=roomId
                                        ))
            self.sio.enter_room(sid, roomId)
            await self.sio.emit(self.MESSAGES['TEAM_LIST'], self.__teams[owner['id']].get(), room=roomId)
            await self.sio.emit(self.MESSAGES['CREATE_TEAM'], True, room=sid)
            return
        await self.sio.emit(self.MESSAGES['CREATE_TEAM'], False, room=sid)

    async def leaveTeam(self, sid, data):
        user = self.mediator.get(self.TRIGGERS['GET_USER_BY_TOKEN'], data)
        if user:
            team = self.__getTeamByUserId(userId=user['id'])
            if team:
                roomId = team.getSelf()['roomId']
                self.__deleteUserFromAllTeams(userId=user['id'], sid=sid)
                await self.sio.emit(self.MESSAGES['TEAM_LIST'], team.get(), room=roomId)
                await self.sio.emit(self.MESSAGES['LEAVE_TEAM'], dict(id=user['id']), room=roomId)
                return
        await self.sio.emit(self.MESSAGES['LEAVE_TEAM'], False, room=sid)

    async def readyToStart(self, sid, data):
        user= self.mediator.get(self.TRIGGERS['GET_USER_BY_TOKEN'], data)
        if user:
            team = self.__getTeamByUserId(userId=user['id']).getSelf()
            player = self.__findPlayerInTeam(userId=user['id'], team=team)
            if player:
                player['readyToStart'] = True
                if self.__checkTeamIsReady(team=team):
                    await self.sio.emit(self.MESSAGES['READY_TO_START'], True, room=team['roomId'])
                    # начать игру...
        await self.sio.emit(self.MESSAGES['READY_TO_START'], False, room=sid)

    async def kickFromTeam(self, sid, data):
        owner = self.mediator.get(self.TRIGGERS['GET_USER_BY_TOKEN'], data)
        ejectedId = data['id']
        if owner and ejectedId:
            team = self.__getTeamByUserId(userId=ejectedId)
            if self.__isOwner(userId=owner['id']) and team:
                roomId = team.getSelf()['roomId']
                self.sio.leave_room(sid, roomId)
                self.__deleteUserFromTeam(userId=ejectedId, team=team.getSelf())
                await self.sio.emit(self.MESSAGES['TEAM_LIST'], team.get(), room=roomId)
                await self.sio.emit(self.MESSAGES['KICK_FROM_TEAM'], True, room=sid)
                return
        await self.sio.emit(self.MESSAGES['KICK_FROM_TEAM'], False, room=sid)

    async def joinToTeam(self, sid, data):
        user = self.mediator.get(self.TRIGGERS['GET_USER_BY_TOKEN'], data)
        if user:
            team = self.__findTeamByPassword(password=data['password'])
            if team:
                self.__deleteUserFromAllTeams(userId=user['id'], sid=sid)
                team.getSelf()['players'].append(self.__player(dict(id=user['id'],
                                                                    name=user['name']
                                                                    )))
                self.sio.enter_room(sid, team.getSelf()['roomId'])
                await self.sio.emit(self.MESSAGES['TEAM_LIST'], team.get(), room=team.getSelf()['roomId'])
                await self.sio.emit(self.MESSAGES['JOIN_TO_TEAM'], True, room=sid)
                return
            await self.sio.emit(self.MESSAGES['JOIN_TO_TEAM'], False, room=sid)
        await self.sio.emit(self.MESSAGES['JOIN_TO_TEAM'], False, room=sid)

    async def inviteToTeam(self, sid, data):
        owner = self.mediator.get(self.TRIGGERS['GET_USER_BY_TOKEN'], data)
        inviteUserId = data['userId']
        isAgree = data['isAgree']
        if owner and inviteUserId and isAgree:
            if isAgree:
                if self.__isOwner(userId=owner['id']):
                    teamInviteUser = self.__getTeamByUserId(userId=inviteUserId)
                    if teamInviteUser:
                        self.__deleteUserFromTeam(userId=inviteUserId, team=teamInviteUser.getSelf())
                    user = self.mediator.get(self.TRIGGERS['GET_USER_BY_ID'], dict(id=inviteUserId))
                    if user:
                        team = self.__getTeamByUserId(userId=owner['id'])
                        team.getSelf()['players'].append(self.__player(dict(id=user['id'],
                                                                            name=user['name'])))
                        await self.sio.emit(self.MESSAGES['TEAM_LIST'], team.get(), room=team.getSelf()['roomId'])
                        await self.sio.emit(self.MESSAGES['INVITE_TO_TEAM'], True, room=sid)
            await self.sio.emit(self.MESSAGES['INVITE_TO_TEAM'], False, room=sid)
        await self.sio.emit(self.MESSAGES['INVITE_TO_TEAM'], False, room=sid)
