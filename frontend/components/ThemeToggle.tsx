/**
 * theme toggle button component
 */

'use client'

import React from 'react'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from '@/contexts/ThemeContext'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="relative w-12 h-12 rounded-full flex items-center justify-center
                 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700
                 transition-all duration-300 shadow-sm hover:shadow-md
                 border border-gray-200 dark:border-gray-700"
      aria-label="Toggle theme"
    >
      {/* sun icon */}
      <Sun
        className={`absolute h-5 w-5 text-yellow-500 transition-all duration-300 ${
          theme === 'light' 
            ? 'rotate-0 scale-100 opacity-100' 
            : 'rotate-90 scale-0 opacity-0'
        }`}
      />
      
      {/* moon icon */}
      <Moon
        className={`absolute h-5 w-5 text-blue-500 transition-all duration-300 ${
          theme === 'dark' 
            ? 'rotate-0 scale-100 opacity-100' 
            : '-rotate-90 scale-0 opacity-0'
        }`}
      />
    </button>
  )
}
