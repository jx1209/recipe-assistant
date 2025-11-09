'use client'

/**
 * recipe detail page
 */

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { recipeApi, Recipe } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import Link from 'next/link'
import { 
  Clock, 
  Users, 
  Star, 
  Heart, 
  Edit, 
  Trash2, 
  ChefHat,
  ArrowLeft,
  Share2
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function RecipeDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated } = useAuth()
  const [recipe, setRecipe] = useState<Recipe | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isFavorite, setIsFavorite] = useState(false)

  useEffect(() => {
    if (params.id) {
      loadRecipe(parseInt(params.id as string))
    }
  }, [params.id])

  const loadRecipe = async (id: number) => {
    try {
      setIsLoading(true)
      const data = await recipeApi.getRecipe(id)
      setRecipe(data)
      setIsFavorite(data.is_favorite)
    } catch (error) {
      console.error('failed to load recipe:', error)
      toast.error('failed to load recipe')
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleFavorite = async () => {
    if (!recipe || !isAuthenticated) return

    try {
      await recipeApi.toggleFavorite(recipe.id)
      setIsFavorite(!isFavorite)
      toast.success(isFavorite ? 'removed from favorites' : 'added to favorites')
    } catch (error) {
      toast.error('failed to update favorite')
    }
  }

  const handleDelete = async () => {
    if (!recipe || !confirm('are you sure you want to delete this recipe?')) return

    try {
      await recipeApi.deleteRecipe(recipe.id)
      toast.success('recipe deleted')
      router.push('/search')
    } catch (error) {
      toast.error('failed to delete recipe')
    }
  }

  const handleShare = () => {
    if (navigator.share && recipe) {
      navigator.share({
        title: recipe.title,
        text: recipe.description || '',
        url: window.location.href,
      })
    } else {
      navigator.clipboard.writeText(window.location.href)
      toast.success('link copied to clipboard!')
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!recipe) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card>
          <CardContent className="py-12 text-center">
            <ChefHat className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">recipe not found</h2>
            <p className="text-gray-600 mb-6">the recipe you're looking for doesn't exist</p>
            <Link href="/search">
              <Button>browse recipes</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const totalTime = (recipe.prep_time || 0) + (recipe.cook_time || 0)

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* back button */}
        <Link href="/search">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            back to recipes
          </Button>
        </Link>

        {/* recipe header */}
        <Card variant="elevated" className="mb-6">
          {recipe.image_url && (
            <div className="h-96 bg-gray-200 rounded-t-xl overflow-hidden">
              <img 
                src={recipe.image_url} 
                alt={recipe.title}
                className="w-full h-full object-cover"
              />
            </div>
          )}
          
          <CardContent className="pt-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">{recipe.title}</h1>
                {recipe.description && (
                  <p className="text-lg text-gray-600">{recipe.description}</p>
                )}
              </div>

              <div className="flex gap-2 ml-4">
                {isAuthenticated && (
                  <>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={handleToggleFavorite}
                      className={isFavorite ? 'text-red-600 border-red-600' : ''}
                    >
                      <Heart className={`h-4 w-4 ${isFavorite ? 'fill-current' : ''}`} />
                    </Button>
                    <Link href={`/recipe/${recipe.id}/edit`}>
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Button variant="outline" size="sm" onClick={handleDelete}>
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </Button>
                  </>
                )}
                <Button variant="outline" size="sm" onClick={handleShare}>
                  <Share2 className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* meta info */}
            <div className="flex flex-wrap gap-6 text-gray-600 mb-4">
              {totalTime > 0 && (
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  <span>{totalTime} min total</span>
                  {recipe.prep_time && <span className="text-sm">({recipe.prep_time} prep)</span>}
                </div>
              )}
              {recipe.servings && (
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  <span>{recipe.servings} servings</span>
                </div>
              )}
              {recipe.average_rating && recipe.average_rating > 0 && (
                <div className="flex items-center gap-2">
                  <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                  <span>{recipe.average_rating.toFixed(1)} ({recipe.total_ratings} ratings)</span>
                </div>
              )}
            </div>

            {/* tags */}
            {recipe.tags && recipe.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {recipe.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* additional info */}
            <div className="flex flex-wrap gap-4 text-sm text-gray-600">
              {recipe.difficulty && (
                <span className="font-medium">difficulty: <span className="text-gray-900">{recipe.difficulty}</span></span>
              )}
              {recipe.cuisine && (
                <span className="font-medium">cuisine: <span className="text-gray-900">{recipe.cuisine}</span></span>
              )}
              {recipe.meal_type && (
                <span className="font-medium">meal type: <span className="text-gray-900">{recipe.meal_type}</span></span>
              )}
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* ingredients */}
          <div className="lg:col-span-1">
            <Card variant="elevated">
              <CardHeader>
                <h2 className="text-2xl font-bold text-gray-900">ingredients</h2>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {recipe.ingredients.map((ingredient, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="inline-block w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0" />
                      <span className="text-gray-900">
                        {ingredient.amount && ingredient.unit && (
                          <span className="font-medium">{ingredient.amount} {ingredient.unit} </span>
                        )}
                        {ingredient.name}
                        {ingredient.notes && (
                          <span className="text-gray-600 text-sm"> ({ingredient.notes})</span>
                        )}
                      </span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* instructions */}
          <div className="lg:col-span-2">
            <Card variant="elevated">
              <CardHeader>
                <h2 className="text-2xl font-bold text-gray-900">instructions</h2>
              </CardHeader>
              <CardContent>
                <ol className="space-y-4">
                  {recipe.instructions.map((instruction, idx) => (
                    <li key={idx} className="flex gap-4">
                      <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                        {idx + 1}
                      </span>
                      <p className="text-gray-900 pt-1">{instruction}</p>
                    </li>
                  ))}
                </ol>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* source */}
        {recipe.source_url && (
          <Card className="mt-6">
            <CardContent className="py-4">
              <p className="text-sm text-gray-600">
                source: <a href={recipe.source_url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                  {recipe.source_url}
                </a>
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
