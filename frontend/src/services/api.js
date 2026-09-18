const API_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? "http://localhost:8000" : "");

// ── Auth ──────────────────────────────────────────────────────

export async function registerUser(name, email, password) {
  const res = await fetch(`${API_URL}/api/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name,
      email,
      password,
    }),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || "Registration failed.");
  }

  return data;
}

export async function loginUser(email, password) {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || "Login failed.");
  }

  return data;
}

export async function getMe(token) {
  const res = await fetch(`${API_URL}/api/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error("Session expired.");
  }

  return res.json();
}

export async function logoutUser(token) {
  await fetch(`${API_URL}/api/auth/logout`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

// ── Chat & recommendations ────────────────────────────────────

export async function sendChatMessage(message, history, currentProfile) {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      history,
      current_profile: currentProfile,
    }),
  });

  if (!res.ok) {
    throw new Error(`Chat API error: ${res.statusText}`);
  }

  return await res.json();
}

export async function fetchRecommendations(studentProfile) {
  const res = await fetch(`${API_URL}/api/recommend`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(studentProfile),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));

    throw new Error(
      errorData.detail ||
        `Recommendation API error: ${res.statusText}`
    );
  }

  return await res.json();
}

export async function fetchAllPrograms() {
  const res = await fetch(`${API_URL}/api/programs`);

  if (!res.ok) {
    throw new Error(`Programs fetch error: ${res.statusText}`);
  }

  return await res.json();
}