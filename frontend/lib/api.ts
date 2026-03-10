/**
 * api client for recipe assistant
 * handles all backend api communication with axios
 */

import axios, { AxiosInstance, AxiosError } from 'axios'

// api configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token) {
        // ensure headers object exists before setting authorization
        if (!config.headers) {
          config.headers = {} as any
        }
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    // if 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // only attempt token refresh in browser environment
      if (typeof window !== 'undefined') {
        try {
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            const response = await axios.post(
              `${API_BASE_URL}/auth/refresh`,
              { refresh_token: refreshToken }
            )

            const { access_token, refresh_token: newRefreshToken } = response.data
            localStorage.setItem('access_token', access_token)
            localStorage.setItem('refresh_token', newRefreshToken)

            // retry original request with new token
            // ensure headers object exists before setting authorization
            if (!originalRequest.headers) {
              originalRequest.headers = {}
            }
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            return apiClient(originalRequest)
          }
        } catch (refreshError) {
          // refresh failed - clear tokens and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/auth/login'
          return Promise.reject(refreshError)
        }
      }
    }

    return Promise.reject(error)
  }
)

// typescript interfaces
export interface UserProfile {
  id: number
  email: string
  full_name: string | null
  created_at: string
  is_active: boolean
  is_verified: boolean
  preferences: Record<string, any>
  height?: number | null
  weight?: number | null
  sex?: string | null
  body_type?: string | null
  bmi?: number | null
}

export interface Recipe {
  id: number
  title: string
  description: string | null
  source_url: string | null
  source_name: string | null
  ingredients: RecipeIngredient[]
  instructions: string[]
  image_url: string | null
  prep_time: number | null
  cook_time: number | null
  servings: number
  difficulty: 'Easy' | 'Medium' | 'Hard' | null
  cuisine: string | null
  meal_type?: string | null
  tags: string[]
  created_by: number
  created_at: string
  updated_at: string
  average_rating: number | null
  rating_count: number
  total_ratings?: number  // alias for rating_count
  nutrition?: RecipeNutrition | null
  is_favorite?: boolean
  external?: boolean
}

export interface RecipeIngredient {
  name: string
  quantity?: number | null
  amount?: number | null  // alias for quantity for backward compatibility
  unit?: string | null
  notes?: string | null
}

export interface RecipeNutrition {
  calories?: number | null
  protein_g?: number | null
  carbs_g?: number | null
  fat_g?: number | null
  fiber_g?: number | null
  sugar_g?: number | null
  sodium_mg?: number | null
  cholesterol_mg?: number | null
}

export interface RecipeCreate {
  title: string
  description?: string | null
  source_url?: string | null
  source_name?: string | null
  ingredients: RecipeIngredient[]
  instructions: string[]
  image_url?: string | null
  prep_time_minutes?: number | null
  cook_time_minutes?: number | null
  servings?: number
  difficulty?: 'Easy' | 'Medium' | 'Hard' | null
  cuisine?: string | null
  tags?: string[]
  nutrition?: RecipeNutrition | null
}

export interface MealPlan {
  id: number
  user_id: number
  name: string
  start_date: string
  end_date: string
  meals: MealPlanDay[]
  created_at: string
  updated_at: string
}

export interface MealPlanDay {
  date: string
  breakfast?: number | null
  lunch?: number | null
  dinner?: number | null
  snacks?: number[] | null
}

export interface ShoppingList {
  id: number
  user_id: number
  name: string
  items: ShoppingListItem[]
  recipe_ids?: number[]
  created_at: string
  updated_at: string
  checked_items?: number
  total_items?: number
}

export interface ShoppingListItem {
  id?: number
  ingredient_name: string
  ingredient?: string  // alias for ingredient_name
  quantity?: number | null
  unit?: string | null
  notes?: string | null
  checked: boolean
  category?: string | null
  recipe_id?: number | null
}

// export alias for backward compatibility  
export type ShoppingItem = ShoppingListItem

export interface Rating {
  id: number
  recipe_id: number
  user_id: number
  rating: number
  comment: string | null
  created_at: string
  updated_at: string
}

