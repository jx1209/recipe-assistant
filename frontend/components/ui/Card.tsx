/**
 * Enhanced card component with multiple variants and animations
 */

import { HTMLAttributes, ReactNode } from 'react'
import { clsx } from 'clsx'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  variant?: 'default' | 'bordered' | 'elevated' | 'glass' | 'gradient'
  hover?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export function Card({ 
  children, 
  variant = 'default', 
  hover = false,
  padding,
  className, 
  ...props 
}: CardProps) {
  return (
    <div
      className={clsx(
        'rounded-xl transition-all duration-300',
        {
          // Variants
          'bg-white shadow-soft': variant === 'default',
          'bg-white border-2 border-gray-200': variant === 'bordered',
          'bg-white shadow-elevation-2': variant === 'elevated',
          'glass backdrop-blur-lg': variant === 'glass',
          'bg-gradient-primary text-white shadow-lg': variant === 'gradient',
          
          // Hover effect
          'card-hover cursor-pointer': hover,
          
          // Padding (if set directly on card)
          'p-2': padding === 'sm',
          'p-4': padding === 'md',
          'p-6': padding === 'lg',
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
}

export function CardHeader({ children, className, ...props }: CardHeaderProps) {
  return (
    <div className={clsx('px-6 py-5 border-b border-gray-200', className)} {...props}>
      {children}
    </div>
  )
}

interface CardContentProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
}

export function CardContent({ children, className, ...props }: CardContentProps) {
  return (
    <div className={clsx('px-6 py-5', className)} {...props}>
      {children}
    </div>
  )
}

interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
}

export function CardFooter({ children, className, ...props }: CardFooterProps) {
  return (
    <div className={clsx('px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl', className)} {...props}>
      {children}
    </div>
  )
}

