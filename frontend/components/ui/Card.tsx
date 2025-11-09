/**
 * reusable card component
 */

import { HTMLAttributes, ReactNode } from 'react'
import { clsx } from 'clsx'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  variant?: 'default' | 'bordered' | 'elevated'
}

export function Card({ children, variant = 'default', className, ...props }: CardProps) {
  return (
    <div
      className={clsx(
        'rounded-xl',
        {
          'bg-white shadow': variant === 'default',
          'bg-white border-2 border-gray-200': variant === 'bordered',
          'bg-white shadow-lg': variant === 'elevated',
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
    <div className={clsx('px-6 py-4 border-b border-gray-200', className)} {...props}>
      {children}
    </div>
  )
}

interface CardContentProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
}

export function CardContent({ children, className, ...props }: CardContentProps) {
  return (
    <div className={clsx('px-6 py-4', className)} {...props}>
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

