'use client'

import { useState, useEffect } from 'react'
import { recipeApi, Recipe, shoppingListApi } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { RecipeCard } from '@/components/RecipeCard'
import { useRouter } from 'next/navigation'
import { 
  Calendar, 
  Plus, 
  X, 
  Search, 
  ShoppingCart, 
  Coffee, 
  Sun, 
  Moon,
  Utensils,
  ChevronRight
} from 'lucide-react'
import toast from 'react-hot-toast'

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

const mealTypes = [
  { key: 'breakfast', label: 'Breakfast', icon: Coffee, color: 'orange' },
  { key: 'lunch', label: 'Lunch', icon: Sun, color: 'yellow' },
  { key: 'dinner', label: 'Dinner', icon: Moon, color: 'purple' },
]

type MealPlan = {
  [day: string]: {
    [mealType: string]: Recipe | null
  }
}

export default function PlannerPage() {
  const router = useRouter()
  const [mealPlan, setMealPlan] = useState<MealPlan>({})
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<Recipe[]>([])
  const [showSearch, setShowSearch] = useState(false)
  const [selectedSlot, setSelectedSlot] = useState<{ day: string; mealType: string } | null>(null)
  const [creatingList, setCreatingList] = useState(false)

  useEffect(() => {
    // Initialize meal plan
    const initialPlan: MealPlan = {}
    days.forEach((day) => {
      initialPlan[day] = {
        breakfast: null,
        lunch: null,
        dinner: null,
      }
    })
    setMealPlan(initialPlan)
  }, [])

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    
    try {
      const results = await recipeApi.searchRecipes(searchQuery)
      setSearchResults(results)
    } catch (error) {
      console.error('Failed to search recipes:', error)
      toast.error('Failed to search recipes')
    }
  }

  const selectRecipeForSlot = (recipe: Recipe) => {
    if (!selectedSlot) return

    setMealPlan((prev) => ({
      ...prev,
      [selectedSlot.day]: {
        ...prev[selectedSlot.day],
        [selectedSlot.mealType]: recipe,
      },
    }))

    setShowSearch(false)
    setSelectedSlot(null)
    setSearchQuery('')
    setSearchResults([])
    toast.success(`${recipe.title} added to ${selectedSlot.day} ${selectedSlot.mealType}`)
  }

  const removeRecipe = (day: string, mealType: string) => {
    setMealPlan((prev) => ({
      ...prev,
      [day]: {
        ...prev[day],
        [mealType]: null,
      },
    }))
    toast.success('Recipe removed')
  }

  const openSearchForSlot = (day: string, mealType: string) => {
    setSelectedSlot({ day, mealType })
    setShowSearch(true)
  }

  const generateShoppingList = async () => {
    // Collect all recipe IDs from the meal plan
    const recipeIds: number[] = []
    Object.values(mealPlan).forEach((dayMeals) => {
      Object.values(dayMeals).forEach((recipe) => {
        if (recipe && recipe.id) {
          recipeIds.push(recipe.id)
        }
      })
    })

    if (recipeIds.length === 0) {
      toast.error('Add some recipes to your meal plan first!')
      return
    }

    setCreatingList(true)
    try {
      const listName = `Weekly Meal Plan - ${new Date().toLocaleDateString()}`
      await shoppingListApi.createShoppingList({
        name: listName,
        recipe_ids: recipeIds,
        exclude_pantry: true,
        group_by_category: true,
      })
      
      toast.success('Shopping list created!')
      router.push('/shopping-list')
    } catch (error) {
      console.error('Failed to create shopping list:', error)
      toast.error('Failed to create shopping list')
    } finally {
      setCreatingList(false)
    }
  }

  const getMealTypeColor = (color: string) => {
    const colors = {
      orange: 'bg-orange-100 text-orange-700 border-orange-200',
      yellow: 'bg-yellow-100 text-yellow-700 border-yellow-200',
      purple: 'bg-purple-100 text-purple-700 border-purple-200',
    }
    return colors[color as keyof typeof colors] || colors.orange
  }

  const totalMeals = Object.values(mealPlan).reduce((sum, day) => {
    return sum + Object.values(day).filter((meal) => meal !== null).length
  }, 0)

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-orange-50/30 to-yellow-50/40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <div className="mb-8 animate-fade-in-up">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-2xl shadow-lg">
                <Calendar className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl md:text-5xl font-bold text-gray-900">
                  Weekly <span className="gradient-text">Meal Planner</span>
                </h1>
                <p className="text-lg text-gray-600 mt-1">Plan your meals and create shopping lists</p>
              </div>
            </div>
            <Button
              onClick={generateShoppingList}
              disabled={creatingList || totalMeals === 0}
              variant="gradient"
              size="lg"
              rounded="full"
              className="bg-gradient-to-r from-orange-600 to-yellow-600 hover:from-orange-700 hover:to-yellow-700 shadow-lg"
            >
              <ShoppingCart className="w-5 h-5 mr-2" />
              {creatingList ? 'Creating...' : `Generate Shopping List (${totalMeals} meals)`}
            </Button>
          </div>
        </div>

        {/* Meal Plan Grid */}
        <div className="space-y-6">
          {days.map((day, dayIndex) => (
            <Card
              key={day}
              className="overflow-hidden animate-fade-in-up"
              style={{ animationDelay: `${dayIndex * 0.05}s` }}
            >
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-primary rounded-full text-white font-bold">
                    {day[0]}
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900">{day}</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {mealTypes.map(({ key, label, icon: Icon, color }) => {
                    const recipe = mealPlan[day]?.[key]

                    return (
                      <div key={key} className="space-y-2">
                        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${getMealTypeColor(color)}`}>
                          <Icon className="w-4 h-4" />
                          <span className="font-semibold text-sm">{label}</span>
                        </div>

                        {recipe ? (
                          <div className="relative group">
                            <div className="aspect-video rounded-lg overflow-hidden bg-gradient-to-br from-gray-200 to-gray-300 relative">
                              {recipe.image_url ? (
                                <img
                                  src={recipe.image_url}
                                  alt={recipe.title}
                                  className="w-full h-full object-cover"
                                />
                              ) : (
                                <div className="w-full h-full flex items-center justify-center">
                                  <Utensils className="w-12 h-12 text-gray-400" />
                                </div>
                              )}
                              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-3">
                                <p className="text-white font-semibold text-sm line-clamp-2">
                                  {recipe.title}
                                </p>
                              </div>
                              <button
                                onClick={() => removeRecipe(day, key)}
                                className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        ) : (
                          <button
                            onClick={() => openSearchForSlot(day, key)}
                            className="w-full aspect-video rounded-lg border-2 border-dashed border-gray-300 hover:border-orange-500 hover:bg-orange-50 transition-all flex flex-col items-center justify-center gap-2 group text-gray-400 hover:text-orange-600"
                          >
                            <Plus className="w-8 h-8 group-hover:scale-110 transition-transform" />
                            <span className="text-sm font-medium">Add Recipe</span>
                          </button>
                        )}
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recipe Search Modal */}
        {showSearch && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
            <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">Select Recipe</h3>
                    <p className="text-gray-600 text-sm mt-1">
                      {selectedSlot?.day} - {mealTypes.find((m) => m.key === selectedSlot?.mealType)?.label}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setShowSearch(false)
                      setSelectedSlot(null)
                      setSearchQuery('')
                      setSearchResults([])
                    }}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="flex gap-3 mb-6">
                  <Input
                    type="text"
                    placeholder="Search recipes..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    className="flex-1 text-gray-900 placeholder:text-gray-400"
                  />
                  <Button onClick={handleSearch} variant="primary" className="bg-orange-600 hover:bg-orange-700">
                    <Search className="w-5 h-5 mr-2" />
                    Search
                  </Button>
                </div>

                <div className="overflow-y-auto max-h-[60vh]">
                  {searchResults.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {searchResults.map((recipe) => (
                        <button
                          key={recipe.id}
                          onClick={() => selectRecipeForSlot(recipe)}
                          className="text-left hover:scale-102 transition-transform"
                        >
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
                          />
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">
                        {searchQuery ? 'No recipes found. Try a different search.' : 'Search for recipes to add to your meal plan'}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Empty State */}
        {totalMeals === 0 && (
          <Card className="mt-8 animate-fade-in">
            <CardContent className="py-12 text-center">
              <Calendar className="w-20 h-20 text-gray-300 mx-auto mb-6" />
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Start Planning Your Week</h3>
              <p className="text-gray-600 mb-6">
                Click the <Plus className="w-4 h-4 inline" /> buttons above to add recipes to your meal plan
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
