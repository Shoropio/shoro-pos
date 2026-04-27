import React from 'react'
import { useTheme } from '../contexts/ThemeContext'

export const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme()
  return (
    <button
      aria-label="Cambiar tema"
      aria-pressed={theme === 'dark'}
      onClick={toggleTheme}
      className="btn-ghost"
      style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
    >
      {theme === 'dark' ? '🌞' : '🌜'} Tema
    </button>
  )
}
