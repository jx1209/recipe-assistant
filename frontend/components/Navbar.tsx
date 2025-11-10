'use client'

/**
 * Enhanced navigation bar with beautiful animations and modern design
 */

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useState } from 'react'
import { 
  ChefHat, 
  Search, 
  CalendarDays, 
  ShoppingCart, 
  Sparkles,
  User,
  LogOut,
  Menu,
  X,
  Home
} from 'lucide-react'
import { Button } from './ui/Button'
import { Badge } from './ui/Badge'

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const pathname = usePathname()

  const navigation = [
    { name: 'home', href: '/', icon: Home },
    { name: 'recipes', href: '/search', icon: Search },
    { name: 'meal planner', href: '/planner', icon: CalendarDays },
    { name: 'shopping list', href: '/shopping-list', icon: ShoppingCart },
    { name: 'AI features', href: '/ai', icon: Sparkles, highlight: true },
  ]

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname?.startsWith(href)
  }

  return (
    <nav className="bg-white/80 backdrop-blur-lg shadow-soft border-b border-gray-200/50 sticky top-0 z-50 animate-fade-in-down">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="p-2 bg-gradient-primary rounded-lg group-hover:shadow-glow transition-all duration-300 group-hover:scale-105">
              <ChefHat className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-700 bg-clip-text text-transparent">
              Recipe Assistant
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const Icon = item.icon
              const active = isActive(item.href)
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`
                    relative flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200
                    ${active 
                      ? 'text-primary-600 bg-primary-50' 
                      : 'text-gray-700 hover:bg-gray-100 hover:text-primary-600'
                    }
                  `}
                >
                  <Icon className={`h-4 w-4 ${item.highlight ? 'text-secondary-500' : ''}`} />
                  <span className="text-sm">{item.name}</span>
                  {item.highlight && (
                    <Badge variant="secondary" size="sm" className="ml-1">New</Badge>
                  )}
                  {active && (
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-primary-600 rounded-full" />
                  )}
                </Link>
              )
            })}
          </div>

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-3">
            {isAuthenticated ? (
              <>
                <Link href="/profile">
                  <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                    <div className="w-7 h-7 bg-gradient-primary rounded-full flex items-center justify-center">
                      <User className="h-4 w-4 text-white" />
                    </div>
                    <span className="font-medium">{user?.full_name || user?.email?.split('@')[0]}</span>
                  </Button>
                </Link>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={logout} 
                  className="flex items-center space-x-2"
                >
                  <LogOut className="h-4 w-4" />
                  <span>logout</span>
                </Button>
              </>
            ) : (
              <>
                <Link href="/auth/login">
                  <Button variant="ghost" size="sm">login</Button>
                </Link>
                <Link href="/auth/register">
                  <Button variant="gradient" size="sm" rounded="full">
                    get started free
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 rounded-lg text-gray-700 hover:bg-gray-100 active:scale-95 transition-all"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200 animate-fade-in">
            <div className="space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon
                const active = isActive(item.href)
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`
                      flex items-center justify-between px-3 py-2.5 rounded-lg transition-all
                      ${active 
                        ? 'bg-primary-50 text-primary-600 font-semibold' 
                        : 'text-gray-700 hover:bg-gray-100'
                      }
                    `}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <div className="flex items-center space-x-2.5">
                      <Icon className={`h-5 w-5 ${item.highlight ? 'text-secondary-500' : ''}`} />
                      <span className="text-sm font-medium">{item.name}</span>
                    </div>
                    {item.highlight && <Badge variant="secondary" size="sm">New</Badge>}
                  </Link>
                )
              })}
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200 space-y-2">
              {isAuthenticated ? (
                <>
                  <Link href="/profile" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" size="sm" className="w-full justify-start">
                      <div className="w-7 h-7 bg-gradient-primary rounded-full flex items-center justify-center mr-2">
                        <User className="h-4 w-4 text-white" />
                      </div>
                      {user?.full_name || user?.email}
                    </Button>
                  </Link>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    fullWidth
                    onClick={() => {
                      logout()
                      setMobileMenuOpen(false)
                    }}
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    logout
                  </Button>
                </>
              ) : (
                <>
                  <Link href="/auth/login" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" size="sm" fullWidth>login</Button>
                  </Link>
                  <Link href="/auth/register" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="gradient" size="sm" fullWidth>get started free</Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

