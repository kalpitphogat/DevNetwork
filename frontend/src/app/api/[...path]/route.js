/**
 * SentinelBrief — Backend Proxy Route
 *
 * Runs on Vercel Edge Runtime (no timeout on streaming responses).
 * Forwards all /api/* requests to the backend, adding the
 * bypass-tunnel-reminder header so localtunnel never shows the
 * HTML interception page to non-localhost callers.
 *
 * Set BACKEND_URL in Vercel environment variables when the tunnel URL changes.
 * Default: current working tunnel (moody-wasp-7.loca.lt)
 */

export const runtime = 'edge';

const BACKEND_URL =
  process.env.BACKEND_URL || 'https://sentinelbrief-backend.onrender.com';

async function handler(request, { params }) {
  const resolvedParams = await params;
  const pathSegments = resolvedParams?.path ?? [];
  const path = pathSegments.join('/');

  const url = new URL(request.url);
  const targetUrl = `${BACKEND_URL}/api/${path}${url.search}`;

  // Build forwarded headers — strip host, add tunnel bypass
  const headers = new Headers(request.headers);
  headers.delete('host');
  headers.set('bypass-tunnel-reminder', 'true');

  const isBodyMethod =
    request.method !== 'GET' && request.method !== 'HEAD';

  const backendResponse = await fetch(targetUrl, {
    method: request.method,
    headers,
    ...(isBodyMethod && { body: request.body }),
  });

  // Stream response body directly — no buffering, no timeout on SSE
  return new Response(backendResponse.body, {
    status: backendResponse.status,
    statusText: backendResponse.statusText,
    headers: backendResponse.headers,
  });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const DELETE = handler;
export const PATCH = handler;
