'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { authApi, UserProfile } from '@/lib/api'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

interface AuthContextType {
  user: UserProfile | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  updateUser: (data: Partial<UserProfile>) => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  const isAuthenticated = !!user

  useEffect(() => {
    loadUser()
  }, [])

  const loadUser = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (token) {
        const userData = await authApi.getCurrentUser()
        setUser(userData)
      }
    } catch (error) {
      console.error('failed to load user:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login({ email, password })
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)

      const userData = await authApi.getCurrentUser()
      setUser(userData)

      toast.success('logged in successfully!')
      router.push('/')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'login failed'
      toast.error(message)
      throw error
    }
  }

  const register = async (email: string, password: string, fullName?: string) => {
    try {
      const response = await authApi.register({
        email,
        password,
        full_name: fullName,
      })

      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)

      const userData = await authApi.getCurrentUser()
      setUser(userData)

      toast.success('account created successfully!')
      router.push('/')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'registration failed'
      toast.error(message)
      throw error
    }
  }

  const logout = () => {
    authApi.logout()
    setUser(null)
    toast.success('logged out successfully')
    router.push('/auth/login')
  }

  const updateUser = async (data: Partial<UserProfile>) => {
    try {
      const updated = await authApi.updateProfile(data)
      setUser(updated)
      toast.success('profile updated!')
    } catch (error) {
      toast.error('failed to update profile')
      throw error
    }
  }

  const refreshUser = async () => {
    try {
      const userData = await authApi.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('failed to refresh user:', error)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        updateUser,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

