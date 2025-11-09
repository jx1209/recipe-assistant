'use client'

/**
 * reusable recipe form component
 */

import { useState, useEffect } from 'react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Card, CardContent, CardHeader } from './ui/Card'
import { Plus, X } from 'lucide-react'
import { RecipeIngredient } from '@/lib/api'

interface RecipeFormData {
  title: string
  description: string
  ingredients: RecipeIngredient[]
  instructions: string[]
  prep_time: number | null
  cook_time: number | null
  servings: number
  difficulty: string
  cuisine: string
  meal_type: string
  tags: string[]
  image_url: string
  source_url: string
}

interface RecipeFormProps {
  initialData?: Partial<RecipeFormData>
  onSubmit: (data: RecipeFormData) => Promise<void>
  submitLabel?: string
  isLoading?: boolean
}

export function RecipeForm({ 
  initialData, 
  onSubmit, 
  submitLabel = 'save recipe',
  isLoading = false 
}: RecipeFormProps) {
  const [formData, setFormData] = useState<RecipeFormData>({
    title: '',
    description: '',
    ingredients: [{ name: '', amount: null, unit: null, notes: null }],
    instructions: [''],
    prep_time: null,
    cook_time: null,
    servings: 4,
    difficulty: 'medium',
    cuisine: '',
    meal_type: '',
    tags: [],
    image_url: '',
    source_url: '',
    ...initialData,
  })

  const [newTag, setNewTag] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // filter out empty ingredients and instructions
    const cleanedData = {
      ...formData,
      ingredients: formData.ingredients.filter(ing => ing.name.trim()),
      instructions: formData.instructions.filter(inst => inst.trim()),
      tags: formData.tags.filter(tag => tag.trim()),
    }

    await onSubmit(cleanedData)
  }

  const addIngredient = () => {
    setFormData({
      ...formData,
      ingredients: [...formData.ingredients, { name: '', amount: null, unit: null, notes: null }]
    })
  }

  const removeIngredient = (index: number) => {
    setFormData({
      ...formData,
      ingredients: formData.ingredients.filter((_, i) => i !== index)
    })
  }

  const updateIngredient = (index: number, field: keyof RecipeIngredient, value: any) => {
    const newIngredients = [...formData.ingredients]
    newIngredients[index] = { ...newIngredients[index], [field]: value }
    setFormData({ ...formData, ingredients: newIngredients })
  }

  const addInstruction = () => {
    setFormData({
      ...formData,
      instructions: [...formData.instructions, '']
    })
  }

  const removeInstruction = (index: number) => {
    setFormData({
      ...formData,
      instructions: formData.instructions.filter((_, i) => i !== index)
    })
  }

  const updateInstruction = (index: number, value: string) => {
    const newInstructions = [...formData.instructions]
    newInstructions[index] = value
    setFormData({ ...formData, instructions: newInstructions })
  }

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, newTag.trim()]
      })
      setNewTag('')
    }
  }

  const removeTag = (tag: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(t => t !== tag)
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* basic info */}
      <Card variant="elevated">
        <CardHeader>
          <h2 className="text-xl font-semibold text-gray-900">basic information</h2>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            label="recipe title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
            placeholder="e.g. Spicy Chickpea Stir Fry"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="brief description of the recipe..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="prep time (minutes)"
              type="number"
              value={formData.prep_time || ''}
              onChange={(e) => setFormData({ ...formData, prep_time: e.target.value ? parseInt(e.target.value) : null })}
              placeholder="15"
            />

            <Input
              label="cook time (minutes)"
              type="number"
              value={formData.cook_time || ''}
              onChange={(e) => setFormData({ ...formData, cook_time: e.target.value ? parseInt(e.target.value) : null })}
              placeholder="30"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="servings"
              type="number"
              value={formData.servings}
              onChange={(e) => setFormData({ ...formData, servings: parseInt(e.target.value) || 1 })}
              required
              min="1"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">difficulty</label>
              <select
                value={formData.difficulty}
                onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="easy">easy</option>
                <option value="medium">medium</option>
                <option value="hard">hard</option>
              </select>
            </div>

            <Input
              label="cuisine"
              value={formData.cuisine}
              onChange={(e) => setFormData({ ...formData, cuisine: e.target.value })}
              placeholder="e.g. Italian"
            />
          </div>

          <Input
            label="meal type"
            value={formData.meal_type}
            onChange={(e) => setFormData({ ...formData, meal_type: e.target.value })}
            placeholder="e.g. dinner"
          />
        </CardContent>
      </Card>

      {/* ingredients */}
      <Card variant="elevated">
        <CardHeader>
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">ingredients</h2>
            <Button type="button" size="sm" onClick={addIngredient}>
              <Plus className="h-4 w-4 mr-1" />
              add ingredient
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {formData.ingredients.map((ingredient, index) => (
            <div key={index} className="flex gap-2">
              <Input
                placeholder="ingredient name"
                value={ingredient.name}
                onChange={(e) => updateIngredient(index, 'name', e.target.value)}
                className="flex-1"
              />
              <Input
                type="number"
                placeholder="amount"
                value={ingredient.amount || ''}
                onChange={(e) => updateIngredient(index, 'amount', e.target.value ? parseFloat(e.target.value) : null)}
                className="w-24"
              />
              <Input
                placeholder="unit"
                value={ingredient.unit || ''}
                onChange={(e) => updateIngredient(index, 'unit', e.target.value)}
                className="w-24"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeIngredient(index)}
                disabled={formData.ingredients.length === 1}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* instructions */}
      <Card variant="elevated">
        <CardHeader>
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">instructions</h2>
            <Button type="button" size="sm" onClick={addInstruction}>
              <Plus className="h-4 w-4 mr-1" />
              add step
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {formData.instructions.map((instruction, index) => (
            <div key={index} className="flex gap-2">
              <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                {index + 1}
              </span>
              <textarea
                value={instruction}
                onChange={(e) => updateInstruction(index, e.target.value)}
                placeholder={`step ${index + 1}...`}
                rows={2}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeInstruction(index)}
                disabled={formData.instructions.length === 1}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* tags and media */}
      <Card variant="elevated">
        <CardHeader>
          <h2 className="text-xl font-semibold text-gray-900">tags & media</h2>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">tags</label>
            <div className="flex gap-2 mb-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                placeholder="add a tag..."
              />
              <Button type="button" onClick={addTag}>add</Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm flex items-center gap-2"
                >
                  {tag}
                  <button type="button" onClick={() => removeTag(tag)}>
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          <Input
            label="image URL"
            value={formData.image_url}
            onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
            placeholder="https://example.com/image.jpg"
          />

          <Input
            label="source URL"
            value={formData.source_url}
            onChange={(e) => setFormData({ ...formData, source_url: e.target.value })}
            placeholder="https://example.com/recipe"
          />
        </CardContent>
      </Card>

      {/* submit */}
      <div className="flex justify-end gap-4">
        <Button type="submit" isLoading={isLoading}>
          {submitLabel}
        </Button>
      </div>
    </form>
  )
}

