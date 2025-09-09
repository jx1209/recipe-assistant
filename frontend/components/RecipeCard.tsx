type RecipeCardProps = {
  title: string;
  description: string;
  tags: string[];
};

export function RecipeCard({ title, description, tags }: RecipeCardProps) {
  return (
    <div className="bg-white rounded-xl shadow p-4 hover:shadow-lg transition">
      <h2 className="text-xl font-semibold">{title}</h2>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
      <div className="mt-2 flex flex-wrap gap-1">
        {tags.map((tag: string, idx: number) => (
          <span
            key={idx}
            className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}
