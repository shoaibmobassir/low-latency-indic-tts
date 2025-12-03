'use client'

import { useState } from 'react'
import TextInput from './TextInput'
import LanguageSelector from './LanguageSelector'
import ModelSelector from './ModelSelector'

export type TTSRequest = {
  text: string
  lang: 'gu' | 'mr'
  model: 'mms' | 'indic'
  chunk_ms: number
}

interface RequestFormProps {
  onSubmit: (request: TTSRequest) => void
  disabled?: boolean
}

export default function RequestForm({ onSubmit, disabled }: RequestFormProps) {
  const [text, setText] = useState('')
  const [lang, setLang] = useState<'gu' | 'mr'>('gu')
  const [model, setModel] = useState<'mms' | 'indic'>('mms')
  const [chunkMs, setChunkMs] = useState(40)
  
  const handleLangChange = (newLang: 'gu' | 'mr') => {
    setLang(newLang)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (text.trim() && !disabled) {
      onSubmit({ text: text.trim(), lang, model, chunk_ms: chunkMs })
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <TextInput value={text} onChange={setText} language={lang} disabled={disabled} />
      
      <LanguageSelector value={lang} onChange={handleLangChange} disabled={disabled} />
      
      <ModelSelector value={model} onChange={setModel} disabled={disabled} />
      
      <div className="w-full">
        <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
          Chunk Size: {chunkMs}ms
        </label>
        <input
          type="range"
          min="20"
          max="80"
          step="10"
          value={chunkMs}
          onChange={(e) => setChunkMs(Number(e.target.value))}
          disabled={disabled}
          className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer
            disabled:opacity-50"
        />
        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>20ms</span>
          <span>50ms</span>
          <span>80ms</span>
        </div>
      </div>

      <button
        type="submit"
        disabled={!text.trim() || disabled}
        className="w-full px-6 py-3 bg-primary-600 text-white rounded-lg font-medium
          hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors shadow-lg"
      >
        Speak
      </button>
    </form>
  )
}

