/**
 * card component
 */

'use client'

import Link from 'next/link'
import Image from 'next/image'
import { Recipe } from '@/lib/api'
import { Clock, Users, Star, Heart, ChefHat } from 'lucide-react'
import { useState } from 'react'

type RecipeCardProps = {
  recipe: Recipe
  selectable?: boolean
  selected?: boolean
  onSelect?: (id: number) => void
  external?: boolean
  sourceName?: string | null
}

export function RecipeCard({ 
  recipe, 
  selectable = false,
  selected = false,
  onSelect,
  external,
  sourceName
}: RecipeCardProps) {
  const [imageError, setImageError] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  const totalTime = (recipe.prep_time || 0) + (recipe.cook_time || 0)
  const displayRating = recipe.average_rating?.toFixed(1) || null

  return (
    <div 
      className="group relative bg-white dark:bg-gray-800 rounded-none overflow-hidden 
                 transition-all duration-300 hover:shadow-xl border-b border-gray-100 dark:border-gray-700"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Link href={`/recipe/${recipe.id}`} className="block">
        {/* Image Container */}
        <div className="relative aspect-[4/3] overflow-hidden bg-gray-100 dark:bg-gray-700">
          {recipe.image_url && !imageError ? (
            <Image
              src={recipe.image_url}
              alt={recipe.title}
              fill
              className={`object-cover transition-transform duration-700 ${
                isHovered ? 'scale-105' : 'scale-100'
              }`}
              onError={() => setImageError(true)}
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-800 dark:to-gray-700">
              <ChefHat className="w-16 h-16 text-gray-300 dark:text-gray-600" />
            </div>
          )}

          {/* Overlay Badges */}
          <div className="absolute top-3 left-3 flex flex-col gap-2">
            {recipe.difficulty && (
              <span className={`
                px-2.5 py-1 text-xs font-medium uppercase tracking-wide rounded-sm
                ${recipe.difficulty === 'Easy' ? 'bg-green-600' : 
                  recipe.difficulty === 'Medium' ? 'bg-yellow-600' : 'bg-red-600'}
                text-white shadow-lg
              `}>
                {recipe.difficulty}
              </span>
            )}
            {totalTime <= 30 && totalTime > 0 && (
              <span className="px-2.5 py-1 text-xs font-medium uppercase tracking-wide bg-blue-600 text-white rounded-sm shadow-lg">
                Quick Meal
              </span>
            )}
            {recipe.is_favorite && (
              <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm p-1.5 rounded-sm shadow-lg">
                <Heart className="w-4 h-4 text-red-500 fill-red-500" />
              </div>
            )}
          </div>

          {/* Selection Checkbox */}
          {selectable && (
            <div 
              className="absolute top-3 right-3 z-10"
              onClick={(e) => {
                e.preventDefault()
                onSelect?.(recipe.id)
              }}
            >
              <div className={`
                w-6 h-6 rounded-sm border-2 flex items-center justify-center cursor-pointer
                transition-all duration-200 backdrop-blur-sm
                ${selected 
                  ? 'bg-primary-600 border-primary-600' 
                  : 'bg-white/80 border-gray-300 dark:bg-gray-800/80 dark:border-gray-600 hover:border-primary-500'
                }
              `}>
                {selected && (
                  <svg className="w-4 h-4 text-white" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-5">
          {/* Title */}
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2 line-clamp-2 
                         group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-200
                         leading-tight tracking-tight">
            {recipe.title}
          </h3>

          {/* Description */}
          {recipe.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2 leading-relaxed">
              {recipe.description}
            </p>
          )}

          {/* Meta Info */}
          <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-3 border-t border-gray-100 dark:border-gray-700 pt-3">
            {totalTime > 0 && (
              <div className="flex items-center gap-1.5">
                <Clock className="w-4 h-4" />
                <span className="font-medium">{totalTime} min</span>
              </div>
            )}
            {recipe.servings && (
              <div className="flex items-center gap-1.5">
                <Users className="w-4 h-4" />
                <span className="font-medium">{recipe.servings} servings</span>
              </div>
            )}
            {displayRating && (
              <div className="flex items-center gap-1.5 ml-auto">
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                <span className="font-semibold text-gray-900 dark:text-gray-100">{displayRating}</span>
                {recipe.rating_count > 0 && (
                  <span className="text-xs">({recipe.rating_count})</span>
                )}
              </div>
            )}
          </div>

          {/* Tags */}
          {recipe.tags && recipe.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {recipe.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-1 rounded-sm bg-gray-50 dark:bg-gray-700/50 
                           text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600
                           font-medium"
                >
                  {tag}
                </span>
              ))}
              {recipe.tags.length > 3 && (
                <span className="text-xs px-2 py-1 text-gray-500 dark:text-gray-400 font-medium">
                  +{recipe.tags.length - 3} more
                </span>
              )}
            </div>
          )}

          {/* External Source */}
          {external && sourceName && (
            <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
              <span className="text-xs text-gray-500 dark:text-gray-400 italic">
                From {sourceName}
              </span>
            </div>
          )}
        </div>
      </Link>
    </div>
  )
}
