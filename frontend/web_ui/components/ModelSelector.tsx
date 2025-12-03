'use client'

interface ModelSelectorProps {
  value: 'mms' | 'indic'
  onChange: (value: 'mms' | 'indic') => void
  disabled?: boolean
}

export default function ModelSelector({ value, onChange, disabled }: ModelSelectorProps) {
  const models = [
    { id: 'mms' as const, name: 'MMS-TTS', description: 'High Quality' },
    { id: 'indic' as const, name: 'IndicTTS', description: 'Fallback' },
  ]

  return (
    <div className="w-full">
      <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
        TTS Model
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as 'mms' | 'indic')}
        disabled={disabled}
        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
          bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
          focus:ring-2 focus:ring-primary-500 focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {models.map((model) => (
          <option key={model.id} value={model.id}>
            {model.name} - {model.description}
          </option>
        ))}
      </select>
    </div>
  )
}

