const MOCK_ITEMS = [
  { name: "chickpeas", quantity: "2 cans" },
  { name: "sriracha", quantity: "1 tbsp" },
  { name: "garlic", quantity: "3 cloves" },
  { name: "olive oil", quantity: "1 tbsp" }
]

export default function ShoppingListPage() {
  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">🛒 Shopping List</h1>
      <ul className="list-disc pl-5 space-y-2">
        {MOCK_ITEMS.map((item, idx) => (
          <li key={idx}>
            <span className="font-medium">{item.name}:</span> {item.quantity}
          </li>
        ))}
      </ul>
    </main>
  )
}
