import { IPartialTheme } from '@uifabric/styling';
import { DefaultPalette } from '@uifabric/styling';

export const LightTheme: IPartialTheme = {
    palette: DefaultPalette,
};


export const DarkTheme: IPartialTheme = {
    palette: {
        neutralLighterAlt: '#282828',
        neutralLighter: '#282828',
        neutralLight: '#282828',
        neutralQuaternaryAlt: '#484848',
        neutralQuaternary: '#4f4f4f',
        neutralTertiaryAlt: '#6d6d6d',
        neutralTertiary: '#c8c8c8',
        neutralSecondary: '#d0d0d0',
        neutralPrimaryAlt: '#dadada',
        neutralPrimary: '#ffffff',
        neutralDark: '#ffffff',
        black: '#282828',
        white: '#282828',
        themePrimary: '#ffaff3',
        themeLighterAlt: '#020609',
        themeLighter: '#091823',
        themeLight: '#112d43',
        themeTertiary: '#235a85',
        themeSecondary: '#3385c3',
        themeDarkAlt: '#FF99F0',
        themeDark: '#FF85ED',
        themeDarker: '#8ac2ec',
        accent: '#3a96dd'
    }
};