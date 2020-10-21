import { ADD_MESSAGES } from '../../constants/action-types.constants';
import { CHAT_INITIAL_STATE } from '../../constants/chat.constants';

export default (state = CHAT_INITIAL_STATE, action) => {
  switch (action.type) {
    case ADD_MESSAGES:
      return {
        ...state,
        messages: [...state.messages, ...action.payload],
      };
    default:
      return state;
  }
};
