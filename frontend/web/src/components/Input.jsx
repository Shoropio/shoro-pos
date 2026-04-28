import React from 'react'

export const Input = ({ value, onChange, ...rest }) => (
  <input className="input" value={value} onChange={onChange} {...rest} />
)
