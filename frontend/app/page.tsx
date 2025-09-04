import { RecipeCard } from "@/components/RecipeCard"
import { SearchBar } from "@/components/SearchBar"

export default function Home() {
  return (
    <main className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">🍳 Recipe Assistant</h1>
      <SearchBar />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
        {/* Map recipes from API */}
        <RecipeCard
          title="Spicy Chickpea Stir Fry"
          description="A quick vegan stir fry with sriracha and garlic"
          tags={["spicy", "vegan", "quick"]}
        />
      </div>
    </main>
  )
}
