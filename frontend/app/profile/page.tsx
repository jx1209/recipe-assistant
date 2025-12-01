'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/Card'
import { User, Mail, Calendar, Settings, Activity, X, Search } from 'lucide-react'
import { authApi } from '@/lib/api'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  )
}

function ProfileContent() {
  const { user, updateUser, refreshUser } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isEditingPreferences, setIsEditingPreferences] = useState(false)
  
  // Profile fields
  const [fullName, setFullName] = useState('')
  const [height, setHeight] = useState('')
  const [weight, setWeight] = useState('')
  const [sex, setSex] = useState('')
  const [bodyType, setBodyType] = useState('')
  
  // Preferences
  const [dietaryRestrictions, setDietaryRestrictions] = useState<string[]>([])
  const [allergies, setAllergies] = useState<string[]>([])
  const [favoriteCuisines, setFavoriteCuisines] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [allergySearchTerm, setAllergySearchTerm] = useState('')
  const [cuisineSearchTerm, setCuisineSearchTerm] = useState('')
  
  const [isLoading, setIsLoading] = useState(false)

  // Common options
  const commonDietaryRestrictions = [
    'vegan', 'vegetarian', 'pescatarian', 'gluten-free', 'dairy-free',
    'nut-free', 'keto', 'paleo', 'low-carb', 'halal', 'kosher'
  ]

  const commonAllergies = [
    'peanuts', 'tree nuts', 'milk', 'eggs', 'wheat', 'soy',
    'fish', 'shellfish', 'sesame', 'mustard', 'celery', 'lupin'
  ]

  const commonCuisines = [
    'italian', 'mexican', 'chinese', 'japanese', 'indian', 'thai',
    'french', 'greek', 'spanish', 'korean', 'vietnamese', 'mediterranean',
    'american', 'middle eastern', 'caribbean', 'german', 'turkish'
  ]

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '')
      setHeight(user.height?.toString() || '')
      setWeight(user.weight?.toString() || '')
      setSex(user.sex || '')
      setBodyType(user.body_type || '')
      setDietaryRestrictions(user.preferences?.dietary_restrictions || [])
      setAllergies(user.preferences?.allergies || [])
      setFavoriteCuisines(user.preferences?.favorite_cuisines || [])
    }
  }, [user])

  const calculateBMI = (heightCm: number, weightKg: number) => {
    if (!heightCm || !weightKg) return null
    const heightM = heightCm / 100
    return (weightKg / (heightM * heightM)).toFixed(1)
  }

  const bmi = height && weight ? calculateBMI(parseFloat(height), parseFloat(weight)) : user?.bmi

  const handleSave = async () => {
    setIsLoading(true)
    try {
      const updates: any = {
        full_name: fullName || undefined,
        height: height ? parseFloat(height) : undefined,
        weight: weight ? parseFloat(weight) : undefined,
        sex: sex || undefined,
        body_type: bodyType || undefined,
        bmi: bmi ? parseFloat(bmi as string) : undefined,
      }

      await updateUser(updates)
      setIsEditing(false)
      toast.success('Profile updated successfully!')
    } catch (error) {
      console.error('failed to update profile:', error)
      toast.error('Failed to update profile')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSavePreferences = async () => {
    setIsLoading(true)
    try {
      await authApi.updatePreferences({
        dietary_restrictions: dietaryRestrictions,
        allergies: allergies,
        favorite_cuisines: favoriteCuisines,
      })
      await refreshUser()
      setIsEditingPreferences(false)
      toast.success('Preferences updated successfully!')
    } catch (error) {
      console.error('failed to update preferences:', error)
      toast.error('Failed to update preferences')
    } finally {
      setIsLoading(false)
    }
  }

  const addDietaryRestriction = (restriction: string) => {
    const lower = restriction.toLowerCase().trim()
    if (lower && !dietaryRestrictions.includes(lower)) {
      setDietaryRestrictions([...dietaryRestrictions, lower])
      setSearchTerm('')
    }
  }

  const removeDietaryRestriction = (restriction: string) => {
    setDietaryRestrictions(dietaryRestrictions.filter(r => r !== restriction))
  }

  const addAllergy = (allergy: string) => {
    const lower = allergy.toLowerCase().trim()
    if (lower && !allergies.includes(lower)) {
      setAllergies([...allergies, lower])
      setAllergySearchTerm('')
    }
  }

  const removeAllergy = (allergy: string) => {
    setAllergies(allergies.filter(a => a !== allergy))
  }

  const addCuisine = (cuisine: string) => {
    const lower = cuisine.toLowerCase().trim()
    if (lower && !favoriteCuisines.includes(lower)) {
      setFavoriteCuisines([...favoriteCuisines, lower])
      setCuisineSearchTerm('')
    }
  }

  const removeCuisine = (cuisine: string) => {
    setFavoriteCuisines(favoriteCuisines.filter(c => c !== cuisine))
  }

  const filteredDietaryOptions = commonDietaryRestrictions.filter(
    option => option.toLowerCase().includes(searchTerm.toLowerCase()) &&
             !dietaryRestrictions.includes(option)
  )

  const filteredAllergyOptions = commonAllergies.filter(
    option => option.toLowerCase().includes(allergySearchTerm.toLowerCase()) &&
             !allergies.includes(option)
  )

  const filteredCuisineOptions = commonCuisines.filter(
    option => option.toLowerCase().includes(cuisineSearchTerm.toLowerCase()) &&
             !favoriteCuisines.includes(option)
  )

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const firstName = user?.full_name?.split(' ')[0] || 'Your'

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-primary-50/30 to-secondary-50/20 px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Profile Settings</h1>
          <p className="text-gray-600 mt-2">manage your account information and preferences</p>
        </div>

        <div className="space-y-6">
          {/* Personal Information */}
          <Card variant="elevated">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-14 w-14 bg-gradient-primary rounded-full flex items-center justify-center shadow-lg">
                  <User className="h-7 w-7 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{firstName}'s Information</h2>
                  <p className="text-sm text-gray-500">your personal details</p>
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {isEditing ? (
                  <>
                    <Input
                      label="full name"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Jessica Xu"
                    />
                    
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">sex</label>
                      <select
                        value={sex}
                        onChange={(e) => setSex(e.target.value)}
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 bg-white text-gray-900"
                      >
                        <option value="">Select...</option>
                        <option value="female">Female</option>
                        <option value="male">Male</option>
                        <option value="other">Other</option>
                        <option value="prefer-not-to-say">Prefer not to say</option>
                      </select>
                    </div>

                    <Input
                      label="height (cm)"
                      type="number"
                      value={height}
                      onChange={(e) => setHeight(e.target.value)}
                      placeholder="165"
                    />

                    <Input
                      label="weight (kg)"
                      type="number"
                      value={weight}
                      onChange={(e) => setWeight(e.target.value)}
                      placeholder="60"
                    />

                    <div className="md:col-span-2">
                      <label className="block text-sm font-semibold text-gray-700 mb-2">body type</label>
                      <select
                        value={bodyType}
                        onChange={(e) => setBodyType(e.target.value)}
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 bg-white text-gray-900"
                      >
                        <option value="">Select...</option>
                        <option value="slim">Slim</option>
                        <option value="average">Average</option>
                        <option value="athletic">Athletic</option>
                        <option value="muscular">Muscular</option>
                        <option value="curvy">Curvy</option>
                        <option value="heavyset">Heavyset</option>
                      </select>
                    </div>

                    {bmi && (
                      <div className="md:col-span-2">
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          BMI (calculated)
                        </label>
                        <div className="flex items-center gap-2">
                          <span className="text-2xl font-bold text-orange-600">{bmi}</span>
                          <span className="text-sm text-gray-500">
                            {parseFloat(bmi) < 18.5 ? '(Underweight)' :
                             parseFloat(bmi) < 25 ? '(Normal)' :
                             parseFloat(bmi) < 30 ? '(Overweight)' : '(Obese)'}
                          </span>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">full name</label>
                      <p className="text-gray-900 font-medium">{user?.full_name || 'not set'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">sex</label>
                      <p className="text-gray-900 capitalize">{user?.sex || 'not set'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">height</label>
                      <p className="text-gray-900">{user?.height ? `${user.height} cm` : 'not set'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">weight</label>
                      <p className="text-gray-900">{user?.weight ? `${user.weight} kg` : 'not set'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">body type</label>
                      <p className="text-gray-900 capitalize">{user?.body_type || 'not set'}</p>
                    </div>

                    {user?.bmi && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">BMI</label>
                        <p className="text-2xl font-bold text-orange-600">{user.bmi}</p>
                      </div>
                    )}
                  </>
                )}
              </div>

              <div className="border-t pt-4 mt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Mail className="inline h-4 w-4 mr-1" />
                      email
                    </label>
                    <p className="text-gray-900">{user?.email}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Calendar className="inline h-4 w-4 mr-1" />
                      member since
                    </label>
                    <p className="text-gray-900">
                      {user?.created_at ? formatDate(user.created_at) : 'unknown'}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">account status</label>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                        user?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user?.is_active ? 'active' : 'inactive'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>

            <CardFooter>
              {isEditing ? (
                <div className="flex space-x-2">
                  <Button 
                    onClick={handleSave} 
                    isLoading={isLoading}
                    variant="gradient"
                  >
                    save changes
                  </Button>
                  <Button variant="outline" onClick={() => {
                    setIsEditing(false)
                    // Reset fields
                    setFullName(user?.full_name || '')
                    setHeight(user?.height?.toString() || '')
                    setWeight(user?.weight?.toString() || '')
                    setSex(user?.sex || '')
                    setBodyType(user?.body_type || '')
                  }}>
                    cancel
                  </Button>
                </div>
              ) : (
                <Button variant="outline" onClick={() => setIsEditing(true)}>
                  <Activity className="h-4 w-4 mr-2" />
                  edit profile
                </Button>
              )}
            </CardFooter>
          </Card>

          {/* Preferences */}
          <Card variant="elevated">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-14 w-14 bg-gradient-secondary rounded-full flex items-center justify-center shadow-lg">
                  <Settings className="h-7 w-7 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">preferences</h2>
                  <p className="text-sm text-gray-500">dietary restrictions, allergies, and favorite cuisines</p>
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Dietary Restrictions */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Dietary Restrictions
                </label>
                
                {isEditingPreferences ? (
                  <div className="space-y-3">
                    {/* Selected tags */}
                    <div className="flex flex-wrap gap-2 min-h-[40px] p-3 border border-gray-200 rounded-lg bg-gray-50">
                      {dietaryRestrictions.length > 0 ? (
                        dietaryRestrictions.map((restriction) => (
                          <span
                            key={restriction}
                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-primary-600 text-white rounded-full text-sm font-medium shadow-sm"
                          >
                            {restriction}
                            <button
                              onClick={() => removeDietaryRestriction(restriction)}
                              className="hover:bg-primary-700 rounded-full p-0.5 transition-colors"
                            >
                              <X className="h-3 w-3" />
                            </button>
                          </span>
                        ))
                      ) : (
                        <p className="text-gray-400 text-sm">No dietary restrictions selected</p>
                      )}
                    </div>

                    {/* Search box */}
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                      <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && searchTerm.trim()) {
                            addDietaryRestriction(searchTerm)
                          }
                        }}
                        placeholder="Search or type to add (press Enter)"
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-gray-900"
                      />
                    </div>

                    {/* Suggestions */}
                    {searchTerm && (
                      <div className="flex flex-wrap gap-2">
                        {filteredDietaryOptions.map((option) => (
                          <button
                            key={option}
                            onClick={() => addDietaryRestriction(option)}
                            className="px-3 py-1.5 bg-white border-2 border-primary-300 text-primary-700 rounded-full text-sm hover:bg-primary-50 transition-colors font-medium"
                          >
                            + {option}
                          </button>
                        ))}
                        {searchTerm && !commonDietaryRestrictions.includes(searchTerm.toLowerCase()) && (
                          <button
                            onClick={() => addDietaryRestriction(searchTerm)}
                            className="px-3 py-1.5 bg-primary-100 border-2 border-primary-400 text-primary-800 rounded-full text-sm hover:bg-primary-200 transition-colors font-medium"
                          >
                            + Add "{searchTerm}"
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {dietaryRestrictions.length > 0 ? (
                      dietaryRestrictions.map((restriction) => (
                        <span key={restriction} className="px-3 py-1.5 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                          {restriction}
                        </span>
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">no dietary restrictions set</p>
                    )}
                  </div>
                )}
              </div>

              {/* Favorite Cuisines */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Favorite Cuisines
                </label>
                
                {isEditingPreferences ? (
                  <div className="space-y-3">
                    {/* Selected tags */}
                    <div className="flex flex-wrap gap-2 min-h-[40px] p-3 border border-gray-200 rounded-lg bg-gray-50">
                      {favoriteCuisines.length > 0 ? (
                        favoriteCuisines.map((cuisine) => (
                          <span
                            key={cuisine}
                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-gradient-secondary text-white rounded-full text-sm font-medium shadow-sm"
                          >
                            {cuisine}
                            <button
                              onClick={() => removeCuisine(cuisine)}
                              className="hover:bg-secondary-700 rounded-full p-0.5 transition-colors"
                            >
                              <X className="h-3 w-3" />
                            </button>
                          </span>
                        ))
                      ) : (
                        <p className="text-gray-400 text-sm">No favorite cuisines selected</p>
                      )}
                    </div>

                    {/* Search box */}
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                      <input
                        type="text"
                        value={cuisineSearchTerm}
                        onChange={(e) => setCuisineSearchTerm(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && cuisineSearchTerm.trim()) {
                            addCuisine(cuisineSearchTerm)
                          }
                        }}
                        placeholder="Search or type to add (press Enter)"
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500 text-gray-900"
                      />
                    </div>

                    {/* Suggestions */}
                    {cuisineSearchTerm && (
                      <div className="flex flex-wrap gap-2">
                        {filteredCuisineOptions.map((option) => (
                          <button
                            key={option}
                            onClick={() => addCuisine(option)}
                            className="px-3 py-1.5 bg-white border-2 border-secondary-300 text-secondary-700 rounded-full text-sm hover:bg-secondary-50 transition-colors font-medium capitalize"
                          >
                            + {option}
                          </button>
                        ))}
                        {cuisineSearchTerm && !commonCuisines.includes(cuisineSearchTerm.toLowerCase()) && (
                          <button
                            onClick={() => addCuisine(cuisineSearchTerm)}
                            className="px-3 py-1.5 bg-secondary-100 border-2 border-secondary-400 text-secondary-800 rounded-full text-sm hover:bg-secondary-200 transition-colors font-medium"
                          >
                            + Add "{cuisineSearchTerm}"
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {favoriteCuisines.length > 0 ? (
                      favoriteCuisines.map((cuisine) => (
                        <span key={cuisine} className="px-3 py-1.5 bg-secondary-100 text-secondary-700 rounded-full text-sm font-medium capitalize">
                          {cuisine}
                        </span>
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">no favorite cuisines set</p>
                    )}
                  </div>
                )}
              </div>

              {/* Allergies */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Allergies
                </label>
                
                {isEditingPreferences ? (
                  <div className="space-y-3">
                    {/* Selected tags */}
                    <div className="flex flex-wrap gap-2 min-h-[40px] p-3 border border-gray-200 rounded-lg bg-gray-50">
                      {allergies.length > 0 ? (
                        allergies.map((allergy) => (
                          <span
                            key={allergy}
                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-red-500 text-white rounded-full text-sm font-medium shadow-sm"
                          >
                            {allergy}
                            <button
                              onClick={() => removeAllergy(allergy)}
                              className="hover:bg-red-600 rounded-full p-0.5 transition-colors"
                            >
                              <X className="h-3 w-3" />
                            </button>
                          </span>
                        ))
                      ) : (
                        <p className="text-gray-400 text-sm">No allergies selected</p>
                      )}
                    </div>

                    {/* Search box */}
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                      <input
                        type="text"
                        value={allergySearchTerm}
                        onChange={(e) => setAllergySearchTerm(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && allergySearchTerm.trim()) {
                            addAllergy(allergySearchTerm)
                          }
                        }}
                        placeholder="Search or type to add (press Enter)"
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900"
                      />
                    </div>

                    {/* Suggestions */}
                    {allergySearchTerm && (
                      <div className="flex flex-wrap gap-2">
                        {filteredAllergyOptions.map((option) => (
                          <button
                            key={option}
                            onClick={() => addAllergy(option)}
                            className="px-3 py-1.5 bg-white border-2 border-red-300 text-red-700 rounded-full text-sm hover:bg-red-50 transition-colors font-medium"
                          >
                            + {option}
                          </button>
                        ))}
                        {allergySearchTerm && !commonAllergies.includes(allergySearchTerm.toLowerCase()) && (
                          <button
                            onClick={() => addAllergy(allergySearchTerm)}
                            className="px-3 py-1.5 bg-red-100 border-2 border-red-400 text-red-800 rounded-full text-sm hover:bg-red-200 transition-colors font-medium"
                          >
                            + Add "{allergySearchTerm}"
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {allergies.length > 0 ? (
                      allergies.map((allergy) => (
                        <span key={allergy} className="px-3 py-1.5 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                          {allergy}
                        </span>
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">no allergies set</p>
                    )}
                  </div>
                )}
              </div>
            </CardContent>

            <CardFooter>
              {isEditingPreferences ? (
                <div className="flex space-x-2">
                  <Button 
                    onClick={handleSavePreferences} 
                    isLoading={isLoading}
                    variant="gradient"
                  >
                    save preferences
                  </Button>
                  <Button variant="outline" onClick={() => {
                    setIsEditingPreferences(false)
                    setDietaryRestrictions(user?.preferences?.dietary_restrictions || [])
                    setAllergies(user?.preferences?.allergies || [])
                    setFavoriteCuisines(user?.preferences?.favorite_cuisines || [])
                  }}>
                    cancel
                  </Button>
                </div>
              ) : (
                <Button variant="outline" onClick={() => setIsEditingPreferences(true)}>
                  <Settings className="h-4 w-4 mr-2" />
                  edit preferences
                </Button>
              )}
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  )
}
