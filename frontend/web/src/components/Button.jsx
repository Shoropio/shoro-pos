import React from 'react'

export const Button = ({ children, className = '', onClick, ...rest }) => (
  <button className={`btn ${className}`} onClick={onClick} {...rest}>
    {children}
  </button>
)
