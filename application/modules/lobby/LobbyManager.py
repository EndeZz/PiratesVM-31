from application.modules.BaseManager import BaseManager
# генерация пароля для лобби и roomId
from application.modules.common.Common import Common
from .Player import Player
from .Team import Team


class LobbyManager(BaseManager):
    def __init__(self, mediator, sio, MESSAGES):
        super().__init__(mediator=mediator, sio=sio, MESSAGES=MESSAGES)
        self.__common = Common
        self.__team = Team
        self.__player = Player
        self.__teams = {}

        #TRIGGERS
        #получение user по token
        #EVENTS
        #self.mediator.subscribe(self.EVENTS['USER_LOGOUT'], self.leaveTeam)
        #Если чел дисконектнулся, тогда вызывать leaveTeam и вызывать событие logout

        @sio.event
        def disconnect(sid):
            print('я тут ', sid)

    def test(self, token=None):
        test = token or '6666'

        self.__teams[1] = self.__team(dict(
            teamId=1,
            name='QQWWE',
            players=[
                self.__player(dict(id=1, name='1231')),
                self.__player(dict(id=2, name='1231', readyToStart=True))],
            roomId="333"
        ))
        print(self.__teams, test)
    ''' self.sio.on(self.MESSAGES['CREATE_TEAM'], self.createTeam)
        # self.sio.on(self.MESSAGES['KICK_FROM_TEAM'], self.kickFromTeam)
        self.sio.on(self.MESSAGES['LEAVE_TEAM'], self.leaveTeam)
        self.sio.on(self.MESSAGES['READY_TO_START'], self.readyToStart)
        self.sio.on(self.MESSAGES['JOIN_TO_TEAM'], self.joinToTeam)
        self.sio.on(self.MESSAGES['INVITE_TO_TEAM'], self.inviteToTeam)

    def __findUserInTeams(self, token):
        for teamKey in self.__teams:
            for user in self.__teams[teamKey]['players']:
                if user['token'] == token:
                    return user, teamKey
        return None, None

    def __checkTeamIsReady(self, teamId):
        for user in self.__teams[teamId]['players']:
            if not user['readyToStart']:
                return False
        return True

    def __getTeamIdByToken(self, token):
        for teamId in self.__teams:
            users = self.__teams[teamId]['players']
            for user in users:
                if user['token'] == token:
                    userInTeamId = teamId
                    return userInTeamId
        return None

    def __deleteEmptyTeams(self):
        for teamId in self.__teams:
            if len(self.__teams[teamId]['players']) == 0:
                del self.__teams[teamId]
                return

    def __deleteFromTeam(self, userToken, teamId):
        users = self.__teams[teamId]['players']
        for user in users:
            if user['token'] == userToken:
                self.__teams[teamId]['players'].remove(user)
                return

    def __deleteUserFromAllTeams(self, userToken, sid):
        for teamId in self.__teams:
            for user in self.__teams[teamId]['players']:
                if user['token'] == userToken:
                    self.sio.leave_room(sid, self.__teams[teamId]['roomId'])
                    if userToken == self.__teams[teamId]:
                        del self.__teams[teamId]
                    self.__deleteFromTeam(user['token'], teamId)
                    continue
        self.__deleteEmptyTeams()

    async def readyToStart(self, sid, data):
        user, teamId = self.__findUserInTeams(data['token'])
        if user and teamId:
            user['readyToStart'] = True
            if self.__checkTeamIsReady(teamId):
                for user in self.__teams[teamId]['players']:
                    await self.sio.emit(self.MESSAGES['READY_TO_START'], {}, user['sid'])
                    # начать игру...
        await self.sio.emit(self.MESSAGES['READY_TO_START'], False)

    async def createTeam(self, sid, data):
        user = self.mediator.get(self.TRIGGERS['GET_USER_BY_TOKEN'], data)  # создатель (data=token пока)
        if user:
            for teamId in self.__teams:
                if user['token'] == teamId:  # если уже создал свою команду
                    await self.sio.emit(self.MESSAGES['CREATE_TEAM'], False)
                    return
            self.__deleteUserFromAllTeams(user['token'], sid)
            roomId = self.__common.getRoomId()
            passwordTeam = self.__common.generatePasswordForLobby()  # генерируется из больших англ. букв длиной 7
            self.__teams[user['token']] = dict(passwordTeam=passwordTeam,
                                               players=[dict(token=user['token'],
                                                               sid=sid,
                                                               readyToStart=False)],
                                               roomId=roomId)
            self.sio.enter_room(sid, roomId)
            await self.sio.emit(self.MESSAGES['TEAM_LIST'], self.__teams)
            await self.sio.emit(self.MESSAGES['CREATE_TEAM'], True)
            return
        await self.sio.emit(self.MESSAGES['CREATE_TEAM'], False)

    # TODO
    # Переделать. Неправильная логика(Это leaveTeam, а не kick)
    async def kickFromTeam(self, sid, data):
        user = self.mediator.get(self.TRIGGERS['GET_USER_BY_TOKEN'], data)
        if user:
            teamId = self.__getTeamIdByToken(user['token'])
            team = self.__getTeamByToken(user['token'])
            if teamId:
                self.__deleteFromTeam(user['token'], teamId)
                await self.sio.emit(self.MESSAGES['TEAM_LIST'], self.__teams)
                await self.sio.emit(self.MESSAGES['KICK_FROM_TEAM'], dict(token=user['token']))
                self.sio.leave_room(sid, team['roomId'])
                return
        await self.sio.emit(self.MESSAGES['KICK_FROM_TEAM'], False)

    async def leaveTeam(self, sid, data):
        user = self.mediator.get(self.TRIGGERS['GET_USER_BY_TOKEN'], data)
        if user:
            self.__deleteUserFromAllTeams(user['token'], sid)
            await self.sio.emit(self.MESSAGES['TEAM_LIST'], self.__teams)
            await self.sio.emit(self.MESSAGES['LEAVE_TEAM'], dict(token=user['token']))
            return
        await self.sio.emit(self.MESSAGES['LEAVE_TEAM'], False)

    async def joinToTeam(self, sio, data):
        user = self.mediator.get(self.TRIGGERS['GET_USER_BY_TOKEN'], data)
        if user:
            for key in self.__teams.keys():
                if key == data['teamId'] and self.__teams[key]['passwordTeam'] == data['passwordTeam']:
                    self.__teams[key]['players'].append({'token': data['userToken']})
                    await self.sio.emit(self.MESSAGES['TEAM_LIST'], self.__teams)
                    await self.sio.emit(self.MESSAGES['JOIN_TO_TEAM'], True)
                    return True
                else:
                    await self.sio.emit(self.MESSAGES['JOIN_TO_TEAM'], False)
                    return False
        await self.sio.emit(self.MESSAGES['JOIN_TO_TEAM'], False)

    async def inviteToTeam(self, sid, data):
        inviter, teamId = self.__findUserInTeams(data['token'])
        # проверяем состоит ли в команде сам пригласитель
        if teamId == data['teamId']:
            invited, teamId = self.__findUserInTeams(data['invitedToken'])
            # проверяем состоит ли в какой либо команде приглашённый
            if invited is None and teamId is None:
                teamId = data['teamId']
                invitedSid = self.mediator.get(self.TRIGGERS['GET_SID_BY_TOKEN'], dict(token=data['invitedToken']))
                # отправляем приглашённому teamId и passwordTeam
                await self.sio.emit(
                    self.MESSAGES['INVITE_TO_TEAM'],
                    dict(teamId=teamId, passwordTeam=self.__teams[teamId]['passwordTeam']),
                    invitedSid
                )
                return
        await self.sio.emit(self.MESSAGES['INVITE_TO_TEAM'], False, sid)'''
