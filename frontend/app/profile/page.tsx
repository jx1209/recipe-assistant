'use client'

/**
 * user profile page
 */

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/Card'
import { User, Mail, Calendar, Settings } from 'lucide-react'

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  )
}

function ProfileContent() {
  const { user, updateUser } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [fullName, setFullName] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (user?.full_name) {
      setFullName(user.full_name)
    }
  }, [user])

  const handleSave = async () => {
    if (!fullName.trim()) return

    setIsLoading(true)
    try {
      await updateUser({ full_name: fullName })
      setIsEditing(false)
    } catch (error) {
      console.error('failed to update profile:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">profile settings</h1>
        <p className="text-gray-600 mt-2">manage your account information and preferences</p>
      </div>

      <div className="space-y-6">
        {/* profile information */}
        <Card variant="elevated">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
                <User className="h-6 w-6 text-primary-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">profile information</h2>
                <p className="text-sm text-gray-500">your personal details</p>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {isEditing ? (
              <Input
                label="full name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter your full name"
              />
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">full name</label>
                <p className="text-gray-900">{user?.full_name || 'not set'}</p>
              </div>
            )}

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
                <span className={`px-2 py-1 text-xs rounded-full ${
                  user?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {user?.is_active ? 'active' : 'inactive'}
                </span>
                {user?.is_verified && (
                  <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                    verified
                  </span>
                )}
              </div>
            </div>
          </CardContent>

          <CardFooter>
            {isEditing ? (
              <div className="flex space-x-2">
                <Button onClick={handleSave} isLoading={isLoading}>
                  save changes
                </Button>
                <Button variant="outline" onClick={() => {
                  setIsEditing(false)
                  setFullName(user?.full_name || '')
                }}>
                  cancel
                </Button>
              </div>
            ) : (
              <Button variant="outline" onClick={() => setIsEditing(true)}>
                edit profile
              </Button>
            )}
          </CardFooter>
        </Card>

        {/* preferences */}
        <Card variant="elevated">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
                <Settings className="h-6 w-6 text-primary-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">preferences</h2>
                <p className="text-sm text-gray-500">dietary restrictions and cuisine preferences</p>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  dietary restrictions
                </label>
                <div className="flex flex-wrap gap-2">
                  {user?.preferences?.dietary_restrictions?.length > 0 ? (
                    user.preferences.dietary_restrictions.map((restriction: string, idx: number) => (
                      <span key={idx} className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                        {restriction}
                      </span>
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm">no dietary restrictions set</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  favorite cuisines
                </label>
                <div className="flex flex-wrap gap-2">
                  {user?.preferences?.favorite_cuisines?.length > 0 ? (
                    user.preferences.favorite_cuisines.map((cuisine: string, idx: number) => (
                      <span key={idx} className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                        {cuisine}
                      </span>
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm">no favorite cuisines set</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  allergies
                </label>
                <div className="flex flex-wrap gap-2">
                  {user?.preferences?.allergies?.length > 0 ? (
                    user.preferences.allergies.map((allergy: string, idx: number) => (
                      <span key={idx} className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm">
                        {allergy}
                      </span>
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm">no allergies set</p>
                  )}
                </div>
              </div>
            </div>
          </CardContent>

          <CardFooter>
            <p className="text-sm text-gray-500">
              preferences can be updated through the API or upcoming settings page
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}

