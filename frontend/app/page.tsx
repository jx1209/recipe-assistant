'use client'

/**
 * home page with recipe recommendations
 */

import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { recipeApi, Recipe } from '@/lib/api'
import { RecipeCard } from '@/components/RecipeCard'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import Link from 'next/link'
import { ChefHat, Sparkles, Search, TrendingUp, Heart } from 'lucide-react'

export default function HomePage() {
  const { user, isAuthenticated } = useAuth()
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadRecommendations()
  }, [isAuthenticated])

  const loadRecommendations = async () => {
    try {
      setIsLoading(true)
      const data = await recipeApi.getRecipes({ limit: 6 })
      setRecipes(data)
    } catch (error) {
      console.error('failed to load recipes:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-primary-50">
      {/* hero section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <ChefHat className="h-16 w-16 text-primary-600" />
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
            welcome to <span className="text-primary-600">Recipe Assistant</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            AI-powered recipe management, meal planning, and smart cooking assistance all in one place
          </p>
          
          {!isAuthenticated ? (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/auth/register">
                <Button size="lg" className="w-full sm:w-auto">
                  get started free
                </Button>
              </Link>
              <Link href="/auth/login">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  sign in
                </Button>
              </Link>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/search">
                <Button size="lg" className="w-full sm:w-auto">
                  <Search className="h-5 w-5 mr-2" />
                  browse recipes
                </Button>
              </Link>
              <Link href="/ai">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  <Sparkles className="h-5 w-5 mr-2" />
                  AI features
                </Button>
              </Link>
            </div>
          )}
        </div>
      </section>

      {/* features section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card variant="elevated" className="text-center">
            <CardContent className="pt-6 space-y-3">
              <div className="flex justify-center">
                <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-primary-600" />
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-900">AI-powered</h3>
              <p className="text-gray-600">
                generate recipes, get cooking advice, and modify dishes with AI assistance
              </p>
            </CardContent>
          </Card>

          <Card variant="elevated" className="text-center">
            <CardContent className="pt-6 space-y-3">
              <div className="flex justify-center">
                <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-primary-600" />
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-900">meal planning</h3>
              <p className="text-gray-600">
                plan your weekly meals and generate shopping lists automatically
              </p>
            </CardContent>
          </Card>

          <Card variant="elevated" className="text-center">
            <CardContent className="pt-6 space-y-3">
              <div className="flex justify-center">
                <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <Heart className="h-6 w-6 text-primary-600" />
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-900">personalized</h3>
              <p className="text-gray-600">
                save favorites, track dietary preferences, and get custom recommendations
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* recipe recommendations */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900">
            {isAuthenticated ? 'recommended for you' : 'popular recipes'}
          </h2>
          <Link href="/search">
            <Button variant="outline">view all</Button>
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-80 bg-gray-200 animate-pulse rounded-xl" />
            ))}
          </div>
        ) : recipes.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {recipes.map((recipe) => (
              <RecipeCard
                key={recipe.id}
                id={recipe.id}
                title={recipe.title}
                description={recipe.description}
                tags={recipe.tags}
                prepTime={recipe.prep_time}
                cookTime={recipe.cook_time}
                servings={recipe.servings}
                averageRating={recipe.average_rating}
                imageUrl={recipe.image_url}
                difficulty={recipe.difficulty}
              />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <ChefHat className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">no recipes found. start by adding some recipes!</p>
              <Link href="/search">
                <Button className="mt-4">browse recipes</Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </section>

      {/* CTA section */}
      {!isAuthenticated && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <Card variant="elevated" className="bg-gradient-to-r from-primary-600 to-primary-700">
            <CardContent className="py-12 text-center">
              <h2 className="text-3xl font-bold text-white mb-4">
                ready to start cooking?
              </h2>
              <p className="text-primary-100 mb-8 max-w-2xl mx-auto">
                join thousands of home cooks who trust Recipe Assistant for meal planning and cooking inspiration
              </p>
              <Link href="/auth/register">
                <Button size="lg" className="bg-white text-primary-600 hover:bg-gray-100">
                  create free account
                </Button>
              </Link>
            </CardContent>
          </Card>
        </section>
      )}
    </div>
  )
}
