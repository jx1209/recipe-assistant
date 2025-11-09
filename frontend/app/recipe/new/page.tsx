'use client'

/**
 * create new recipe page
 */

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { recipeApi } from '@/lib/api'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RecipeForm } from '@/components/RecipeForm'
import { Button } from '@/components/ui/Button'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export default function NewRecipePage() {
  return (
    <ProtectedRoute>
      <NewRecipeContent />
    </ProtectedRoute>
  )
}

function NewRecipeContent() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (data: any) => {
    setIsLoading(true)
    try {
      const recipe = await recipeApi.createRecipe(data)
      toast.success('recipe created successfully!')
      router.push(`/recipe/${recipe.id}`)
    } catch (error: any) {
      console.error('failed to create recipe:', error)
      toast.error(error.response?.data?.detail || 'failed to create recipe')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* header */}
        <div className="mb-6">
          <Link href="/search">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              back to recipes
            </Button>
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">create new recipe</h1>
          <p className="text-gray-600 mt-2">add a new recipe to your collection</p>
        </div>

        {/* form */}
        <RecipeForm 
          onSubmit={handleSubmit} 
          submitLabel="create recipe"
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}

