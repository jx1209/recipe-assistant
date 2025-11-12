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
import { ChefHat, Sparkles, Search, TrendingUp, Heart, Star } from 'lucide-react'

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
    <div className="min-h-screen bg-gradient-to-br from-white via-primary-50/30 to-secondary-50/20">
      {/* Hero Section */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
        {/* Background Decorations */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 right-10 w-72 h-72 bg-primary-200/30 rounded-full blur-3xl animate-pulse-soft" />
          <div className="absolute bottom-20 left-10 w-96 h-96 bg-secondary-200/20 rounded-full blur-3xl animate-pulse-soft animation-delay-400" />
        </div>

        <div className="relative text-center">
          {/* Icon with Animation */}
          <div className="flex justify-center mb-8 animate-fade-in">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-primary rounded-2xl blur-xl opacity-50 animate-pulse-soft" />
              <div className="relative p-5 bg-gradient-primary rounded-2xl shadow-elevation-3">
                <ChefHat className="h-14 w-14 text-white animate-float" />
              </div>
            </div>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 animate-fade-in-up tracking-tight">
            Welcome to{' '}
            <span className="gradient-text animate-fade-in-up animation-delay-200">
              Recipe Assistant
            </span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed animate-fade-in-up animation-delay-400">
            AI-powered recipe management, intelligent meal planning, and smart cooking assistance—all in one beautiful platform
          </p>
          
          {/* CTAs */}
          {!isAuthenticated ? (
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up animation-delay-600">
              <Link href="/auth/register">
                <Button size="xl" variant="gradient" rounded="full" className="w-full sm:w-auto shadow-elevation-3 hover:shadow-elevation-4">
                  <Sparkles className="h-5 w-5 mr-2" />
                  Get Started Free
                </Button>
              </Link>
              <Link href="/auth/login">
                <Button size="xl" variant="outline" rounded="full" className="w-full sm:w-auto">
                  Sign In
                </Button>
              </Link>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up animation-delay-600">
              <Link href="/search">
                <Button size="xl" variant="gradient" rounded="full" className="w-full sm:w-auto">
                  <Search className="h-5 w-5 mr-2" />
                  Browse Recipes
                </Button>
              </Link>
              <Link href="/ai">
                <Button size="xl" variant="outline" rounded="full" className="w-full sm:w-auto">
                  <Sparkles className="h-5 w-5 mr-2" />
                  Try AI Features
                </Button>
              </Link>
            </div>
          )}

          {/* Social Proof */}
          <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-8 text-gray-600 animate-fade-in animation-delay-600">
            <div className="flex items-center gap-2">
              <div className="flex -space-x-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="w-8 h-8 rounded-full bg-gradient-primary border-2 border-white" />
                ))}
              </div>
              <span className="text-sm font-medium">1,000+ home cooks</span>
            </div>
            <div className="hidden sm:block w-px h-4 bg-gray-300" />
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
              <span className="text-sm font-medium">5,000+ recipes shared</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Everything You Need
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Powerful features to transform your cooking experience
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card hover variant="elevated" className="text-center group animate-fade-in-up">
            <CardContent className="pt-8 pb-8 space-y-4">
              <div className="flex justify-center">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-secondary rounded-2xl blur-xl opacity-30 group-hover:opacity-50 transition-opacity" />
                  <div className="relative h-16 w-16 bg-gradient-secondary rounded-2xl flex items-center justify-center transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg">
                    <Sparkles className="h-8 w-8 text-white" />
                  </div>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                AI-Powered
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Generate recipes, get cooking advice, and modify dishes with cutting-edge AI assistance
              </p>
            </CardContent>
          </Card>

          <Card hover variant="elevated" className="text-center group animate-fade-in-up animation-delay-200">
            <CardContent className="pt-8 pb-8 space-y-4">
              <div className="flex justify-center">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-primary rounded-2xl blur-xl opacity-30 group-hover:opacity-50 transition-opacity" />
                  <div className="relative h-16 w-16 bg-gradient-primary rounded-2xl flex items-center justify-center transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg">
                    <TrendingUp className="h-8 w-8 text-white" />
                  </div>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                Meal Planning
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Plan your weekly meals effortlessly and generate shopping lists automatically
              </p>
            </CardContent>
          </Card>

          <Card hover variant="elevated" className="text-center group animate-fade-in-up animation-delay-400">
            <CardContent className="pt-8 pb-8 space-y-4">
              <div className="flex justify-center">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-sunset rounded-2xl blur-xl opacity-30 group-hover:opacity-50 transition-opacity" />
                  <div className="relative h-16 w-16 bg-gradient-sunset rounded-2xl flex items-center justify-center transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg">
                    <Heart className="h-8 w-8 text-white" />
                  </div>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                Personalized
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Save favorites, track dietary preferences, and get custom recommendations
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Recipe Recommendations */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 bg-gradient-to-b from-transparent to-gray-50/50">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-12 gap-4">
          <div>
            <h2 className="text-4xl font-bold text-gray-900 mb-2">
              {isAuthenticated ? 'Recommended for You' : 'Popular Recipes'}
            </h2>
            <p className="text-gray-600">
              {isAuthenticated 
                ? 'Handpicked recipes based on your preferences' 
                : 'Discover our community\'s favorite dishes'
              }
            </p>
          </div>
          <Link href="/search">
            <Button variant="outline" size="lg">
              View All Recipes
            </Button>
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-[420px] shimmer-bg rounded-xl" />
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
          <Card variant="elevated" padding="lg">
            <CardContent className="py-16 text-center">
              <ChefHat className="h-20 w-20 text-gray-400 mx-auto mb-6 animate-bounce-soft" />
              <h3 className="text-2xl font-bold text-gray-900 mb-2">No Recipes Yet</h3>
              <p className="text-gray-600 mb-6">Start your culinary journey by adding your first recipe!</p>
              <Link href="/search">
                <Button variant="gradient" size="lg" rounded="full">
                  <Search className="h-5 w-5 mr-2" />
                  Browse Recipes
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </section>

      {/* CTA Section */}
      {!isAuthenticated && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <Card variant="elevated" className="relative overflow-hidden">
            {/* Background Gradient */}
            <div className="absolute inset-0 bg-gradient-ocean" />
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-10 right-10 w-40 h-40 bg-white rounded-full blur-3xl" />
              <div className="absolute bottom-10 left-10 w-56 h-56 bg-white rounded-full blur-3xl" />
            </div>

            <CardContent className="relative py-16 px-8 text-center">
              <Sparkles className="h-12 w-12 text-white mx-auto mb-6 animate-float" />
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                Ready to Start Cooking?
              </h2>
              <p className="text-xl text-white/90 mb-10 max-w-2xl mx-auto leading-relaxed">
                Join thousands of home cooks who trust Recipe Assistant for meal planning and cooking inspiration
              </p>
              <Link href="/auth/register">
                <Button 
                  size="xl" 
                  rounded="full"
                  className="bg-white text-primary-600 hover:bg-gray-50 shadow-elevation-3 hover:shadow-elevation-4"
                >
                  Create Free Account
                </Button>
              </Link>
              
              {/* Trust Indicators */}
              <div className="mt-10 flex flex-wrap items-center justify-center gap-6 text-white/80">
                <div className="flex items-center gap-2">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                  </svg>
                  <span className="text-sm font-medium">Free Forever</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                  </svg>
                  <span className="text-sm font-medium">No Credit Card Required</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                  </svg>
                  <span className="text-sm font-medium">Get Started in 30 Seconds</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
      )}
    </div>
  )
}
