'use client'

/**
 * edit recipe page
 */

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { recipeApi, Recipe } from '@/lib/api'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RecipeForm } from '@/components/RecipeForm'
import { Button } from '@/components/ui/Button'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export default function EditRecipePage() {
  return (
    <ProtectedRoute>
      <EditRecipeContent />
    </ProtectedRoute>
  )
}

function EditRecipeContent() {
  const params = useParams()
  const router = useRouter()
  const [recipe, setRecipe] = useState<Recipe | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(true)

  useEffect(() => {
    if (params.id) {
      loadRecipe(parseInt(params.id as string))
    }
  }, [params.id])

  const loadRecipe = async (id: number) => {
    try {
      setIsFetching(true)
      const data = await recipeApi.getRecipe(id)
      setRecipe(data)
    } catch (error) {
      console.error('failed to load recipe:', error)
      toast.error('failed to load recipe')
    } finally {
      setIsFetching(false)
    }
  }

  const handleSubmit = async (data: any) => {
    if (!recipe) return

    setIsLoading(true)
    try {
      await recipeApi.updateRecipe(recipe.id, data)
      toast.success('recipe updated successfully!')
      router.push(`/recipe/${recipe.id}`)
    } catch (error: any) {
      console.error('failed to update recipe:', error)
      toast.error(error.response?.data?.detail || 'failed to update recipe')
    } finally {
      setIsLoading(false)
    }
  }

  if (isFetching) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!recipe) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">recipe not found</h2>
          <Link href="/search">
            <Button>browse recipes</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* header */}
        <div className="mb-6">
          <Link href={`/recipe/${recipe.id}`}>
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              back to recipe
            </Button>
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">edit recipe</h1>
          <p className="text-gray-600 mt-2">update your recipe details</p>
        </div>

        {/* form */}
        <RecipeForm 
          initialData={{
            title: recipe.title,
            description: recipe.description || '',
            ingredients: recipe.ingredients,
            instructions: recipe.instructions,
            prep_time: recipe.prep_time,
            cook_time: recipe.cook_time,
            servings: recipe.servings,
            difficulty: recipe.difficulty || 'medium',
            cuisine: recipe.cuisine || '',
            meal_type: recipe.meal_type || '',
            tags: recipe.tags || [],
            image_url: recipe.image_url || '',
            source_url: recipe.source_url || '',
          }}
          onSubmit={handleSubmit} 
          submitLabel="update recipe"
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}

