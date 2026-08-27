const ACCESS_TOKEN_KEY = "pm_access_token";
const REFRESH_TOKEN_KEY = "pm_refresh_token";

export const tokenStore = {
  getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return sessionStorage.getItem(ACCESS_TOKEN_KEY);
  },

  setAccessToken(token: string): void {
    if (typeof window === "undefined") return;
    sessionStorage.setItem(ACCESS_TOKEN_KEY, token);
  },

  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return sessionStorage.getItem(REFRESH_TOKEN_KEY);
  },

  setRefreshToken(token: string): void {
    if (typeof window === "undefined") return;
    sessionStorage.setItem(REFRESH_TOKEN_KEY, token);
  },

  setTokens(accessToken: string, refreshToken: string): void {
    this.setAccessToken(accessToken);
    this.setRefreshToken(refreshToken);
  },

  clear(): void {
    if (typeof window === "undefined") return;
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};
