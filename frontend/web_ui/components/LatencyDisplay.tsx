'use client'

interface LatencyDisplayProps {
  inferenceTimeMs?: number | null
  totalTimeMs?: number | null
  audioDurationMs?: number
  realTimeFactor?: number | null
  model?: string
  device?: string
  chunksSent?: number
  firstChunkTimeMs?: number | null
  chunkingTimeMs?: number | null
  perceivedLatencyMs?: number | null // Time from click to first audio playback
}

export default function LatencyDisplay({
  inferenceTimeMs,
  totalTimeMs,
  audioDurationMs,
  realTimeFactor,
  model,
  device,
  chunksSent,
  firstChunkTimeMs,
  chunkingTimeMs,
  perceivedLatencyMs,
}: LatencyDisplayProps) {
  if (!inferenceTimeMs && !totalTimeMs && !firstChunkTimeMs && !perceivedLatencyMs) {
    return null
  }

  const getLatencyColor = (ms: number | null | undefined, threshold: number) => {
    if (!ms) return 'text-gray-500'
    if (ms < threshold * 0.5) return 'text-green-600 dark:text-green-400'
    if (ms < threshold) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getLatencyLabel = (ms: number | null | undefined, threshold: number) => {
    if (!ms) return 'N/A'
    if (ms < threshold * 0.5) return 'Excellent'
    if (ms < threshold) return 'Good'
    return 'Slow'
  }

  const getRTFColor = (rtf: number | null | undefined) => {
    if (!rtf) return 'text-gray-500'
    if (rtf < 0.5) return 'text-green-600 dark:text-green-400'
    if (rtf < 1.0) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getRTFLabel = (rtf: number | null | undefined) => {
    if (!rtf) return 'N/A'
    if (rtf < 0.5) return 'Excellent'
    if (rtf < 1.0) return 'Good'
    if (rtf < 2.0) return 'Acceptable'
    return 'Slow'
  }

  return (
    <div className="mt-4 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-800 shadow-sm">
      <h3 className="text-base font-bold mb-3 text-gray-900 dark:text-gray-100 flex items-center gap-2">
        <span className="text-blue-600 dark:text-blue-400">⚡</span>
        Performance Metrics
      </h3>
      
      {/* Perceived Latency - Time from click to first audio playback */}
      {perceivedLatencyMs !== null && perceivedLatencyMs !== undefined && (
        <div className={`mb-4 p-3 rounded-lg border-2 ${
          perceivedLatencyMs < 100 ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700' :
          perceivedLatencyMs < 200 ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-700' :
          'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
                Perceived Latency (Click → Playback)
              </div>
              <div className={`font-mono font-bold text-2xl ${getLatencyColor(perceivedLatencyMs, 200)}`}>
                {perceivedLatencyMs.toFixed(0)}ms
              </div>
              <div className={`text-xs mt-1 font-semibold ${getLatencyColor(perceivedLatencyMs, 200)}`}>
                {getLatencyLabel(perceivedLatencyMs, 200)} • Target: &lt;100ms
              </div>
            </div>
            <div className="text-3xl">
              {perceivedLatencyMs < 100 ? '🚀' : perceivedLatencyMs < 200 ? '✅' : '⚠️'}
            </div>
          </div>
        </div>
      )}

      {/* First Chunk Latency - Backend metric */}
      {firstChunkTimeMs !== null && firstChunkTimeMs !== undefined && (
        <div className={`mb-4 p-3 rounded-lg border-2 ${
          firstChunkTimeMs < 50 ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700' :
          firstChunkTimeMs < 100 ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-700' :
          'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
                First Chunk Latency (Backend)
              </div>
              <div className={`font-mono font-bold text-xl ${getLatencyColor(firstChunkTimeMs, 100)}`}>
                {firstChunkTimeMs.toFixed(0)}ms
              </div>
              <div className={`text-xs mt-1 font-semibold ${getLatencyColor(firstChunkTimeMs, 100)}`}>
                {getLatencyLabel(firstChunkTimeMs, 100)} • Backend processing
              </div>
            </div>
            <div className="text-2xl">
              {firstChunkTimeMs < 50 ? '⚡' : firstChunkTimeMs < 100 ? '✅' : '⚠️'}
            </div>
          </div>
        </div>
      )}

      {/* Detailed Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        {inferenceTimeMs !== null && inferenceTimeMs !== undefined && (
          <div className="bg-white dark:bg-gray-800/50 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Inference Time</div>
            <div className="font-mono font-bold text-lg text-gray-900 dark:text-gray-100">
              {inferenceTimeMs.toFixed(0)}ms
            </div>
          </div>
        )}
        {totalTimeMs !== null && totalTimeMs !== undefined && (
          <div className="bg-white dark:bg-gray-800/50 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Total Time</div>
            <div className="font-mono font-bold text-lg text-gray-900 dark:text-gray-100">
              {totalTimeMs.toFixed(0)}ms
            </div>
          </div>
        )}
        {audioDurationMs !== undefined && (
          <div className="bg-white dark:bg-gray-800/50 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Audio Duration</div>
            <div className="font-mono font-bold text-lg text-gray-900 dark:text-gray-100">
              {audioDurationMs.toFixed(0)}ms
            </div>
          </div>
        )}
        {realTimeFactor !== null && realTimeFactor !== undefined && (
          <div className={`bg-white dark:bg-gray-800/50 p-3 rounded-lg border-2 ${
            realTimeFactor < 0.5 ? 'border-green-300 dark:border-green-700' :
            realTimeFactor < 1.0 ? 'border-yellow-300 dark:border-yellow-700' :
            'border-red-300 dark:border-red-700'
          }`}>
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Real-Time Factor</div>
            <div className={`font-mono font-bold text-lg ${getRTFColor(realTimeFactor)}`}>
              {realTimeFactor.toFixed(3)}x
            </div>
            <div className={`text-xs mt-1 font-semibold ${getRTFColor(realTimeFactor)}`}>
              {getRTFLabel(realTimeFactor)}
            </div>
          </div>
        )}
        {chunkingTimeMs !== null && chunkingTimeMs !== undefined && (
          <div className="bg-white dark:bg-gray-800/50 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Chunking Time</div>
            <div className="font-mono font-bold text-lg text-gray-900 dark:text-gray-100">
              {chunkingTimeMs.toFixed(1)}ms
            </div>
          </div>
        )}
      </div>
      
      {/* Latency Breakdown */}
      {(inferenceTimeMs || totalTimeMs || firstChunkTimeMs || perceivedLatencyMs) && (
        <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">Latency Breakdown</div>
          <div className="space-y-1 text-xs">
            {perceivedLatencyMs !== null && perceivedLatencyMs !== undefined && (
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Perceived Latency (Click → Playback:</span>
                <span className={`font-mono font-semibold ${getLatencyColor(perceivedLatencyMs, 200)}`}>
                  {perceivedLatencyMs.toFixed(1)}ms
                </span>
              </div>
            )}
            {firstChunkTimeMs !== null && firstChunkTimeMs !== undefined && (
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Time to First Chunk (Backend):</span>
                <span className="font-mono font-semibold text-gray-900 dark:text-gray-100">
                  {firstChunkTimeMs.toFixed(1)}ms
                </span>
              </div>
            )}
            {inferenceTimeMs !== null && inferenceTimeMs !== undefined && (
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Model Inference:</span>
                <span className="font-mono font-semibold text-gray-900 dark:text-gray-100">
                  {inferenceTimeMs.toFixed(1)}ms
                </span>
              </div>
            )}
            {chunkingTimeMs !== null && chunkingTimeMs !== undefined && (
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Audio Chunking:</span>
                <span className="font-mono font-semibold text-gray-900 dark:text-gray-100">
                  {chunkingTimeMs.toFixed(1)}ms
                </span>
              </div>
            )}
            {totalTimeMs !== null && totalTimeMs !== undefined && (
              <div className="flex justify-between pt-1 border-t border-gray-200 dark:border-gray-700">
                <span className="text-gray-700 dark:text-gray-300 font-semibold">Total Processing:</span>
                <span className="font-mono font-bold text-gray-900 dark:text-gray-100">
                  {totalTimeMs.toFixed(1)}ms
                </span>
              </div>
            )}
          </div>
        </div>
      )}
      
      {(model || device || chunksSent) && (
        <div className="mt-4 pt-3 border-t-2 border-gray-300 dark:border-gray-600 grid grid-cols-3 gap-3 text-xs">
          {model && (
            <div className="bg-white dark:bg-gray-800/50 px-2 py-1.5 rounded border border-gray-200 dark:border-gray-700">
              <div className="text-gray-500 dark:text-gray-400 mb-0.5">Model</div>
              <div className="font-bold text-gray-900 dark:text-gray-100 uppercase">{model}</div>
            </div>
          )}
          {device && (
            <div className="bg-white dark:bg-gray-800/50 px-2 py-1.5 rounded border border-gray-200 dark:border-gray-700">
              <div className="text-gray-500 dark:text-gray-400 mb-0.5">Device</div>
              <div className="font-bold text-gray-900 dark:text-gray-100 uppercase">{device}</div>
            </div>
          )}
          {chunksSent !== undefined && (
            <div className="bg-white dark:bg-gray-800/50 px-2 py-1.5 rounded border border-gray-200 dark:border-gray-700">
              <div className="text-gray-500 dark:text-gray-400 mb-0.5">Chunks</div>
              <div className="font-bold text-gray-900 dark:text-gray-100">{chunksSent}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

