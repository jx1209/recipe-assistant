/**
 * Skeleton loader component for loading states
 */

import React from 'react'

export const Skeleton = ({ className = '' }: { className?: string }) => (
  <div className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${className}`} />
)

export const RecipeCardSkeleton = () => (
  <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-sm animate-pulse">
    {/* image skeleton */}
    <div className="h-52 bg-gray-200 dark:bg-gray-700" />
    
    {/* content skeleton */}
    <div className="p-5 space-y-3">
      {/* title */}
      <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
      
      {/* description */}
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6" />
      </div>
      
      {/* meta info */}
      <div className="flex gap-4 pt-2">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20" />
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24" />
      </div>
      
      {/* tags */}
      <div className="flex gap-2 pt-2">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-full w-16" />
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-full w-20" />
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-full w-14" />
      </div>
    </div>
  </div>
)

export const RecipeDetailSkeleton = () => (
  <div className="max-w-7xl mx-auto px-4 py-8 animate-pulse">
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* image skeleton */}
      <div className="h-96 bg-gray-200 dark:bg-gray-700 rounded-2xl" />
      
      {/* info skeleton */}
      <div className="space-y-6">
        <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
        </div>
      </div>
    </div>
  </div>
)

export const ListItemSkeleton = () => (
  <div className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg animate-pulse">
    <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded" />
    <div className="flex-1 space-y-2">
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3" />
      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
    </div>
  </div>
)

export const ProfileSkeleton = () => (
  <div className="max-w-4xl mx-auto px-4 py-8 space-y-6 animate-pulse">
    {/* header */}
    <div className="flex items-center gap-4">
      <div className="w-20 h-20 bg-gray-200 dark:bg-gray-700 rounded-full" />
      <div className="space-y-2">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-40" />
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32" />
      </div>
    </div>
    
    {/* sections */}
    {[1, 2, 3].map((i) => (
      <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-6 space-y-4">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/4" />
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-4/5" />
        </div>
      </div>
    ))}
  </div>
)

export const GridSkeleton = ({ count = 6 }: { count?: number }) => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
    {Array.from({ length: count }).map((_, i) => (
      <RecipeCardSkeleton key={i} />
    ))}
  </div>
)

export const FormSkeleton = () => (
  <div className="space-y-6 animate-pulse">
    {[1, 2, 3, 4].map((i) => (
      <div key={i} className="space-y-2">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24" />
        <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded w-full" />
      </div>
    ))}
  </div>
)
