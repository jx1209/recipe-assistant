'use client'

/**
 * home page
 */

import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { recipeApi, Recipe } from '@/lib/api'
import { RecipeCard } from '@/components/RecipeCard'
import { Button } from '@/components/ui/Button'
import { GridSkeleton } from '@/components/ui/Skeleton'
import Link from 'next/link'
import { ChefHat, Sparkles, Search, ArrowRight } from 'lucide-react'

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
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Hero Section - Clean Editorial Style */}
      <section className="border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          <div className="max-w-3xl">
            {/* Small Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary-50 dark:bg-primary-900/20 
                           rounded-full text-sm font-medium text-primary-700 dark:text-primary-300 mb-6">
              <ChefHat className="w-4 h-4" />
              <span>Professional Recipe Management</span>
            </div>

            {/* Headline */}
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-gray-100 mb-6 
                         tracking-tight leading-tight">
              Cook with confidence.{' '}
              <span className="text-primary-600 dark:text-primary-400">
                Save with ease.
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 leading-relaxed">
              Discover chef-tested recipes, plan your week, and generate smart shopping lists. 
              AI-powered assistance makes cooking simple and enjoyable.
            </p>

            {/* CTAs */}
            {!isAuthenticated ? (
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/auth/register">
                  <Button size="lg" variant="primary" className="w-full sm:w-auto font-semibold group">
                    Get Started
                    <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
                <Link href="/search">
                  <Button size="lg" variant="outline" className="w-full sm:w-auto font-semibold">
                    Browse Recipes
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/search">
                  <Button size="lg" variant="primary" className="w-full sm:w-auto font-semibold group">
                    Browse Recipes
                    <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
                <Link href="/ai">
                  <Button size="lg" variant="outline" className="w-full sm:w-auto font-semibold">
                    <Sparkles className="w-5 h-5 mr-2" />
                    AI Features
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Featured Recipes */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex items-end justify-between mb-8 border-b border-gray-200 dark:border-gray-800 pb-4">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 tracking-tight">
              Featured Recipes
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Handpicked by our culinary team
            </p>
          </div>
          <Link href="/search">
            <Button variant="ghost" size="sm" className="font-semibold group">
              View all
              <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
        </div>

        {isLoading ? (
          <GridSkeleton count={6} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {recipes.map((recipe) => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>
        )}
      </section>

      {/* Features Section */}
      <section className="bg-gray-50 dark:bg-gray-800/50 border-t border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-3 tracking-tight">
              Everything you need to cook better
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Professional tools for home cooks
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: Search,
                title: 'Smart Search',
                description: 'Find recipes by ingredients, cuisine, dietary needs, or cooking time.'
              },
              {
                icon: ChefHat,
                title: 'Meal Planning',
                description: 'Plan your entire week with drag-and-drop simplicity.'
              },
              {
                icon: Sparkles,
                title: 'AI Assistance',
                description: 'Get recipe suggestions, substitutions, and cooking tips powered by AI.'
              }
            ].map((feature, idx) => (
              <div key={idx} className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full 
                              bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 mb-4">
                  <feature.icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      {!isAuthenticated && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl p-12 text-center text-white">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to start cooking?
            </h2>
            <p className="text-xl text-primary-50 mb-8 max-w-2xl mx-auto">
              Join thousands of home cooks who are making better meals every day
            </p>
            <Link href="/auth/register">
              <Button size="lg" variant="outline" className="bg-white text-primary-600 hover:bg-gray-50 border-0 font-semibold">
                Create Free Account
              </Button>
            </Link>
          </div>
        </section>
      )}
    </div>
  )
}
