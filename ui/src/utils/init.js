export const getInitThemeStyle = (colorTheme, customColorTheme) => {
  if (colorTheme === 'custom') {
    return `--background-color: ${customColorTheme.background};
  --text-color: ${customColorTheme.textColor};
  --sub-text-color: ${customColorTheme.subTextColor};
  --inverted-text-color: ${customColorTheme.invertedTextColor};

  --highlight-monochrome-color: #e6e6e6;
  --light-monochrome-color: #f3f3f3;
  --monochrome-color: #c3c3c382;
  --dark-monochrome-color: #9e9e9eab;

  --light-theme-color: #eeeeeeb3;
  --theme-color: ${customColorTheme.themeColor};
  --dark-theme-color: ${customColorTheme.themeColor};
  --box-background: #ffffffb0;
  --profile-border-color: rgba(87, 87, 87, 0.326);`
  } else {
    return ''
  }
}
