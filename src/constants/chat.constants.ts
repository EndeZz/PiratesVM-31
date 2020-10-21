import { MessageInterface } from '../components/common/messages/message/message';

export const MAX_CHAT_INPUT_LENGTH = 300;

export interface ChatStateInterface {
  messages: MessageInterface[];
}

export const CHAT_INITIAL_STATE: ChatStateInterface = {
  messages: [],
};

export const CHAT_NAMES = {
  messages: 'messages',
};
