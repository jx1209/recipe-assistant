/**
 * recipe card component for displaying recipe summaries
 */

import Link from 'next/link'
import { Clock, Users, Star } from 'lucide-react'
import { Card, CardContent } from './ui/Card'

type RecipeCardProps = {
  id?: number
  title: string
  description: string | null
  tags?: string[]
  prepTime?: number | null
  cookTime?: number | null
  servings?: number
  averageRating?: number | null
  imageUrl?: string | null
  difficulty?: string | null
}

export function RecipeCard({ 
  id, 
  title, 
  description, 
  tags = [], 
  prepTime, 
  cookTime,
  servings,
  averageRating,
  imageUrl,
  difficulty
}: RecipeCardProps) {
  const totalTime = (prepTime || 0) + (cookTime || 0)
  
  const content = (
    <Card className="hover:shadow-xl transition-all duration-200 cursor-pointer group h-full">
      {imageUrl && (
        <div className="h-48 bg-gray-200 rounded-t-xl overflow-hidden">
          <img 
            src={imageUrl} 
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
          />
        </div>
      )}
      <CardContent className="space-y-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {description}
            </p>
          )}
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-500">
          {totalTime > 0 && (
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              <span>{totalTime} min</span>
            </div>
          )}
          {servings && (
            <div className="flex items-center gap-1">
              <Users className="h-4 w-4" />
              <span>{servings}</span>
            </div>
          )}
          {averageRating && averageRating > 0 && (
            <div className="flex items-center gap-1">
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
              <span>{averageRating.toFixed(1)}</span>
            </div>
          )}
        </div>

        {tags && tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {tags.slice(0, 3).map((tag, idx) => (
              <span
                key={idx}
                className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full"
              >
                {tag}
              </span>
            ))}
            {tags.length > 3 && (
              <span className="text-xs text-gray-500 px-2 py-0.5">
                +{tags.length - 3} more
              </span>
            )}
          </div>
        )}

        {difficulty && (
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            {difficulty}
          </div>
        )}
      </CardContent>
    </Card>
  )

  if (id) {
    return <Link href={`/recipe/${id}`}>{content}</Link>
  }

  return content
}
