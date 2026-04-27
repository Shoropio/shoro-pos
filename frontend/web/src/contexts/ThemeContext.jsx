import React, { createContext, useContext, useEffect, useState } from 'react'

const ThemeContext = createContext({ theme: 'light', toggleTheme: () => {} })

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => localStorage.getItem('shoro_theme') || 'light')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('shoro_theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme((t) => (t === 'light' ? 'dark' : 'light'))

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
