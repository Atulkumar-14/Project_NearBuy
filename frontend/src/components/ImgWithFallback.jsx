import React, { useState } from 'react'

export default function ImgWithFallback({ src, alt, className, fallback }) {
  const [failed, setFailed] = useState(false)
  if (!src || failed) return fallback || null
  return (
    <img
      src={src}
      alt={alt || ''}
      className={className}
      onError={() => setFailed(true)}
    />
  )
}