import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { branding } from '../config/branding';

const BrandLogo = ({ variant = 'full', className = '', size = 'default' }) => {
  const { theme } = useTheme();
  const logo = branding.logos[theme][variant];

  // Size variants for more control
  const sizeMap = {
    sm: '32px',
    default: '48px',
    md: '56px',
    lg: '64px',
    xl: '80px'
  };

  const height = sizeMap[size] || sizeMap.default;

  return (
    <img
      src={logo}
      alt={branding.companyName}
      className={`transition-all duration-300 ${className}`}
      style={{ height, width: 'auto', objectFit: 'contain' }}
      data-testid="brand-logo"
    />
  );
};

export default BrandLogo;
