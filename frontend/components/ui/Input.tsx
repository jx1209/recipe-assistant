/**
 * Enhanced input component with icons and better styling
 */

import { InputHTMLAttributes, forwardRef, ReactNode } from 'react'
import { clsx } from 'clsx'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  variant?: 'default' | 'filled' | 'outline'
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className, 
    label, 
    error, 
    helperText, 
    leftIcon,
    rightIcon,
    variant = 'default',
    ...props 
  }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            {label}
            {props.required && <span className="text-danger-500 ml-1">*</span>}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {leftIcon}
            </div>
          )}
          
          <input
            ref={ref}
            className={clsx(
              'w-full px-4 py-2.5 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-0 text-gray-900 placeholder:text-gray-400',
              {
                // Variants
                'border border-gray-300 bg-white': variant === 'default',
                'border-0 bg-gray-100 focus:bg-white': variant === 'filled',
                'border-2 border-gray-300 bg-white': variant === 'outline',
                
                // Icons padding
                'pl-10': leftIcon,
                'pr-10': rightIcon,
                
                // Error state
                'border-danger-500 focus:ring-danger-500 focus:border-danger-500': error,
                'focus:ring-primary-500 focus:border-primary-500': !error,
              },
              className
            )}
            {...props}
          />
          
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
              {rightIcon}
            </div>
          )}
        </div>
        
        {error && (
          <p className="mt-1.5 text-sm text-danger-600 animate-fade-in">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

