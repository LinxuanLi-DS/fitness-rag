// API Base URL - 部署后改成你的服务器地址
const BASE_URL = "http://127.0.0.1:8000";

interface RequestOptions {
  url: string;
  method?: "GET" | "POST" | "PUT" | "DELETE";
  data?: any;
  header?: Record<string, string>;
}

export function api<T = any>(options: RequestOptions): Promise<T> {
  const token = uni.getStorageSync("token");
  const header: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.header,
  };
  if (token) {
    header["Authorization"] = `Bearer ${token}`;
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || "GET",
      data: options.data,
      header,
      timeout: 30000,
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync("token");
          uni.redirectTo({ url: "/pages/login/login" });
          reject(new Error("未登录"));
          return;
        }
        resolve(res.data as T);
      },
      fail: (err) => {
        console.error("API request failed:", options.url, err);
        reject(err);
      },
    });
  });
}

export async function login(username: string, password: string) {
  const res = await api<{ access_token: string }>({
    url: "/users/login",
    method: "POST",
    data: { username, password },
  });
  uni.setStorageSync("token", res.access_token);
  return res;
}

export async function register(username: string, password: string) {
  return await api({
    url: "/users/register",
    method: "POST",
    data: { username, password },
  });
}

export async function chatStream(
  message: string,
  assistant: string,
  history: any[],
  onChunk: (text: string) => void
) {
  const token = uni.getStorageSync("token");

  return new Promise<void>((resolve, reject) => {
    const task = uni.request({
      url: BASE_URL + "/chat/stream",
      method: "POST",
      header: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      data: {
        query: message,
        user_profile: { assistant },
        chat_history: history,
      },
      enableChunked: true,
      success: () => resolve(),
      fail: (err) => reject(err),
    });

    task.onChunkReceived((res) => {
      const text = arrayBufferToString(res.data);
      // Parse SSE format: data: "text chunk"
      const lines = text.split("\n");
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6).trim();
          if (data === "[DONE]") return;
          // Try JSON parse (handles "quoted strings")
          try {
            const parsed = JSON.parse(data);
            if (typeof parsed === "string") {
              onChunk(parsed);
            } else if (parsed.content) {
              onChunk(parsed.content);
            }
          } catch (e) {
            // raw text
            if (data && data !== "[DONE]") {
              onChunk(data);
            }
          }
        }
      }
    });
  });
}

function arrayBufferToString(buffer: ArrayBuffer): string {
  const uint8 = new Uint8Array(buffer);
  let text = "";
  for (let i = 0; i < uint8.length; i++) {
    text += String.fromCharCode(uint8[i]);
  }
  // Decode UTF-8
  try {
    return decodeURIComponent(escape(text));
  } catch {
    return text;
  }
}
