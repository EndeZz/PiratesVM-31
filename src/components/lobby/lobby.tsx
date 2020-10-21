import React from 'react';
import styled from 'styled-components';
import Chat from '../common/chat/chat';

const StyledLobby = styled.div`
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 100vh;
  background: ${(({ theme }) => theme.colors.primary)};
`;

const Lobby = () => {
  return (
    <StyledLobby>
      <Chat />
    </StyledLobby>
  );
};

export default Lobby;
