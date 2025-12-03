'use client'

import { useState, useEffect } from 'react'

interface TextInputProps {
  value: string
  onChange: (value: string) => void
  language: 'gu' | 'mr'
  disabled?: boolean
}

export default function TextInput({ value, onChange, language, disabled }: TextInputProps) {
  const [charCount, setCharCount] = useState(0)

  useEffect(() => {
    setCharCount(value.length)
  }, [value])

  const languageClass = language === 'gu' ? 'gujarati-text' : 'marathi-text'
  const languageName = language === 'gu' ? 'Gujarati' : 'Marathi'
  const placeholder = language === 'gu' ? 'નમસ્તે, તમે કેમ છો?' : 'नमस्कार, तुम्ही कसे आहात?'

  return (
    <div className="w-full">
      <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
        Enter Text ({languageName})
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={`w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg 
          bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
          focus:ring-2 focus:ring-primary-500 focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          resize-none ${languageClass}`}
        rows={6}
        placeholder={placeholder}
      />
      <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
        {charCount} characters
      </div>
    </div>
  )
}

