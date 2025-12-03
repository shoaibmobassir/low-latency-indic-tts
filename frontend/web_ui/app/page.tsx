'use client'

import { useState, useEffect, useRef } from 'react'
import RequestForm, { TTSRequest } from '@/components/RequestForm'
import StreamingPlayer from '@/components/StreamingPlayer'
import LatencyDisplay from '@/components/LatencyDisplay'
import { TTSWebSocketClient, WebSocketStatus, ChunkMetadata } from '@/lib/websocket'
import { AudioPlayer } from '@/lib/audio'
import { ttsRequest, healthCheck } from '@/lib/api'

export default function Home() {
  const [wsStatus, setWsStatus] = useState<WebSocketStatus>('disconnected')
  const [playerStatus, setPlayerStatus] = useState<'idle' | 'connecting' | 'streaming' | 'playing' | 'finished' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)
  const [audioPlayer, setAudioPlayer] = useState<AudioPlayer | null>(null)
  const [useWebSocket, setUseWebSocket] = useState(true)
  const [latencyMetrics, setLatencyMetrics] = useState<{
    inferenceTimeMs?: number
    totalTimeMs?: number
    audioDurationMs?: number
    realTimeFactor?: number
    model?: string
    device?: string
    chunksSent?: number
    firstChunkTimeMs?: number
    chunkingTimeMs?: number
    perceivedLatencyMs?: number // Time from click to first audio playback
  } | null>(null)
  
  const wsClientRef = useRef<TTSWebSocketClient | null>(null)
  const audioPlayerRef = useRef<AudioPlayer | null>(null)
  const speakClickTimeRef = useRef<number | null>(null) // Track when "Speak" button was clicked

  useEffect(() => {
    // Initialize audio player
    const player = new AudioPlayer(16000)
    audioPlayerRef.current = player
    setAudioPlayer(player)

    // Set up end callback to update status when playback finishes
    player.setOnEnd(() => {
      console.log('🎵 Audio playback finished, resetting to idle')
      setPlayerStatus('idle')
      // Clear any error state
      setError(null)
      // Reset click time reference
      speakClickTimeRef.current = null
      // Clear audio buffer for next request
      player.clear()
    })

    // Check backend health
    healthCheck()
      .then((health) => {
        console.log('Backend health:', health)
      })
      .catch((err) => {
        console.error('Backend health check failed:', err)
        setError('Backend server not available. Make sure it\'s running on port 8050.')
      })

    return () => {
      if (wsClientRef.current) {
        wsClientRef.current.disconnect()
      }
      if (audioPlayerRef.current) {
        audioPlayerRef.current.clear()
      }
    }
  }, [])

  const handleWebSocketChunk = async (chunk: ArrayBuffer, metadata?: { type: string; server_received_ts: number; chunk_index: number; server_chunk_gen_ts: number; is_first_chunk: boolean }) => {
    if (audioPlayerRef.current) {
      // Track first chunk received timestamp
      const firstChunkReceivedTs = performance.now()
      
      // Start streaming on first chunk for low-latency playback
      if (!audioPlayerRef.current.isCurrentlyPlaying()) {
        await audioPlayerRef.current.startStreaming()
        setPlayerStatus('playing')
        
        // Get playback start timestamp from audio context
        const playbackStartTs = performance.now()
        
        // Calculate perceived latency: time from click to first audio playback
        if (speakClickTimeRef.current !== null) {
          const clickTs = speakClickTimeRef.current
          const perceivedLatency = playbackStartTs - clickTs
          
          // Calculate network latency (first chunk received - server sent)
          let networkLatency = null
          if (metadata?.is_first_chunk && metadata.server_chunk_gen_ts) {
            // Estimate: client received time - server generation time
            // Note: This is approximate due to clock skew, but useful for relative measurements
            const serverTs = metadata.server_chunk_gen_ts * 1000 // Convert to ms
            networkLatency = firstChunkReceivedTs - serverTs
          }
          
          // Update latency metrics with comprehensive timing
          setLatencyMetrics((prev) => ({
            ...prev,
            perceivedLatencyMs: perceivedLatency,
            firstChunkReceivedMs: firstChunkReceivedTs - clickTs,
            playbackStartMs: playbackStartTs - clickTs,
            networkLatencyMs: networkLatency,
          }))
          
          console.log(`🎵 Audio playback started!`, {
            clickTs,
            firstChunkReceivedTs,
            playbackStartTs,
            perceivedLatency: perceivedLatency.toFixed(1) + 'ms',
            networkLatency: networkLatency ? networkLatency.toFixed(1) + 'ms' : 'N/A',
            metadata: metadata?.is_first_chunk ? 'first chunk' : 'subsequent'
          })
          
          // Store metrics for experiments (if running in test mode)
          if (typeof window !== 'undefined' && (window as any).__CHUNK_SIZE_EXPERIMENT) {
            const experimentData = {
              chunk_size_ms: (window as any).__CURRENT_CHUNK_SIZE || 40,
              trial: (window as any).__CURRENT_TRIAL || 0,
              click_ts: clickTs,
              first_chunk_received_ts: firstChunkReceivedTs,
              playback_start_ts: playbackStartTs,
              perceived_latency_ms: perceivedLatency,
              network_latency_ms: networkLatency,
              server_chunk_gen_ts: metadata?.server_chunk_gen_ts ? metadata.server_chunk_gen_ts * 1000 : null,
            }
            console.log('📊 Experiment data:', experimentData)
            // Store in global for test script to collect
            if (!(window as any).__EXPERIMENT_RESULTS) {
              (window as any).__EXPERIMENT_RESULTS = []
            }
            ;(window as any).__EXPERIMENT_RESULTS.push(experimentData)
          }
          
          speakClickTimeRef.current = null // Reset after first use
        }
      }
      audioPlayerRef.current.addPCM16Chunk(chunk)
    }
  }

  const handleWebSocketEnd = async (message: {
    event: string
    duration_ms: number
    chunks_sent: number
    model: string
    device: string
    inference_time_ms?: number
    total_time_ms?: number
    real_time_factor?: number
    first_chunk_time_ms?: number
    chunking_time_ms?: number
  }) => {
    setWsStatus('connected')
    
    // Store latency metrics, preserving perceivedLatencyMs if it was already set
    setLatencyMetrics((prev) => ({
      inferenceTimeMs: message.inference_time_ms,
      totalTimeMs: message.total_time_ms,
      audioDurationMs: message.duration_ms,
      realTimeFactor: message.real_time_factor,
      model: message.model,
      device: message.device,
      chunksSent: message.chunks_sent,
      firstChunkTimeMs: message.first_chunk_time_ms,
      chunkingTimeMs: message.chunking_time_ms,
      // Preserve perceivedLatencyMs if it was already calculated
      perceivedLatencyMs: prev?.perceivedLatencyMs,
    }))
    
    // Stop streaming mode (audio should already be playing)
    // IMPORTANT: Wait a bit before stopping to ensure all chunks are received
    if (audioPlayerRef.current) {
      // Give a small delay to ensure any in-flight chunks are received and played
      setTimeout(() => {
        if (audioPlayerRef.current) {
          audioPlayerRef.current.stopStreaming()
          // Update status - if audio is still playing, keep it as 'playing'
          // The onEnd callback will update it to 'idle' when playback completes
          if (audioPlayerRef.current.isCurrentlyPlaying()) {
            setPlayerStatus('playing')
          } else {
            setPlayerStatus('idle')
          }
        }
      }, 100) // 100ms delay to catch any late-arriving chunks
    } else {
      setPlayerStatus('idle')
    }
  }

  const handleWebSocketError = (errorMsg: string) => {
    setError(errorMsg)
    setPlayerStatus('idle') // Re-enable form on error
    setWsStatus('error')
  }

  const handleWebSocketStatusChange = (status: WebSocketStatus) => {
    setWsStatus(status)
    if (status === 'streaming') {
      setPlayerStatus('streaming')
    } else if (status === 'connected') {
      // Only set to idle if we're not currently playing audio
      // This prevents resetting status while audio is still playing
      if (audioPlayerRef.current && !audioPlayerRef.current.isCurrentlyPlaying()) {
      setPlayerStatus('idle')
      }
    } else if (status === 'error') {
      setPlayerStatus('idle') // Re-enable form on error
    }
  }

  const handleSubmit = async (request: TTSRequest) => {
    setError(null)
    setLatencyMetrics(null) // Clear previous metrics
    
    // Clear previous audio before starting new request
    if (audioPlayerRef.current) {
      audioPlayerRef.current.clear()
      audioPlayerRef.current.stop()
    }
    
    // Record timestamp when "Speak" button is clicked
    // Use experiment click time if available (from test script), otherwise use performance.now()
    const clickTime = (typeof window !== 'undefined' && (window as any).__EXPERIMENT_CLICK_TS) 
      ? (window as any).__EXPERIMENT_CLICK_TS 
      : performance.now()
    speakClickTimeRef.current = clickTime
    console.log('🖱️ Speak button clicked at:', speakClickTimeRef.current)
    
    if (useWebSocket) {
      // WebSocket streaming
      if (!wsClientRef.current) {
        const client = new TTSWebSocketClient(
          handleWebSocketChunk,
          handleWebSocketEnd,
          handleWebSocketError,
          handleWebSocketStatusChange
        )
        wsClientRef.current = client
      }

      const client = wsClientRef.current
      
      // Always reconnect to ensure clean state for new request
      if (client.isConnected()) {
        client.disconnect()
        // Wait a bit for disconnect to complete
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
        client.connect()
        // Wait for connection
        await new Promise((resolve) => {
          const checkConnection = setInterval(() => {
            if (client.isConnected()) {
              clearInterval(checkConnection)
              resolve(null)
            }
          }, 100)
          setTimeout(() => {
            clearInterval(checkConnection)
            resolve(null)
          }, 5000)
        })

      if (client.isConnected() && audioPlayerRef.current) {
        // Initialize audio context on user interaction (required by browser)
        try {
          await audioPlayerRef.current.initialize()
        } catch (err) {
          console.error('Failed to initialize audio context:', err)
          setError('Failed to initialize audio. Please try again.')
          setPlayerStatus('idle') // Re-enable form on error
          return
        }
        
        // Clear previous audio and reset state
        audioPlayerRef.current.clear()
        setPlayerStatus('connecting')
        client.send(request)
      } else {
        setError('Failed to connect to WebSocket')
        setPlayerStatus('idle') // Re-enable form on error
      }
    } else {
      // REST API fallback
      setPlayerStatus('connecting')
      try {
        const { blob, metrics } = await ttsRequest({
          text: request.text,
          lang: request.lang,
          model: request.model,
        })

        // Store latency metrics
        setLatencyMetrics({
          inferenceTimeMs: metrics.inference_time_ms,
          totalTimeMs: metrics.total_time_ms,
          audioDurationMs: metrics.duration_ms,
          realTimeFactor: metrics.real_time_factor,
          model: metrics.model,
          device: metrics.device,
          chunksSent: undefined, // REST doesn't use chunks
        })

        // Create audio element and play
        const audioUrl = URL.createObjectURL(blob)
        const audio = new Audio(audioUrl)
        
        audio.onended = () => {
          setPlayerStatus('idle')
          URL.revokeObjectURL(audioUrl)
        }

        audio.onerror = () => {
          setError('Failed to play audio')
          setPlayerStatus('idle') // Re-enable form on error
          URL.revokeObjectURL(audioUrl)
        }

        // Record playback start time for REST API
        const playbackStartTime = performance.now()
        await audio.play()
        setPlayerStatus('playing')
        
        // Calculate perceived latency for REST API
        if (speakClickTimeRef.current !== null) {
          const perceivedLatency = playbackStartTime - speakClickTimeRef.current
          setLatencyMetrics((prev) => ({
            ...prev,
            perceivedLatencyMs: perceivedLatency,
          }))
          console.log(`🎵 Audio playback started! Perceived latency: ${perceivedLatency.toFixed(1)}ms`)
          speakClickTimeRef.current = null
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to generate audio')
        setPlayerStatus('idle') // Re-enable form on error
      }
    }
  }

  return (
    <main className="min-h-screen p-8 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8">
          <h1 className="text-3xl font-bold mb-2 text-gray-900 dark:text-gray-100">
            Gujarati & Marathi TTS
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            Real-time Text-to-Speech for Gujarati and Marathi languages
          </p>

          <div className="mb-6">
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input
                type="checkbox"
                checked={useWebSocket}
                onChange={(e) => setUseWebSocket(e.target.checked)}
                className="rounded"
              />
              Use WebSocket Streaming (real-time)
            </label>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
                Input
              </h2>
              <RequestForm onSubmit={handleSubmit} disabled={playerStatus === 'streaming' || playerStatus === 'connecting'} />
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
                Audio Player
              </h2>
              <StreamingPlayer
                audioPlayer={audioPlayer}
                status={playerStatus}
                error={error}
              />
              {latencyMetrics && (
                <LatencyDisplay
                  inferenceTimeMs={latencyMetrics.inferenceTimeMs}
                  totalTimeMs={latencyMetrics.totalTimeMs}
                  audioDurationMs={latencyMetrics.audioDurationMs}
                  realTimeFactor={latencyMetrics.realTimeFactor}
                  model={latencyMetrics.model}
                  device={latencyMetrics.device}
                  chunksSent={latencyMetrics.chunksSent}
                  firstChunkTimeMs={latencyMetrics.firstChunkTimeMs}
                  chunkingTimeMs={latencyMetrics.chunkingTimeMs}
                  perceivedLatencyMs={latencyMetrics.perceivedLatencyMs}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

