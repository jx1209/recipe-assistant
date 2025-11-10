/**
 * Enhanced recipe card component with beautiful animations and modern design
 */

import Link from 'next/link'
import { Clock, Users, Star, ChefHat, Sparkles } from 'lucide-react'
import { Card, CardContent } from './ui/Card'
import { Badge } from './ui/Badge'

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
  
  const getDifficultyVariant = (diff: string | null) => {
    if (!diff) return 'default'
    switch (diff.toLowerCase()) {
      case 'easy': return 'success'
      case 'medium': return 'warning'
      case 'hard': return 'danger'
      default: return 'default'
    }
  }
  
  const content = (
    <Card hover className="group h-full overflow-hidden bg-white animate-fade-in-up">
      {/* Image Section */}
      <div className="relative h-52 bg-gradient-to-br from-gray-200 to-gray-300 overflow-hidden">
        {imageUrl ? (
          <>
            <img 
              src={imageUrl} 
              alt={title}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </>
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <ChefHat className="h-16 w-16 text-gray-400 group-hover:scale-110 transition-transform duration-300" />
          </div>
        )}
        
        {/* Difficulty Badge - Top Right */}
        {difficulty && (
          <div className="absolute top-3 right-3">
            <Badge 
              variant={getDifficultyVariant(difficulty)} 
              size="sm" 
              rounded
              className="backdrop-blur-sm bg-white/90 font-semibold shadow-lg"
            >
              {difficulty}
            </Badge>
          </div>
        )}
        
        {/* Rating Badge - Top Left */}
        {averageRating && averageRating > 0 && (
          <div className="absolute top-3 left-3">
            <div className="flex items-center gap-1 px-2.5 py-1 bg-white/90 backdrop-blur-sm rounded-full shadow-lg">
              <Star className="h-3.5 w-3.5 fill-yellow-400 text-yellow-400" />
              <span className="text-sm font-semibold text-gray-900">{averageRating.toFixed(1)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Content Section */}
      <CardContent className="space-y-3.5">
        {/* Title & Description */}
        <div>
          <h3 className="text-lg font-bold text-gray-900 group-hover:text-primary-600 transition-colors duration-200 line-clamp-1">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-gray-600 mt-1.5 line-clamp-2 leading-relaxed">
              {description}
            </p>
          )}
        </div>

        {/* Meta Information */}
        <div className="flex items-center gap-4 text-sm text-gray-600 font-medium">
          {totalTime > 0 && (
            <div className="flex items-center gap-1.5 group/time">
              <Clock className="h-4 w-4 text-primary-500 group-hover/time:scale-110 transition-transform" />
              <span>{totalTime} min</span>
            </div>
          )}
          {servings && (
            <div className="flex items-center gap-1.5 group/servings">
              <Users className="h-4 w-4 text-primary-500 group-hover/servings:scale-110 transition-transform" />
              <span>{servings} {servings === 1 ? 'serving' : 'servings'}</span>
            </div>
          )}
        </div>

        {/* Tags */}
        {tags && tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {tags.slice(0, 3).map((tag, idx) => (
              <Badge
                key={idx}
                variant="primary"
                size="sm"
                rounded
                className="group-hover:scale-105 transition-transform"
              >
                {tag}
              </Badge>
            ))}
            {tags.length > 3 && (
              <Badge
                variant="default"
                size="sm"
                rounded
              >
                +{tags.length - 3}
              </Badge>
            )}
          </div>
        )}

        {/* Hover Action Hint */}
        <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center gap-2 text-primary-600 text-sm font-semibold pt-1">
          <Sparkles className="h-4 w-4" />
          <span>View Recipe</span>
        </div>
      </CardContent>
    </Card>
  )

  if (id) {
    return <Link href={`/recipe/${id}`} className="block h-full">{content}</Link>
  }

  return content
}
