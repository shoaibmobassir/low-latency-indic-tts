'use client'

import { useState, useEffect, useRef } from 'react'
import { AudioPlayer } from '@/lib/audio'

interface StreamingPlayerProps {
  audioPlayer: AudioPlayer | null
  status: 'idle' | 'connecting' | 'streaming' | 'playing' | 'finished' | 'error'
  error: string | null
}

export default function StreamingPlayer({ audioPlayer, status, error }: StreamingPlayerProps) {
  const [progress, setProgress] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)

  useEffect(() => {
    if (audioPlayer) {
      audioPlayer.setOnProgress((p) => setProgress(p))
      audioPlayer.setOnEnd(() => {
        setIsPlaying(false)
        setProgress(1.0)
      })
    }
  }, [audioPlayer])

  // Sync playing state with audio player
  useEffect(() => {
    if (audioPlayer) {
      const checkPlaying = () => {
        const currentlyPlaying = audioPlayer.isCurrentlyPlaying()
        const isPaused = audioPlayer.isPausedState()
        setIsPlaying(currentlyPlaying || (isPaused && status === 'playing'))
      }
      
      // Check periodically to sync state
      const interval = setInterval(checkPlaying, 100)
      checkPlaying() // Initial check
      
      return () => clearInterval(interval)
    }
  }, [audioPlayer, status])

  const handlePlayPause = async () => {
    if (!audioPlayer) return

    try {
      if (audioPlayer.isPausedState()) {
        // Resume if paused
        audioPlayer.resume()
        setIsPlaying(true)
      } else if (audioPlayer.isCurrentlyPlaying()) {
        // Pause if playing
        audioPlayer.pause()
        setIsPlaying(false)
      } else {
        // Start playing if not playing
        setIsPlaying(true)
        if (progress === 1.0) {
          setProgress(0) // Reset if finished
        }
        await audioPlayer.play()
      }
    } catch (err) {
      console.error('Playback error:', err)
      setIsPlaying(false)
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'connecting':
        return 'bg-yellow-500'
      case 'streaming':
        return 'bg-blue-500'
      case 'playing':
        return 'bg-green-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-gray-400'
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'connecting':
        return 'Connecting...'
      case 'streaming':
        return 'Streaming...'
      case 'playing':
        return 'Playing...'
      case 'finished':
        return 'Finished'
      case 'error':
        return 'Error'
      default:
        return 'Ready'
    }
  }

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${getStatusColor()} animate-pulse`} />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {getStatusText()}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handlePlayPause}
            disabled={!audioPlayer || status === 'connecting' || (status === 'idle' && progress === 0)}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700
              disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isPlaying ? (
              <>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Pause
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
                Play
              </>
            )}
          </button>
          <button
            onClick={() => {
              if (audioPlayer) {
                audioPlayer.stop()
                setIsPlaying(false)
                setProgress(0)
              }
            }}
            disabled={!audioPlayer || (status === 'idle' && progress === 0)}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700
              disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Stop
          </button>
        </div>
      </div>

      {status === 'streaming' || status === 'playing' || progress > 0 ? (
        <div className="w-full">
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-600 transition-all duration-300"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
          <div className="mt-1 text-xs text-gray-500 dark:text-gray-400 text-right">
            {Math.round(progress * 100)}%
          </div>
        </div>
      ) : null}

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}
    </div>
  )
}

