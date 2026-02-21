// Auto-detect URL: Agar localhost hai toh local backend, warna production URL
const isLocal = typeof window !== 'undefined' && window.location.hostname === 'localhost';

const API_URL = isLocal 
  ? "http://127.0.0.1:8000/api" 
  : "https://chocogirl-full-stack-todo.hf.space/api";

/**
 * Tasks fetch karne ke liye function
 */
export async function getTasks(token: string) {
  try {
    const res = await fetch(`${API_URL}/tasks`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) return [];
    return await res.json();
  } catch (error) {
    console.error("Fetch tasks error:", error);
    return [];
  }
}

/**
 * Naya task create karne ke liye function
 */
export async function createTask(title: string, description: string, token: string) {
  try {
    const res = await fetch(`${API_URL}/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title, description }),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    return null;
  }
}

/**
 * Task ko complete/undo karne ke liye function
 */
export async function toggleTaskComplete(id: number, token: string) {
  try {
    const res = await fetch(`${API_URL}/tasks/${id}/complete`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    return null;
  }
}

/**
 * Task delete karne ke liye function
 */
export async function deleteTask(id: number, token: string) {
  try {
    const res = await fetch(`${API_URL}/tasks/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.ok;
  } catch (error) {
    return false;
  }
}

/**
 * AI Chatbot function (RAG)
 */
export async function getChatResponse(message: string) {
  try {
    const res = await fetch(`${API_URL}/chat?user_message=${encodeURIComponent(message)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      return { response: "AI server respond nahi kar raha. Check karein backend deployed hai ya nahi." };
    }

    return await res.json();
  } catch (error) {
    console.error("Chat Error:", error);
    return { response: "Network error! Backend link check karein." };
  }
}