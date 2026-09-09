/**
 * Returns the appropriate API base URL.
 * Prefers explicit VITE_API_URL env var if set.
 * Automatically falls back to the live Render backend URL when deployed in production (e.g. Vercel).
 * Defaults to http://localhost:8000 for local development.
 */
export const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL as string | undefined;
  if (envUrl && envUrl.trim().length > 0) {
    return envUrl.trim();
  }

  // Automatic production fallback when hosted on non-localhost domains (e.g. Vercel)
  if (
    typeof window !== 'undefined' &&
    window.location.hostname !== 'localhost' &&
    window.location.hostname !== '127.0.0.1'
  ) {
    return 'https://satquery-ai-1vmr.onrender.com';
  }

  return 'http://localhost:8000';
};