// authentication api
export const authApi = {
  register: async (data: {
    email: string
    password: string
    full_name?: string
  }) => {
    const response = await apiClient.post('/auth/register', data)
    return response.data
  },

  login: async (data: { email: string; password: string }) => {
    const response = await apiClient.post('/auth/login', data)
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },

  getCurrentUser: async (): Promise<UserProfile> => {
    const response = await apiClient.get('/users/me')
    return response.data
  },

  updateProfile: async (data: Partial<UserProfile>): Promise<UserProfile> => {
    const response = await apiClient.put('/users/me', data)
    return response.data
  },

  updatePreferences: async (preferences: Record<string, any>) => {
    const response = await apiClient.put('/users/me/preferences', preferences)
    return response.data
  },

  refreshToken: async (refreshToken: string) => {
    const response = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },
}

// recipe api
export const recipeApi = {
  getRecipes: async (params?: {
    search?: string
    tags?: string[]
    cuisine?: string
    difficulty?: string
    min_rating?: number
    limit?: number
    offset?: number
  }): Promise<Recipe[]> => {
    const response = await apiClient.get('/recipes', { params })
    return response.data
  },

  getRecipe: async (id: number): Promise<Recipe> => {
    const response = await apiClient.get(`/recipes/${id}`)
    return response.data
  },

  createRecipe: async (data: RecipeCreate): Promise<Recipe> => {
    const response = await apiClient.post('/recipes', data)
    return response.data
  },

  updateRecipe: async (id: number, data: Partial<RecipeCreate>): Promise<Recipe> => {
    const response = await apiClient.put(`/recipes/${id}`, data)
    return response.data
  },

  deleteRecipe: async (id: number): Promise<void> => {
    await apiClient.delete(`/recipes/${id}`)
  },

  toggleFavorite: async (id: number): Promise<Recipe> => {
    const response = await apiClient.post(`/recipes/${id}/favorite`)
    return response.data
  },

  importRecipe: async (url: string): Promise<Recipe> => {
    const response = await apiClient.post('/recipes/import', { url })
    return response.data
  },

  searchRecipes: async (query: string): Promise<Recipe[]> => {
    const response = await apiClient.get('/recipes/search', {
      params: { q: query },
    })
    return response.data
  },

  getMyRecipes: async (): Promise<Recipe[]> => {
    const response = await apiClient.get('/recipes/my')
    return response.data
  },
}

// rating api
export const ratingApi = {
  rateRecipe: async (recipeId: number, rating: number, comment?: string) => {
    const response = await apiClient.post(`/recipes/${recipeId}/ratings`, {
      rating,
      comment,
    })
    return response.data
  },

  getRecipeRatings: async (recipeId: number): Promise<Rating[]> => {
    const response = await apiClient.get(`/recipes/${recipeId}/ratings`)
    return response.data
  },

  updateRating: async (
    recipeId: number,
    ratingId: number,
    rating: number,
    comment?: string
  ) => {
    const response = await apiClient.put(`/recipes/${recipeId}/ratings/${ratingId}`, {
      rating,
      comment,
    })
    return response.data
  },

  deleteRating: async (recipeId: number, ratingId: number) => {
    await apiClient.delete(`/recipes/${recipeId}/ratings/${ratingId}`)
  },
}

// meal plan api
export const mealPlanApi = {
  getMealPlans: async (): Promise<MealPlan[]> => {
    const response = await apiClient.get('/meal-plans')
    return response.data
  },

  getMealPlan: async (id: number): Promise<MealPlan> => {
    const response = await apiClient.get(`/meal-plans/${id}`)
    return response.data
  },

  createMealPlan: async (data: {
    name: string
    start_date: string
    end_date: string
    meals?: MealPlanDay[]
  }): Promise<MealPlan> => {
    const response = await apiClient.post('/meal-plans', data)
    return response.data
  },

  updateMealPlan: async (id: number, data: Partial<MealPlan>): Promise<MealPlan> => {
    const response = await apiClient.put(`/meal-plans/${id}`, data)
    return response.data
  },

  deleteMealPlan: async (id: number): Promise<void> => {
    await apiClient.delete(`/meal-plans/${id}`)
  },

  generateMealPlan: async (params: {
    days: number
    dietary_restrictions?: string[]
    preferences?: Record<string, any>
  }): Promise<MealPlan> => {
    const response = await apiClient.post('/meal-plans/generate', params)
    return response.data
  },
}

