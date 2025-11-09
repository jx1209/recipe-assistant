'use client'

/**
 * recipe search page with filters and sorting
 */

import { useState, useEffect } from 'react'
import { recipeApi, Recipe } from '@/lib/api'
import { RecipeCard } from '@/components/RecipeCard'
import { SearchBar } from '@/components/SearchBar'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import Link from 'next/link'
import { Filter, X, Plus, ChefHat } from 'lucide-react'

export default function SearchPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  
  // filters
  const [cuisine, setCuisine] = useState('')
  const [difficulty, setDifficulty] = useState('')
  const [mealType, setMealType] = useState('')
  const [maxPrepTime, setMaxPrepTime] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])

  useEffect(() => {
    loadRecipes()
  }, [searchQuery, cuisine, difficulty, mealType, maxPrepTime, selectedTags])

  const loadRecipes = async () => {
    try {
      setIsLoading(true)
      const params: any = {}
      
      if (searchQuery) params.query = searchQuery
      if (cuisine) params.cuisine = cuisine
      if (difficulty) params.difficulty = difficulty
      if (mealType) params.meal_type = mealType
      if (maxPrepTime) params.max_prep_time = parseInt(maxPrepTime)
      if (selectedTags.length > 0) params.tags = selectedTags

      const data = searchQuery 
        ? await recipeApi.searchRecipes(searchQuery, params)
        : await recipeApi.getRecipes(params)
      
      setRecipes(data)
    } catch (error) {
      console.error('failed to load recipes:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
  }

  const clearFilters = () => {
    setCuisine('')
    setDifficulty('')
    setMealType('')
    setMaxPrepTime('')
    setSelectedTags([])
  }

  const hasActiveFilters = cuisine || difficulty || mealType || maxPrepTime || selectedTags.length > 0

  const commonTags = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'quick', 'healthy', 'comfort-food']
  const cuisines = ['italian', 'mexican', 'asian', 'american', 'mediterranean', 'indian', 'french']
  const difficulties = ['easy', 'medium', 'hard']
  const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack', 'dessert']

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">discover recipes</h1>
              <p className="text-gray-600 mt-1">browse and search thousands of recipes</p>
            </div>
            <Link href="/recipe/new">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                add recipe
              </Button>
            </Link>
          </div>

          {/* search bar */}
          <div className="flex gap-2">
            <div className="flex-1">
              <SearchBar onSearch={handleSearch} />
            </div>
            <Button 
              variant={showFilters ? "primary" : "outline"}
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="h-4 w-4 mr-2" />
              filters
            </Button>
          </div>
        </div>

        {/* filters panel */}
        {showFilters && (
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">filters</h3>
                {hasActiveFilters && (
                  <Button variant="ghost" size="sm" onClick={clearFilters}>
                    <X className="h-4 w-4 mr-1" />
                    clear all
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* cuisine */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">cuisine</label>
                  <select
                    value={cuisine}
                    onChange={(e) => setCuisine(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">all cuisines</option>
                    {cuisines.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                {/* difficulty */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">difficulty</label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">all levels</option>
                    {difficulties.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>

                {/* meal type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">meal type</label>
                  <select
                    value={mealType}
                    onChange={(e) => setMealType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">all types</option>
                    {mealTypes.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>

                {/* prep time */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">max prep time (min)</label>
                  <input
                    type="number"
                    value={maxPrepTime}
                    onChange={(e) => setMaxPrepTime(e.target.value)}
                    placeholder="e.g. 30"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* tags */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">dietary tags</label>
                <div className="flex flex-wrap gap-2">
                  {commonTags.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => {
                        if (selectedTags.includes(tag)) {
                          setSelectedTags(selectedTags.filter(t => t !== tag))
                        } else {
                          setSelectedTags([...selectedTags, tag])
                        }
                      }}
                      className={`px-3 py-1 rounded-full text-sm transition ${
                        selectedTags.includes(tag)
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* results count */}
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            {isLoading ? 'searching...' : `found ${recipes.length} recipe${recipes.length !== 1 ? 's' : ''}`}
          </p>
        </div>

        {/* recipes grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-96 bg-gray-200 animate-pulse rounded-xl" />
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
            <CardContent className="py-16 text-center">
              <ChefHat className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">no recipes found</h3>
              <p className="text-gray-600 mb-6">
                {hasActiveFilters || searchQuery 
                  ? 'try adjusting your filters or search query'
                  : 'start by adding your first recipe!'
                }
              </p>
              {hasActiveFilters && (
                <Button variant="outline" onClick={clearFilters}>
                  clear filters
                </Button>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
