"use client"
import { useState } from "react"

const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

export default function PlannerPage() {
  const [meals, setMeals] = useState<Record<string, string>>({})

  const handleChange = (day: string, value: string) => {
    setMeals((prev) => ({ ...prev, [day]: value }))
  }

  return (
    <main className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">🍽️ Weekly Meal Planner</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {days.map((day) => (
          <div key={day} className="border rounded-xl p-4 shadow-sm bg-white">
            <h2 className="font-semibold mb-2">{day}</h2>
            <input
              type="text"
              placeholder="Enter recipe..."
              value={meals[day] || ""}
              onChange={(e) => handleChange(day, e.target.value)}
              className="w-full border px-3 py-2 rounded"
            />
          </div>
        ))}
      </div>
    </main>
  )
}
