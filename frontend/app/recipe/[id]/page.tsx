import { notFound } from "next/navigation"

type Recipe = {
  title: string
  description: string
  ingredients: string[]
  instructions: string[]
  tags?: string[]
}

// Simulate fetching from backend
async function fetchRecipe(id: string): Promise<Recipe | null> {
  // Replace with API call later
  const dummy = {
    title: "Spicy Chickpea Stir Fry",
    description: "A quick vegan stir fry with sriracha and garlic",
    ingredients: [
      "1 can chickpeas",
      "1 tbsp sriracha",
      "2 cloves garlic",
      "1 bell pepper",
      "1 tbsp olive oil"
    ],
    instructions: [
      "Rinse and drain chickpeas.",
      "Heat oil and sauté garlic.",
      "Add bell pepper and cook until soft.",
      "Add chickpeas and sriracha, stir-fry 5 minutes."
    ],
    tags: ["spicy", "vegan", "quick"]
  }

  return id === "123" ? dummy : null
}

export default async function RecipePage({ params }: { params: { id: string } }) {
  const recipe = await fetchRecipe(params.id)

  if (!recipe) return notFound()

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h1 className="text-3xl font-bold">{recipe.title}</h1>
      <p className="text-gray-600 mt-2">{recipe.description}</p>

      {recipe.tags && (
        <div className="mt-2 flex flex-wrap gap-1">
          {recipe.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      <section className="mt-6">
        <h2 className="text-xl font-semibold">Ingredients</h2>
        <ul className="list-disc pl-5 mt-2">
          {recipe.ingredients.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="mt-6">
        <h2 className="text-xl font-semibold">Instructions</h2>
        <ol className="list-decimal pl-5 mt-2 space-y-1">
          {recipe.instructions.map((step, idx) => (
            <li key={idx}>{step}</li>
          ))}
        </ol>
      </section>
    </main>
  )
}
