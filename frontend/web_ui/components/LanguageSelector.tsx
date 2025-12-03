'use client'

interface LanguageSelectorProps {
  value: 'gu' | 'mr'
  onChange: (value: 'gu' | 'mr') => void
  disabled?: boolean
}

export default function LanguageSelector({ value, onChange, disabled }: LanguageSelectorProps) {
  return (
    <div className="w-full">
      <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
        Language
      </label>
      <div className="flex gap-2 flex-wrap">
        <button
          type="button"
          onClick={() => onChange('gu')}
          disabled={disabled}
          className={`flex-1 min-w-[120px] px-4 py-2 rounded-lg font-medium transition-colors
            ${value === 'gu'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            }
            disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          <span className="gujarati-text">ગુજરાતી</span> (Gujarati)
        </button>
        <button
          type="button"
          onClick={() => onChange('mr')}
          disabled={disabled}
          className={`flex-1 min-w-[120px] px-4 py-2 rounded-lg font-medium transition-colors
            ${value === 'mr'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            }
            disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          <span className="marathi-text">मराठी</span> (Marathi)
        </button>
      </div>
    </div>
  )
}

