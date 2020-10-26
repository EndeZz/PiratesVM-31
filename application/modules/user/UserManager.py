import hashlib
import random

from application.modules.BaseManager import BaseManager
from application.modules.user.User import User


class UserManager(BaseManager):
    def __init__(self, db, mediator, sio, MESSAGES):
        super().__init__(db, mediator, sio, MESSAGES)

        self.users = {}

        # регистрируем триггеры
        self.mediator.set(self.TRIGGERS['GET_USER_BY_TOKEN'], self.__getUserByToken)
        self.mediator.set(self.TRIGGERS['GET_USER_BY_ID'], self.__getUserByID)
        # регистрируем события
        self.sio.on(self.MESSAGES['USER_LOGIN'], self.auth)
        self.sio.on(self.MESSAGES['USER_LOGOUT'], self.logout)
        self.sio.on(self.MESSAGES['USER_SIGNUP'], self.registration)
        self.sio.on(self.MESSAGES['USERS_ONLINE'], self.getUsersOnline)
        self.sio.on('disconnect', self.logout)

    # def __getUserByToken1(self, data):
    #     return self.db.getUserByToken(data['token'])

    def __generateToken(self, login):
        if login:
            randomInt = random.randint(0, 100000)
            return self.__generateHash(login, str(randomInt))

    def __generateHash(self, str1, str2=""):
        if type(str1) == str and type(str2) == str:
            return hashlib.md5((str1 + str2).encode("utf-8")).hexdigest()
        return None

    def __getUserByToken(self, data=None):
        if 'token' in data:
            for user in self.users:
                if user['token'] == data['token']:
                    return user.getSelf()
        return None

    def __getUserById(self, data=None):
        if 'id' in data:
            for user in self.users:
                if user['id'] == data['id']:
                    return user.getSelf()
        return None

    def __getUserBySid(self, sid=None):
        if sid:
            for user in self.users:
                if user['sid'] == sid:
                    return user
        return None

    def __getUsersOnline(self):
        users = []
        for key in self.users:
            users.append(self.users[key].get())
        return users

    async def getUsersOnline(self, sid):
        await self.sio.emit(self.MESSAGES['USERS_ONLINE'], self.__getUsersOnline())

    async def registration(self, sid, data):
        name = data['login']
        login = data['login']
        password = data['hash']
        if name and login and password:
            user = self.db.getUserByLogin(login=login)
            if user:
                await self.sio.emit(self.MESSAGES['USER_SIGNUP'], False, room=sid)
            token = self.__generateToken(login)
            self.db.insertUser(name=name, login=login, password=password, token=token)
            userData = self.db.getUserByToken(token)
            userData['sid'] = sid
            self.users[userData['id']] = User(userData)
            await self.sio.emit(self.MESSAGES['USER_SIGNUP'], self.users[userData['id']].getSelf(), room=sid)
            await self.getUsersOnline(sid)
        await self.sio.emit(self.MESSAGES['USER_SIGNUP'], False, room=sid)

    async def auth(self, sid, data):
        login = data['login']
        hash = data['hash']
        rnd = data['random']
        if login and hash and rnd:
            hashDB = self.db.getHashByLogin(login=login)
            if self.__generateHash(hashDB, str(rnd)) == hash:
                token = self.__generateToken(login)
                # self.mediator.call(self.EVENTS['UPDATE_TOKEN_BY_LOGIN'], dict(login=login, token=token))
                self.db.updateTokenByLogin(login, token)
                userData = self.db.getUserByToken(token)
                userData['sid'] = sid
                self.users[userData['id']] = User(userData)
                # добавляем пользователя в список пользователей онлайн
                self.mediator.call(self.EVENTS['ADD_USER_ONLINE'], dict(token=token, sid=sid, coord=None))
                await self.sio.emit(self.MESSAGES['USER_LOGIN'], self.users[userData['id']].getSelf(), room=sid)
                await self.getUsersOnline(sid)
                return True
        await self.sio.emit(self.MESSAGES['USER_LOGIN'], False, room=sid)
        return False

    async def logout(self, sid, data):
        user = None
        # если токен, то взять юзера по токену (из self.users)
        if 'token' in data:
            user = self.__getUserByToken(token=data['token'])
        # иначе взять по sid (из self.users)
        else:
            user = self.__getUserBySid(sid=sid)
        if user is not None:
            # бросить событие, что пользователь мухожук
            self.mediator.call(self.EVENTS['USER_LOGOUT'], user)
            # удалить пользователя из self.users
            del self.users[user['id']]
            # перезаписать токен в БД
            self.db.updateUserTokenById(id=user['id'], token='')
            # ответить пользователю о результатах его логаута
            await self.sio.emit(self.MESSAGES['USER_LOGOUT'], True, room=sid)
            return
        await self.sio.emit(self.MESSAGES['USER_LOGOUT'], False, room=sid)
