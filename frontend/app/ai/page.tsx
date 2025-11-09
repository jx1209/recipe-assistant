'use client'

/**
 * AI features page
 */

import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Card, CardHeader, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import Link from 'next/link'
import { Sparkles, Wand2, MessageCircleQuestion, Repeat, Calendar } from 'lucide-react'

export default function AIFeaturesPage() {
  return (
    <ProtectedRoute>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">AI-powered features</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            harness the power of AI to enhance your cooking experience
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* generate recipe */}
          <Card variant="elevated" className="hover:shadow-2xl transition-shadow">
            <CardHeader>
              <div className="flex items-center space-x-3 mb-2">
                <div className="h-12 w-12 bg-primary-100 rounded-xl flex items-center justify-center">
                  <Wand2 className="h-6 w-6 text-primary-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">generate recipe</h2>
              </div>
              <p className="text-gray-600">
                create custom recipes from ingredients or description using AI
              </p>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 mb-4">
                <li>✓ generate from available ingredients</li>
                <li>✓ specify dietary restrictions</li>
                <li>✓ choose cuisine and difficulty</li>
                <li>✓ save directly to your collection</li>
              </ul>
              <Button className="w-full">
                <Wand2 className="h-4 w-4 mr-2" />
                coming soon
              </Button>
            </CardContent>
          </Card>

          {/* cooking Q&A */}
          <Card variant="elevated" className="hover:shadow-2xl transition-shadow">
            <CardHeader>
              <div className="flex items-center space-x-3 mb-2">
                <div className="h-12 w-12 bg-primary-100 rounded-xl flex items-center justify-center">
                  <MessageCircleQuestion className="h-6 w-6 text-primary-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">cooking Q&A</h2>
              </div>
              <p className="text-gray-600">
                get instant answers to your cooking questions
              </p>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 mb-4">
                <li>✓ ask about techniques and timing</li>
                <li>✓ get temperature and safety tips</li>
                <li>✓ learn ingredient measurements</li>
                <li>✓ recipe-specific guidance</li>
              </ul>
              <Button className="w-full">
                <MessageCircleQuestion className="h-4 w-4 mr-2" />
                coming soon
              </Button>
            </CardContent>
          </Card>

          {/* ingredient substitutions */}
          <Card variant="elevated" className="hover:shadow-2xl transition-shadow">
            <CardHeader>
              <div className="flex items-center space-x-3 mb-2">
                <div className="h-12 w-12 bg-primary-100 rounded-xl flex items-center justify-center">
                  <Repeat className="h-6 w-6 text-primary-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">smart substitutions</h2>
              </div>
              <p className="text-gray-600">
                find ingredient alternatives with AI assistance
              </p>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 mb-4">
                <li>✓ dietary-aware substitutions</li>
                <li>✓ based on your pantry</li>
                <li>✓ allergy-safe alternatives</li>
                <li>✓ measurement conversions</li>
              </ul>
              <Button className="w-full">
                <Repeat className="h-4 w-4 mr-2" />
                coming soon
              </Button>
            </CardContent>
          </Card>

          {/* meal plan generation */}
          <Card variant="elevated" className="hover:shadow-2xl transition-shadow">
            <CardHeader>
              <div className="flex items-center space-x-3 mb-2">
                <div className="h-12 w-12 bg-primary-100 rounded-xl flex items-center justify-center">
                  <Calendar className="h-6 w-6 text-primary-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">AI meal planning</h2>
              </div>
              <p className="text-gray-600">
                generate personalized weekly meal plans
              </p>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 mb-4">
                <li>✓ personalized to preferences</li>
                <li>✓ balanced nutrition targets</li>
                <li>✓ variety of cuisines</li>
                <li>✓ auto-generate shopping list</li>
              </ul>
              <Link href="/planner">
                <Button className="w-full">
                  <Calendar className="h-4 w-4 mr-2" />
                  go to meal planner
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* API key notice */}
        <Card className="mt-12 bg-blue-50 border-blue-200">
          <CardContent className="py-6">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <Sparkles className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-blue-900 mb-2">enable AI features</h3>
                <p className="text-sm text-blue-800 mb-3">
                  to use AI-powered features, you can either use the system's Claude API key or add your own personal API key for enhanced privacy and control.
                </p>
                <Button size="sm" variant="outline">
                  manage API keys
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </ProtectedRoute>
  )
}

