'use client'

/**
 * registration page
 */

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardFooter } from '@/components/ui/Card'
import Link from 'next/link'
import { ChefHat } from 'lucide-react'

export default function RegisterPage() {
  const { register } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!email.includes('@')) {
      newErrors.email = 'please enter a valid email'
    }

    if (password.length < 8) {
      newErrors.password = 'password must be at least 8 characters'
    }

    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'passwords do not match'
    }

    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      newErrors.password = 'password must contain uppercase, lowercase, and number'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsLoading(true)

    try {
      await register(email, password, fullName || undefined)
    } catch (err: any) {
      setErrors({
        general: err.response?.data?.detail || 'registration failed. please try again.'
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 hover:opacity-80 transition">
            <ChefHat className="h-12 w-12 text-primary-600" />
            <span className="text-3xl font-bold text-gray-900">Recipe Assistant</span>
          </Link>
          <p className="mt-2 text-gray-600">create your account and start cooking!</p>
        </div>

        <Card variant="elevated">
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {errors.general && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">{errors.general}</p>
                </div>
              )}

              <Input
                type="text"
                label="full name"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                autoComplete="name"
              />

              <Input
                type="email"
                label="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={errors.email}
                required
                autoComplete="email"
              />

              <Input
                type="password"
                label="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={errors.password}
                helperText="must be 8+ characters with uppercase, lowercase, and number"
                required
                autoComplete="new-password"
              />

              <Input
                type="password"
                label="confirm password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                error={errors.confirmPassword}
                required
                autoComplete="new-password"
              />

              <Button type="submit" className="w-full" isLoading={isLoading}>
                {isLoading ? 'creating account...' : 'create account'}
              </Button>
            </form>
          </CardContent>

          <CardFooter>
            <p className="text-sm text-gray-600 text-center w-full">
              already have an account?{' '}
              <Link href="/auth/login" className="text-primary-600 hover:text-primary-700 font-medium">
                sign in
              </Link>
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}

