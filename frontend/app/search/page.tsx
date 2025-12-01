'use client'

import { useState, useEffect } from 'react'
import { recipeApi, Recipe, shoppingListApi } from '@/lib/api'
import { RecipeCard } from '@/components/RecipeCard'
import { SearchBar } from '@/components/SearchBar'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Filter, X, Plus, ChefHat, ShoppingCart, Check } from 'lucide-react'
import toast from 'react-hot-toast'

export default function SearchPage() {
  const router = useRouter()
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedRecipes, setSelectedRecipes] = useState<Set<number>>(new Set())
  const [creatingList, setCreatingList] = useState(false)
  
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

  const toggleRecipeSelection = (recipeId: number) => {
    const newSelection = new Set(selectedRecipes)
    if (newSelection.has(recipeId)) {
      newSelection.delete(recipeId)
    } else {
      newSelection.add(recipeId)
    }
    setSelectedRecipes(newSelection)
  }

  const createShoppingList = async () => {
    if (selectedRecipes.size === 0) {
      toast.error('Please select at least one recipe')
      return
    }

    setCreatingList(true)
    try {
      const listName = `Shopping List - ${new Date().toLocaleDateString()}`
      const shoppingList = await shoppingListApi.createShoppingList({
        name: listName,
        recipe_ids: Array.from(selectedRecipes),
        exclude_pantry: true,
        group_by_category: true,
      })
      
      toast.success('Shopping list created successfully!')
      router.push('/shopping-list')
    } catch (error) {
      console.error('Failed to create shopping list:', error)
      toast.error('Failed to create shopping list')
    } finally {
      setCreatingList(false)
    }
  }

  const hasActiveFilters = cuisine || difficulty || mealType || maxPrepTime || selectedTags.length > 0

  const commonTags = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'quick', 'healthy', 'comfort-food']
  const cuisines = ['italian', 'mexican', 'asian', 'american', 'mediterranean', 'indian', 'french']
  const difficulties = ['easy', 'medium', 'hard']
  const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack', 'dessert']

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-primary-50/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <div className="mb-10 animate-fade-in-up">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-6">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-2">
                Discover <span className="gradient-text">Recipes</span>
              </h1>
              <p className="text-lg text-gray-600">Browse and search thousands of delicious recipes</p>
            </div>
            <div className="flex gap-3">
              <Link href="/recipe/new">
                <Button variant="gradient" size="lg" rounded="full" className="shadow-elevation-2">
                  <Plus className="h-5 w-5 mr-2" />
                  Add Recipe
                </Button>
              </Link>
              <Button 
                variant={selectedRecipes.size > 0 ? "primary" : "outline"} 
                size="lg" 
                rounded="full"
                onClick={() => {
                  if (selectedRecipes.size > 0) {
                    setSelectedRecipes(new Set())
                  }
                }}
                className={selectedRecipes.size > 0 ? "bg-orange-600 hover:bg-orange-700" : ""}
              >
                <ShoppingCart className="h-5 w-5 mr-2" />
                {selectedRecipes.size > 0 ? `${selectedRecipes.size} Selected` : 'Select Mode'}
              </Button>
            </div>
          </div>

          {/* Search Bar with Filter Button */}
          <div className="flex gap-3">
            <div className="flex-1">
              <SearchBar onSearch={handleSearch} />
            </div>
            <Button 
              variant={showFilters ? "primary" : "outline"}
              size="lg"
              onClick={() => setShowFilters(!showFilters)}
              className="transition-all duration-300"
            >
              <Filter className="h-5 w-5 mr-2" />
              {showFilters ? 'Hide' : 'Show'} Filters
              {hasActiveFilters && (
                <span className="ml-2 px-2 py-0.5 bg-white text-primary-600 rounded-full text-xs font-bold">
                  {[cuisine, difficulty, mealType, maxPrepTime, ...selectedTags].filter(Boolean).length}
                </span>
              )}
            </Button>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <Card variant="elevated" className="mb-8 animate-fade-in-down">
            <CardContent className="pt-6 pb-6">
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                  <Filter className="h-5 w-5 text-primary-600" />
                  <h3 className="text-xl font-bold text-gray-900">Filters</h3>
                </div>
                {hasActiveFilters && (
                  <Button variant="ghost" size="sm" onClick={clearFilters} className="group">
                    <X className="h-4 w-4 mr-1.5 group-hover:rotate-90 transition-transform" />
                    Clear All
                  </Button>
                )}
              </div>

              {/* Filter Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                {/* Cuisine */}
                <div className="space-y-2">
                  <label className="block text-sm font-bold text-gray-700">Cuisine</label>
                  <select
                    value={cuisine}
                    onChange={(e) => setCuisine(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all bg-white"
                  >
                    <option value="">All Cuisines</option>
                    {cuisines.map((c) => (
                      <option key={c} value={c} className="capitalize">{c}</option>
                    ))}
                  </select>
                </div>

                {/* Difficulty */}
                <div className="space-y-2">
                  <label className="block text-sm font-bold text-gray-700">Difficulty</label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all bg-white"
                  >
                    <option value="">All Levels</option>
                    {difficulties.map((d) => (
                      <option key={d} value={d} className="capitalize">{d}</option>
                    ))}
                  </select>
                </div>

                {/* Meal Type */}
                <div className="space-y-2">
                  <label className="block text-sm font-bold text-gray-700">Meal Type</label>
                  <select
                    value={mealType}
                    onChange={(e) => setMealType(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all bg-white"
                  >
                    <option value="">All Types</option>
                    {mealTypes.map((m) => (
                      <option key={m} value={m} className="capitalize">{m}</option>
                    ))}
                  </select>
                </div>

                {/* Prep Time */}
                <div className="space-y-2">
                  <label className="block text-sm font-bold text-gray-700">Max Prep Time (min)</label>
                  <input
                    type="number"
                    value={maxPrepTime}
                    onChange={(e) => setMaxPrepTime(e.target.value)}
                    placeholder="e.g. 30"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all text-gray-900 bg-white"
                  />
                </div>
              </div>

              {/* Dietary Tags */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <label className="block text-sm font-bold text-gray-700 mb-3">Dietary Tags</label>
                <div className="flex flex-wrap gap-2.5">
                  {commonTags.map((tag) => {
                    const isSelected = selectedTags.includes(tag)
                    return (
                      <button
                        key={tag}
                        onClick={() => {
                          if (isSelected) {
                            setSelectedTags(selectedTags.filter(t => t !== tag))
                          } else {
                            setSelectedTags([...selectedTags, tag])
                          }
                        }}
                        className={`
                          px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 transform hover:scale-105
                          ${isSelected
                            ? 'bg-gradient-primary text-white shadow-lg shadow-primary-500/30'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }
                        `}
                      >
                        {isSelected && <span className="mr-1">✓</span>}
                        {tag}
                      </button>
                    )
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Count & Sort */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <div className="flex items-center gap-3">
            {!isLoading && (
              <>
                <div className="h-10 w-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <span className="text-lg font-bold text-primary-600">{recipes.length}</span>
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">
                    {recipes.length} Recipe{recipes.length !== 1 ? 's' : ''} Found
                  </p>
                  <p className="text-xs text-gray-500">
                    {searchQuery ? `Matching "${searchQuery}"` : 'All recipes'}
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Recipes Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-[420px] shimmer-bg rounded-xl" />
            ))}
          </div>
        ) : recipes.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 pb-24">
              {recipes.map((recipe, index) => (
                <div key={recipe.id} className="animate-fade-in-up" style={{ animationDelay: `${index * 0.05}s` }}>
                  <RecipeCard
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
                    selectable={selectedRecipes.size > 0}
                    selected={selectedRecipes.has(recipe.id)}
                    onSelect={toggleRecipeSelection}
                    external={recipe.external}
                    sourceName={recipe.source_name}
                  />
                </div>
              ))}
            </div>

            {/* Floating Action Button */}
            {selectedRecipes.size > 0 && (
              <div className="fixed bottom-8 right-8 z-50 animate-fade-in-up">
                <Card className="bg-white shadow-2xl">
                  <CardContent className="p-4 flex items-center gap-4">
                    <div className="text-sm">
                      <p className="font-bold text-gray-900">{selectedRecipes.size} Recipe{selectedRecipes.size !== 1 ? 's' : ''} Selected</p>
                      <p className="text-gray-500 text-xs">Ready to create shopping list</p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedRecipes(new Set())}
                        className="border-gray-300"
                      >
                        Clear
                      </Button>
                      <Button
                        variant="gradient"
                        size="sm"
                        onClick={createShoppingList}
                        disabled={creatingList}
                        className="bg-orange-600 hover:bg-orange-700 shadow-lg"
                      >
                        <ShoppingCart className="h-4 w-4 mr-2" />
                        {creatingList ? 'Creating...' : 'Create List'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </>
        ) : (
          <Card variant="elevated" className="animate-fade-in">
            <CardContent className="py-20 text-center">
              <div className="max-w-md mx-auto">
                <ChefHat className="h-20 w-20 text-gray-300 mx-auto mb-6 animate-bounce-soft" />
                <h3 className="text-2xl font-bold text-gray-900 mb-3">No Recipes Found</h3>
                <p className="text-gray-600 mb-8 leading-relaxed">
                  {hasActiveFilters || searchQuery 
                    ? 'Try adjusting your filters or search query to discover more delicious recipes'
                    : 'Start your culinary journey by adding your first recipe!'
                  }
                </p>
                {hasActiveFilters ? (
                  <Button variant="gradient" size="lg" rounded="full" onClick={clearFilters}>
                    <X className="h-5 w-5 mr-2" />
                    Clear All Filters
                  </Button>
                ) : (
                  <Link href="/recipe/new">
                    <Button variant="gradient" size="lg" rounded="full">
                      <Plus className="h-5 w-5 mr-2" />
                      Add Your First Recipe
                    </Button>
                  </Link>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
