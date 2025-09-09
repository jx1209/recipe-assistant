"use client"

import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import { RecipeCard } from "@/components/RecipeCard"

type Recipe = {
  title: string
  description: string
  tags: string[]
}

const MOCK_RECIPES: Recipe[] = [
  {
    title: "Spicy Chickpea Stir Fry",
    description: "Quick vegan stir fry with chickpeas and sriracha",
    tags: ["spicy", "vegan", "quick"]
  },
  {
    title: "Garlic Butter Pasta",
    description: "Simple pasta with garlic and butter sauce",
    tags: ["vegetarian", "quick"]
  }
]

export default function SearchPage() {
  const searchParams = useSearchParams()
  const query = searchParams.get("q")?.toLowerCase() || ""
  const [results, setResults] = useState<Recipe[]>([])

  useEffect(() => {
    const filtered = MOCK_RECIPES.filter((r) =>
      r.title.toLowerCase().includes(query) ||
      r.description.toLowerCase().includes(query) ||
      r.tags.some((tag) => tag.toLowerCase().includes(query))
    )
    setResults(filtered)
  }, [query])

  return (
    <main className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">Search results for: <span className="italic">{query}</span></h1>

      {results.length === 0 ? (
        <p>No results found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((recipe, idx) => (
            <RecipeCard
              key={idx}
              title={recipe.title}
              description={recipe.description}
              tags={recipe.tags}
            />
          ))}
        </div>
      )}
    </main>
  )
}
