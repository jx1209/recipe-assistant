/**
 * Tooltip component for helpful hints
 */

'use client'

import { ReactNode, useState } from 'react'
import { clsx } from 'clsx'

interface TooltipProps {
  content: ReactNode
  children: ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
  className?: string
}

export function Tooltip({ 
  content, 
  children, 
  position = 'top',
  className 
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      
      {isVisible && (
        <div
          className={clsx(
            'absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg whitespace-nowrap animate-fade-in',
            {
              'bottom-full left-1/2 -translate-x-1/2 mb-2': position === 'top',
              'top-full left-1/2 -translate-x-1/2 mt-2': position === 'bottom',
              'right-full top-1/2 -translate-y-1/2 mr-2': position === 'left',
              'left-full top-1/2 -translate-y-1/2 ml-2': position === 'right',
            },
            className
          )}
        >
          {content}
          
          {/* Arrow */}
          <div
            className={clsx(
              'absolute w-2 h-2 bg-gray-900 transform rotate-45',
              {
                'top-full left-1/2 -translate-x-1/2 -mt-1': position === 'top',
                'bottom-full left-1/2 -translate-x-1/2 -mb-1': position === 'bottom',
                'top-1/2 left-full -translate-y-1/2 -ml-1': position === 'left',
                'top-1/2 right-full -translate-y-1/2 -mr-1': position === 'right',
              }
            )}
          />
        </div>
      )}
    </div>
  )
}

