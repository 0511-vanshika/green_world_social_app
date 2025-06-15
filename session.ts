import { cookies } from "next/headers"
import type { User } from "./auth"

export async function createSession(user: User) {
  try {
    const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days
    const sessionData = JSON.stringify({
      user,
      expires: expires.getTime(),
      created: Date.now(),
    })

    const cookieStore = await cookies()
    cookieStore.set("session", sessionData, {
      expires,
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
    })

    console.log("Session created successfully for user:", user.email)
  } catch (error) {
    console.error("Error creating session:", error)
    throw error
  }
}

export async function getSession() {
  try {
    const cookieStore = await cookies()
    const session = cookieStore.get("session")?.value

    if (!session) {
      return null
    }

    const payload = JSON.parse(session)

    // Check if session is expired
    if (Date.now() > payload.expires) {
      console.log("Session expired")
      return null
    }

    return payload
  } catch (error) {
    console.error("Error getting session:", error)
    return null
  }
}

export async function deleteSession() {
  try {
    const cookieStore = await cookies()
    cookieStore.set("session", "", {
      expires: new Date(0),
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
    })
    console.log("Session deleted successfully")
  } catch (error) {
    console.error("Error deleting session:", error)
  }
}
