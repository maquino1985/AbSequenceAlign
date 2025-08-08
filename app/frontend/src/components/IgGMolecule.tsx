import React from 'react';

interface IgGMoleculeProps {
  size?: number;
}

export const IgGMolecule: React.FC<IgGMoleculeProps> = ({ size = 32 }) => {
  const darkMode = false; // This will be controlled by theme context in the future
  
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      xmlns="http://www.w3.org/2000/svg"
      style={{
        filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))',
      }}
    >
      <defs>
        <linearGradient id="primaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={darkMode ? "#0A84FF" : "#007AFF"} />
          <stop offset="50%" stopColor={darkMode ? "#4DA3FF" : "#4DA3FF"} />
          <stop offset="100%" stopColor={darkMode ? "#0056CC" : "#0056CC"} />
        </linearGradient>
        
        <linearGradient id="secondaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={darkMode ? "#FF6B6B" : "#FF3B30"} />
          <stop offset="50%" stopColor={darkMode ? "#FF8E8E" : "#FF6B6B"} />
          <stop offset="100%" stopColor={darkMode ? "#CC5555" : "#CC4444"} />
        </linearGradient>
        
        <linearGradient id="tertiaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={darkMode ? "#4ECDC4" : "#34C759"} />
          <stop offset="50%" stopColor={darkMode ? "#6EDDD6" : "#4ECDC4"} />
          <stop offset="100%" stopColor={darkMode ? "#3DAFA8" : "#2A9D8F"} />
        </linearGradient>
      </defs>
      
      <g transform="translate(50, 50)">
        {/* Main Y-shaped structure */}
        <g>
          {/* Top arm (left) */}
          <path
            d="M -15 -25 L -25 -35 L -20 -40 L -10 -30 Z"
            fill="url(#primaryGradient)"
            stroke={darkMode ? "#0A84FF" : "#007AFF"}
            strokeWidth="1"
          />
          
          {/* Top arm (right) */}
          <path
            d="M 15 -25 L 25 -35 L 20 -40 L 10 -30 Z"
            fill="url(#primaryGradient)"
            stroke={darkMode ? "#0A84FF" : "#007AFF"}
            strokeWidth="1"
          />
          
          {/* Center stem */}
          <rect
            x="-3"
            y="-25"
            width="6"
            height="50"
            fill="url(#primaryGradient)"
            stroke={darkMode ? "#0A84FF" : "#007AFF"}
            strokeWidth="1"
            rx="3"
          />
          
          {/* Bottom base */}
          <ellipse
            cx="0"
            cy="30"
            rx="12"
            ry="8"
            fill="url(#secondaryGradient)"
            stroke={darkMode ? "#FF6B6B" : "#FF3B30"}
            strokeWidth="1"
          />
          
          {/* Binding sites */}
          <circle
            cx="-15"
            cy="-30"
            r="3"
            fill="url(#tertiaryGradient)"
            stroke={darkMode ? "#4ECDC4" : "#34C759"}
            strokeWidth="1"
          />
          
          <circle
            cx="15"
            cy="-30"
            r="3"
            fill="url(#tertiaryGradient)"
            stroke={darkMode ? "#4ECDC4" : "#34C759"}
            strokeWidth="1"
          />
          
          {/* Center binding site */}
          <circle
            cx="0"
            cy="0"
            r="4"
            fill="url(#tertiaryGradient)"
            stroke={darkMode ? "#4ECDC4" : "#34C759"}
            strokeWidth="1"
          />
        </g>
        
        {/* Animation */}
        <animateTransform
          attributeName="transform"
          type="rotate"
          values="0 0 0;360 0 0"
          dur="15s"
          repeatCount="indefinite"
          additive="sum"
        />
      </g>
    </svg>
  );
};