// shopping list api
export const shoppingListApi = {
  getShoppingLists: async (): Promise<ShoppingList[]> => {
    const response = await apiClient.get('/shopping-lists')
    return response.data
  },

  getShoppingList: async (id: number): Promise<ShoppingList> => {
    const response = await apiClient.get(`/shopping-lists/${id}`)
    return response.data
  },

  createShoppingList: async (data: {
    name: string
    items?: ShoppingListItem[]
    recipe_ids?: number[]
    exclude_pantry?: boolean
    group_by_category?: boolean
  }): Promise<ShoppingList> => {
    const response = await apiClient.post('/shopping-lists', data)
    return response.data
  },

  updateShoppingList: async (
    id: number,
    data: Partial<ShoppingList>
  ): Promise<ShoppingList> => {
    const response = await apiClient.put(`/shopping-lists/${id}`, data)
    return response.data
  },

  deleteShoppingList: async (id: number): Promise<void> => {
    await apiClient.delete(`/shopping-lists/${id}`)
  },

  addItem: async (listId: number, item: ShoppingListItem) => {
    const response = await apiClient.post(`/shopping-lists/${listId}/items`, item)
    return response.data
  },

  updateItem: async (listId: number, itemId: number, item: Partial<ShoppingListItem>) => {
    const response = await apiClient.put(`/shopping-lists/${listId}/items/${itemId}`, item)
    return response.data
  },

  deleteItem: async (listId: number, itemId: number) => {
    await apiClient.delete(`/shopping-lists/${listId}/items/${itemId}`)
  },

  generateFromRecipes: async (recipeIds: number[]): Promise<ShoppingList> => {
    const response = await apiClient.post('/shopping-lists/generate', {
      recipe_ids: recipeIds,
    })
    return response.data
  },
}

// ai api
export const aiApi = {
  generateRecipe: async (params: {
    ingredients?: string[]
    description?: string
    dietary_restrictions?: string[]
    cuisine?: string
    meal_type?: string
    difficulty?: string
  }): Promise<Recipe> => {
    const response = await apiClient.post('/ai/generate-recipe', params)
    return response.data
  },

  askCookingQuestion: async (question: string, recipeId?: number): Promise<string> => {
    const response = await apiClient.post('/ai/ask', {
      question,
      recipe_id: recipeId,
    })
    return response.data.answer
  },

  suggestSubstitutions: async (
    ingredient: string,
    recipeContext?: string
  ): Promise<string[]> => {
    const response = await apiClient.post('/ai/substitutions', {
      ingredient,
      recipe_context: recipeContext,
    })
    return response.data.substitutions
  },

  modifyRecipe: async (
    recipeId: number,
    modifications: string
  ): Promise<Recipe> => {
    const response = await apiClient.post(`/ai/modify-recipe/${recipeId}`, {
      modifications,
    })
    return response.data
  },
}

// nutrition api
export const nutritionApi = {
  analyzeRecipe: async (recipeId: number): Promise<RecipeNutrition> => {
    const response = await apiClient.post(`/nutrition/analyze/${recipeId}`)
    return response.data
  },

  calculateIngredient: async (ingredient: string, quantity: number, unit: string) => {
    const response = await apiClient.post('/nutrition/ingredient', {
      ingredient,
      quantity,
      unit,
    })
    return response.data
  },
}

// recommendations api
export const recommendationApi = {
  getRecommendations: async (limit: number = 10): Promise<Recipe[]> => {
    const response = await apiClient.get('/recommendations', {
      params: { limit },
    })
    return response.data
  },

  getSimilarRecipes: async (recipeId: number, limit: number = 5): Promise<Recipe[]> => {
    const response = await apiClient.get(`/recommendations/similar/${recipeId}`, {
      params: { limit },
    })
    return response.data
  },
}

export default apiClient
