import { createGlobalStyle  } from 'styled-components';
import { normalize } from 'styled-normalize';
import { colors } from './colors.theme';
import { scrollbar } from './scrollbar.theme';

export const GlobalStyle = createGlobalStyle`
  ${normalize}

  body {
    font-size: 10px;
    font-weight: normal;
    font-family: 'Roboto', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  #root {
    min-width: 100vw;
    min-height: 100vh;
  }

  ${colors}
`;

export const AppTheme = {
  lineHeights: {
    solid: 1,
    text: 1.15,
    title: 1.25,
    double: 2,
  },
  fontWeights: [100, 200, 300, 400, 500, 600, 700, 800, 900],
  fonts: {
    Roboto: 'Roboto, sans-serif',
  },
  zIndexes: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],

  colors,
  scrollbar,
};
