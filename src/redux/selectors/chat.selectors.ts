import { CHAT_NAMES, ChatStateInterface } from '../../constants/chat.constants';
import { MessageInterface } from '../../components/common/messages/message/message';

export const selectChat = ({ chat }): ChatStateInterface => chat;
export const selectMessages = ({ chat }): MessageInterface[] => chat[CHAT_NAMES.messages];
