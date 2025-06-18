"use server"

import { redirect } from "next/navigation"
import { createUser, authenticateUser } from "@/lib/auth"
import { createSession, deleteSession } from "@/lib/session"
import { revalidatePath } from "next/cache"

export async function signup(prevState: any, formData: FormData) {
  try {
    const firstName = formData.get("firstName") as string
    const lastName = formData.get("lastName") as string
    const email = formData.get("email") as string
    const username = formData.get("username") as string
    const password = formData.get("password") as string
    const confirmPassword = formData.get("confirmPassword") as string

    console.log("Signup attempt for:", email)

    // Validation
    if (!firstName || !lastName || !email || !username || !password || !confirmPassword) {
      return { error: "All fields are required" }
    }

    if (password !== confirmPassword) {
      return { error: "Passwords do not match" }
    }

    if (password.length < 3) {
      return { error: "Password must be at least 3 characters long" }
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return { error: "Please enter a valid email address" }
    }

    // Username validation
    if (username.length < 3) {
      return { error: "Username must be at least 3 characters long" }
    }

    const user = await createUser({
      email: email.toLowerCase().trim(),
      username: username.toLowerCase().trim(),
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      password,
    })

    console.log("User created successfully, creating session")
    await createSession(user)

    console.log("Session created, revalidating path")
    revalidatePath("/")

    console.log("Signup process completed successfully")
  } catch (error: any) {
    console.error("Signup error:", error)

    if (
      error.message.includes("duplicate") ||
      error.message.includes("unique") ||
      error.message.includes("already exists")
    ) {
      return { error: "Email or username already exists" }
    }

    return { error: error.message || "Failed to create account. Please try again." }
  }

  redirect("/dashboard")
}

export async function login(prevState: any, formData: FormData) {
  try {
    const email = formData.get("email") as string
    const password = formData.get("password") as string

    console.log("Login attempt for:", email)

    if (!email || !password) {
      return { error: "Email and password are required" }
    }

    const user = await authenticateUser(email.toLowerCase().trim(), password)

    console.log("User authenticated successfully, creating session")
    await createSession(user)

    console.log("Session created, revalidating path")
    revalidatePath("/")

    console.log("Login process completed successfully")
  } catch (error: any) {
    console.error("Login error:", error)
    return { error: "Invalid email or password" }
  }

  redirect("/dashboard")
}

export async function logout() {
  try {
    console.log("Logout initiated")
    await deleteSession()
    revalidatePath("/")
    console.log("Logout completed successfully")
  } catch (error) {
    console.error("Logout error:", error)
  }
  redirect("/auth/login")
}
