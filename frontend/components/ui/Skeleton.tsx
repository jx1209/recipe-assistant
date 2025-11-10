/**
 * Skeleton loader component for loading states
 */

import { HTMLAttributes } from 'react'
import { clsx } from 'clsx'

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  animation?: 'pulse' | 'wave' | 'none'
}

export function Skeleton({ 
  variant = 'rectangular',
  width,
  height,
  animation = 'pulse',
  className,
  ...props 
}: SkeletonProps) {
  return (
    <div
      className={clsx(
        'bg-gray-200 dark:bg-gray-700',
        {
          // Variants
          'rounded': variant === 'text',
          'rounded-full': variant === 'circular',
          'rounded-lg': variant === 'rectangular',
          
          // Animations
          'animate-pulse': animation === 'pulse',
          'shimmer-bg': animation === 'wave',
        },
        className
      )}
      style={{
        width: width || (variant === 'text' ? '100%' : undefined),
        height: height || (variant === 'text' ? '1em' : variant === 'circular' ? '40px' : '100px'),
      }}
      {...props}
    />
  )
}

export function SkeletonText({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={clsx('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton 
          key={i} 
          variant="text" 
          width={i === lines - 1 ? '70%' : '100%'}
        />
      ))}
    </div>
  )
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={clsx('p-6 bg-white rounded-xl shadow', className)}>
      <Skeleton variant="rectangular" height={200} className="mb-4" />
      <Skeleton variant="text" height={24} className="mb-2" />
      <SkeletonText lines={2} />
    </div>
  )
}

