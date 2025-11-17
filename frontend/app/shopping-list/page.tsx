'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { shoppingListApi, recipeApi, ShoppingList, Recipe, ShoppingItem } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import toast from 'react-hot-toast'
import { Check, ShoppingCart, Plus, Trash2, ChevronRight } from 'lucide-react'

export default function ShoppingListPage() {
  const router = useRouter()
  const [shoppingLists, setShoppingLists] = useState<ShoppingList[]>([])
  const [selectedList, setSelectedList] = useState<ShoppingList | null>(null)
  const [recipes, setRecipes] = useState<Map<number, Recipe>>(new Map())
  const [selectedRecipeTab, setSelectedRecipeTab] = useState<number | 'all'>('all')
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    loadShoppingLists()
  }, [])

  useEffect(() => {
    if (selectedList && selectedList.recipe_ids.length > 0) {
      loadRecipes(selectedList.recipe_ids)
      setSelectedRecipeTab('all')
    }
  }, [selectedList])

  const loadShoppingLists = async () => {
    try {
      setLoading(true)
      const lists = await shoppingListApi.getShoppingLists()
      setShoppingLists(lists as any)
      
      // Auto-select the first list
      if (lists.length > 0) {
        const fullList = await shoppingListApi.getShoppingList(lists[0].id)
        setSelectedList(fullList)
      }
    } catch (error) {
      console.error('Failed to load shopping lists:', error)
      toast.error('Failed to load shopping lists')
    } finally {
      setLoading(false)
    }
  }

  const loadRecipes = async (recipeIds: number[]) => {
    try {
      const recipeMap = new Map<number, Recipe>()
      await Promise.all(
        recipeIds.map(async (id) => {
          try {
            const recipe = await recipeApi.getRecipe(id)
            recipeMap.set(id, recipe)
          } catch (err) {
            console.error(`Failed to load recipe ${id}:`, err)
          }
        })
      )
      setRecipes(recipeMap)
    } catch (error) {
      console.error('Failed to load recipes:', error)
    }
  }

  const handleCheckItem = async (itemIndex: number) => {
    if (!selectedList) return

    setUpdating(true)
    try {
      const updatedItems = [...selectedList.items]
      updatedItems[itemIndex] = {
        ...updatedItems[itemIndex],
        checked: !updatedItems[itemIndex].checked,
      }

      const updated = await shoppingListApi.updateShoppingList(selectedList.id, {
        items: updatedItems,
      })

      setSelectedList(updated)
      
      // Update in the list view as well
      setShoppingLists((prev) =>
        prev.map((list) => (list.id === updated.id ? updated : list))
      )
    } catch (error) {
      console.error('Failed to update item:', error)
      toast.error('Failed to update item')
    } finally {
      setUpdating(false)
    }
  }

  const handleDeleteList = async (listId: number) => {
    if (!confirm('Are you sure you want to delete this shopping list?')) return

    try {
      await shoppingListApi.deleteShoppingList(listId)
      toast.success('Shopping list deleted')
      setShoppingLists((prev) => prev.filter((list) => list.id !== listId))
      
      if (selectedList?.id === listId) {
        setSelectedList(null)
        setSelectedRecipeTab('all')
      }
    } catch (error) {
      console.error('Failed to delete list:', error)
      toast.error('Failed to delete shopping list')
    }
  }

  const getFilteredItems = (): ShoppingItem[] => {
    if (!selectedList) return []
    
    if (selectedRecipeTab === 'all') {
      return selectedList.items
    }
    
    return selectedList.items.filter((item) => item.recipe_id === selectedRecipeTab)
  }

  const formatQuantity = (item: ShoppingItem): string => {
    if (!item.quantity) return ''
    const qty = item.quantity.toString()
    const unit = item.unit || ''
    return `${qty} ${unit}`.trim()
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-yellow-50 p-6">
        <div className="max-w-6xl mx-auto">
          <Skeleton className="h-12 w-64 mb-8" />
          <div className="grid gap-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-yellow-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <ShoppingCart className="w-8 h-8 text-orange-600" />
            <h1 className="text-4xl font-bold text-gray-900">Shopping Lists</h1>
          </div>
          <Button
            onClick={() => router.push('/planner')}
            className="bg-orange-600 hover:bg-orange-700 text-white"
          >
            <Plus className="w-5 h-5 mr-2" />
            New List
          </Button>
        </div>

        {shoppingLists.length === 0 ? (
          <Card className="p-12 text-center">
            <ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">No Shopping Lists Yet</h2>
            <p className="text-gray-500 mb-6">
              Create your first shopping list from your saved recipes or meal plan
            </p>
            <Button
              onClick={() => router.push('/planner')}
              className="bg-orange-600 hover:bg-orange-700 text-white"
            >
              Get Started
            </Button>
          </Card>
        ) : (
          <div className="grid lg:grid-cols-3 gap-6">
            {/* List Sidebar */}
            <div className="lg:col-span-1 space-y-4">
              <h2 className="text-lg font-semibold text-gray-700 px-2">Your Lists</h2>
              {shoppingLists.map((list) => (
                <Card
                  key={list.id}
                  onClick={() => {
                    shoppingListApi.getShoppingList(list.id).then(setSelectedList)
                    setSelectedRecipeTab('all')
                  }}
                  className={`p-4 cursor-pointer transition-all hover:shadow-lg ${
                    selectedList?.id === list.id
                      ? 'ring-2 ring-orange-500 bg-orange-50'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{list.name}</h3>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteList(list.id)
                      }}
                      className="text-red-500 hover:text-red-700 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Check className="w-4 h-4 text-green-600" />
                      <span>
                        {list.checked_items} / {list.total_items}
                      </span>
                    </div>
                    <span>•</span>
                    <span className="text-gray-500">
                      {new Date(list.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {selectedList?.id === list.id && (
                    <ChevronRight className="w-5 h-5 text-orange-500 mt-2" />
                  )}
                </Card>
              ))}
            </div>

            {/* Main Content */}
            {selectedList && (
              <div className="lg:col-span-2 space-y-6">
                {/* Recipe Cards */}
                {selectedList.recipe_ids.length > 0 && (
                  <div>
                    <h2 className="text-lg font-semibold text-gray-700 mb-4">Recipes</h2>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
                      {selectedList.recipe_ids.map((recipeId) => {
                        const recipe = recipes.get(recipeId)
                        if (!recipe) return null

                        return (
                          <button
                            key={recipeId}
                            onClick={() => setSelectedRecipeTab(recipeId)}
                            className={`relative overflow-hidden rounded-lg transition-all ${
                              selectedRecipeTab === recipeId
                                ? 'ring-4 ring-orange-500 shadow-lg scale-105'
                                : 'hover:shadow-md hover:scale-102'
                            }`}
                          >
                            <div className="aspect-square">
                              {recipe.image_url ? (
                                <img
                                  src={recipe.image_url}
                                  alt={recipe.title}
                                  className="w-full h-full object-cover"
                                />
                              ) : (
                                <div className="w-full h-full bg-gradient-to-br from-orange-200 to-yellow-200 flex items-center justify-center">
                                  <span className="text-4xl">🍽️</span>
                                </div>
                              )}
                            </div>
                            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3">
                              <p className="text-white text-sm font-semibold line-clamp-2">
                                {recipe.title}
                              </p>
                            </div>
                            {selectedRecipeTab === recipeId && (
                              <div className="absolute top-2 right-2 bg-orange-500 rounded-full p-1">
                                <Check className="w-4 h-4 text-white" />
                              </div>
                            )}
                          </button>
                        )
                      })}
                    </div>

                    {/* Tab Buttons */}
                    <div className="flex flex-wrap gap-2 mb-6">
                      <button
                        onClick={() => setSelectedRecipeTab('all')}
                        className={`px-4 py-2 rounded-lg font-medium transition-all ${
                          selectedRecipeTab === 'all'
                            ? 'bg-orange-600 text-white shadow-md'
                            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                        }`}
                      >
                        All Items ({selectedList.items.length})
                      </button>
                      {selectedList.recipe_ids.map((recipeId) => {
                        const recipe = recipes.get(recipeId)
                        const itemCount = selectedList.items.filter(
                          (item) => item.recipe_id === recipeId
                        ).length

                        return (
                          <button
                            key={recipeId}
                            onClick={() => setSelectedRecipeTab(recipeId)}
                            className={`px-4 py-2 rounded-lg font-medium transition-all ${
                              selectedRecipeTab === recipeId
                                ? 'bg-orange-600 text-white shadow-md'
                                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                            }`}
                          >
                            {recipe?.title || `Recipe ${recipeId}`} ({itemCount})
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}

                {/* Shopping List Items - Receipt Style */}
                <Card className="p-6 bg-white shadow-lg">
                  <div className="border-b-2 border-dashed border-gray-300 pb-4 mb-6">
                    <h2 className="text-2xl font-bold text-center text-gray-900">
                      {selectedRecipeTab === 'all'
                        ? selectedList.name
                        : recipes.get(selectedRecipeTab as number)?.title || 'Shopping List'}
                    </h2>
                    <p className="text-center text-gray-500 text-sm mt-1">
                      {new Date(selectedList.created_at).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </p>
                  </div>

                  <div className="space-y-3">
                    {getFilteredItems().length === 0 ? (
                      <p className="text-center text-gray-500 py-8">No items in this list</p>
                    ) : (
                      getFilteredItems().map((item, index) => {
                        const actualIndex = selectedList.items.findIndex(
                          (i) =>
                            i.ingredient === item.ingredient &&
                            i.recipe_id === item.recipe_id
                        )

                        return (
                          <div
                            key={actualIndex}
                            className={`flex items-start gap-3 p-3 rounded-lg transition-all ${
                              item.checked
                                ? 'bg-green-50 border border-green-200'
                                : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'
                            }`}
                          >
                            <button
                              onClick={() => handleCheckItem(actualIndex)}
                              disabled={updating}
                              className={`flex-shrink-0 w-6 h-6 rounded border-2 transition-all mt-0.5 ${
                                item.checked
                                  ? 'bg-green-500 border-green-500'
                                  : 'border-gray-300 hover:border-orange-500'
                              }`}
                            >
                              {item.checked && <Check className="w-5 h-5 text-white" />}
                            </button>

                            <div className="flex-1 min-w-0">
                              <div className="flex items-baseline justify-between gap-2">
                                <span
                                  className={`font-medium capitalize ${
                                    item.checked
                                      ? 'text-gray-500 line-through'
                                      : 'text-gray-900'
                                  }`}
                                >
                                  {item.ingredient}
                                </span>
                                <span
                                  className={`text-sm font-mono flex-shrink-0 ${
                                    item.checked ? 'text-gray-400' : 'text-gray-700'
                                  }`}
                                >
                                  {formatQuantity(item)}
                                </span>
                              </div>
                              {item.notes && (
                                <p className="text-sm text-gray-500 mt-1">{item.notes}</p>
                              )}
                              {item.category && (
                                <span className="inline-block mt-1 text-xs px-2 py-0.5 bg-orange-100 text-orange-700 rounded-full">
                                  {item.category}
                                </span>
                              )}
                            </div>
                          </div>
                        )
                      })
                    )}
                  </div>

                  {/* Receipt Footer */}
                  <div className="border-t-2 border-dashed border-gray-300 mt-6 pt-4">
                    <div className="flex justify-between items-center text-sm font-mono">
                      <span className="text-gray-600">TOTAL ITEMS:</span>
                      <span className="font-bold text-gray-900">
                        {getFilteredItems().length}
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-sm font-mono mt-1">
                      <span className="text-gray-600">CHECKED:</span>
                      <span className="font-bold text-green-600">
                        {getFilteredItems().filter((i) => i.checked).length}
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-sm font-mono mt-1">
                      <span className="text-gray-600">REMAINING:</span>
                      <span className="font-bold text-orange-600">
                        {getFilteredItems().filter((i) => !i.checked).length}
                      </span>
                    </div>
                  </div>

                  <div className="text-center mt-6 text-xs text-gray-400 font-mono">
                    ═══════════════════════════
                    <br />
                    THANK YOU FOR USING RECIPE ASSISTANT
                    <br />
                    ═══════════════════════════
                  </div>
                </Card>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  )
}
