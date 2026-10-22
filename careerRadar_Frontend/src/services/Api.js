const defaultApiHost = typeof window === 'undefined' ? '127.0.0.1' : window.location.hostname;
const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
export const API_BASE_URL = (
  configuredApiBaseUrl || (import.meta.env.PROD ? '' : `http://${defaultApiHost}:5000`)
).replace(/\/+$/, '');
export const ACCESS_TOKEN_KEY = 'careerradar:access-token';
export const SESSION_EXPIRED_MESSAGE = 'Your session has expired. Refresh the page to continue.';
export const TOKEN_NOT_YET_VALID_MESSAGE = 'Refresh the page to see the available jobs.';

export class ApiError extends Error {
  constructor(message, status, code = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

export async function apiRequest(path, { method = 'GET', body, signal, requireAuth = false } = {}) {
  if (!API_BASE_URL) {
    throw new ApiError(
      'CareerRadar API is not configured for this deployment. Set VITE_API_BASE_URL in Netlify to your deployed backend HTTPS URL, then redeploy.',
      0,
      'API_NOT_CONFIGURED',
    );
  }

  const headers = {};
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (requireAuth && !token) {
    throw new ApiError('Your session has expired. Please sign in again.', 401, 'AUTH_REQUIRED');
  }
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers['Content-Type'] = 'application/json';

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    if (error instanceof TypeError) {
      throw new ApiError(
        `Could not connect to CareerRadar at ${API_BASE_URL}. Check that the backend is running and VITE_API_BASE_URL points to it.`,
        0,
      );
    }
    throw error;
  }

  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new ApiError(
      `CareerRadar returned an unreadable response (${response.status}). Check the backend server logs.`,
      response.status,
    );
  }
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new ApiError(
      `CareerRadar returned an invalid response (${response.status}). Check the backend server logs.`,
      response.status,
    );
  }
  if (!response.ok || payload.success === false) {
    const message = payload.error?.message || payload.message || payload.msg || `Request failed (${response.status})`;
    if ((response.status === 401 || response.status === 422) && /token.*not yet valid|not yet valid.*token|\biat\b/i.test(message)) {
      throw new ApiError(TOKEN_NOT_YET_VALID_MESSAGE, response.status, 'TOKEN_NOT_YET_VALID');
    }
    if ((response.status === 401 || response.status === 422) && /token.*expired|expired.*token/i.test(message)) {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      throw new ApiError(SESSION_EXPIRED_MESSAGE, response.status, 'TOKEN_EXPIRED');
    }
    throw new ApiError(message, response.status, payload.error?.code || null);
  }
  return payload;
}

export const apiGet = (path, options) => apiRequest(path, options);
export const apiPost = (path, body, options) => apiRequest(path, { ...options, method: 'POST', body });
export const apiPatch = (path, body, options) => apiRequest(path, { ...options, method: 'PATCH', body });
export const apiDelete = (path, options) => apiRequest(path, { ...options, method: 'DELETE' });
