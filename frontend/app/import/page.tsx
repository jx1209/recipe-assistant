"use client"
import { useState } from "react"

export default function ImportPage() {
  const [url, setUrl] = useState("")
  const [text, setText] = useState("")
  const [result, setResult] = useState<any>(null)

  const handleImport = () => {
    if (url) {
      setResult({ source: "url", data: `Pretend we fetched: ${url}` })
    } else if (text) {
      setResult({ source: "text", data: text.slice(0, 100) + "..." })
    } else {
      alert("Please provide a URL or paste recipe text")
    }
  }

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">📥 Import a Recipe</h1>

      <label className="block mb-2 font-medium">Paste recipe URL</label>
      <input
        type="text"
        placeholder="https://allrecipes.com/..."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        className="w-full border px-3 py-2 rounded mb-4"
      />

      <label className="block mb-2 font-medium">Or paste recipe text</label>
      <textarea
        placeholder="Title\nIngredients\nInstructions..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        className="w-full border px-3 py-2 rounded h-40"
      />

      <button onClick={handleImport} className="mt-4 bg-green-600 text-white px-4 py-2 rounded">
        Import Recipe
      </button>

      {result && (
        <div className="mt-6 bg-gray-50 p-4 border rounded">
          <p className="font-semibold">✅ Imported from {result.source}:</p>
          <pre className="mt-2 text-sm text-gray-700 whitespace-pre-wrap">{result.data}</pre>
        </div>
      )}
    </main>
  )
}
