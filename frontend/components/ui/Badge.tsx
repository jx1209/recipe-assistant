/**
 * Badge component for tags, labels, and status indicators
 */

import { HTMLAttributes } from 'react'
import { clsx } from 'clsx'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md' | 'lg'
  rounded?: boolean
  outline?: boolean
}

export function Badge({ 
  children, 
  variant = 'default', 
  size = 'md',
  rounded = false,
  outline = false,
  className, 
  ...props 
}: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium transition-colors',
        {
          // Variants - Solid
          'bg-gray-100 text-gray-700': variant === 'default' && !outline,
          'bg-primary-100 text-primary-700': variant === 'primary' && !outline,
          'bg-secondary-100 text-secondary-700': variant === 'secondary' && !outline,
          'bg-success-100 text-success-700': variant === 'success' && !outline,
          'bg-warning-100 text-warning-700': variant === 'warning' && !outline,
          'bg-danger-100 text-danger-700': variant === 'danger' && !outline,
          'bg-blue-100 text-blue-700': variant === 'info' && !outline,
          
          // Variants - Outline
          'border-2 border-gray-300 text-gray-700': variant === 'default' && outline,
          'border-2 border-primary-300 text-primary-700': variant === 'primary' && outline,
          'border-2 border-secondary-300 text-secondary-700': variant === 'secondary' && outline,
          'border-2 border-success-300 text-success-700': variant === 'success' && outline,
          'border-2 border-warning-300 text-warning-700': variant === 'warning' && outline,
          'border-2 border-danger-300 text-danger-700': variant === 'danger' && outline,
          'border-2 border-blue-300 text-blue-700': variant === 'info' && outline,
          
          // Sizes
          'px-2 py-0.5 text-xs': size === 'sm',
          'px-2.5 py-1 text-sm': size === 'md',
          'px-3 py-1.5 text-base': size === 'lg',
          
          // Rounded
          'rounded-full': rounded,
          'rounded-md': !rounded,
        },
        className
      )}
      {...props}
    >
      {children}
    </span>
  )
}

