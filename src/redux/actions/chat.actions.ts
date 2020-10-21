import { ADD_MESSAGES } from '../../constants/action-types.constants';
import { MessageInterface } from '../../components/common/messages/message/message';
import { SOCKET_EVENTS } from '../../constants/socket.constants';

export const addMessages = (messages: MessageInterface | MessageInterface[]) => ({
  type: ADD_MESSAGES,
  payload: messages instanceof Array ? messages : [messages],
});

export const sendMessage = (socket: SocketIOClient.Socket, data: { token: string, message: string }) => () => {
  socket.emit(SOCKET_EVENTS.SEND_MESSAGE, data);
};
