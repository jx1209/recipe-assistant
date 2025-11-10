/**
 * Enhanced button component with multiple variants and animations
 */

import { ButtonHTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'
import { Loader2 } from 'lucide-react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost' | 'success' | 'gradient'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  isLoading?: boolean
  fullWidth?: boolean
  rounded?: 'normal' | 'full'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant = 'primary', 
    size = 'md', 
    isLoading, 
    disabled, 
    fullWidth = false,
    rounded = 'normal',
    children, 
    ...props 
  }, ref) => {
    return (
      <button
        ref={ref}
        className={clsx(
          'inline-flex items-center justify-center font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 shadow-sm hover:shadow-md',
          {
            // Variants
            'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800 focus:ring-primary-500 hover:shadow-primary-500/25': variant === 'primary',
            'bg-gray-200 text-gray-900 hover:bg-gray-300 active:bg-gray-400 focus:ring-gray-500': variant === 'secondary',
            'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 active:bg-primary-100 focus:ring-primary-500 bg-white': variant === 'outline',
            'bg-danger-600 text-white hover:bg-danger-700 active:bg-danger-800 focus:ring-danger-500 hover:shadow-danger-500/25': variant === 'danger',
            'text-gray-700 hover:bg-gray-100 active:bg-gray-200 focus:ring-gray-500 shadow-none': variant === 'ghost',
            'bg-success-600 text-white hover:bg-success-700 active:bg-success-800 focus:ring-success-500 hover:shadow-success-500/25': variant === 'success',
            'bg-gradient-primary text-white hover:shadow-lg hover:shadow-primary-500/30 focus:ring-primary-500': variant === 'gradient',
            
            // Sizes
            'px-2 py-1 text-xs': size === 'xs',
            'px-3 py-1.5 text-sm': size === 'sm',
            'px-4 py-2.5 text-base': size === 'md',
            'px-6 py-3 text-lg': size === 'lg',
            'px-8 py-4 text-xl': size === 'xl',
            
            // Full Width
            'w-full': fullWidth,
            
            // Rounded
            'rounded-lg': rounded === 'normal',
            'rounded-full': rounded === 'full',
          },
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && (
          <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
        )}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

