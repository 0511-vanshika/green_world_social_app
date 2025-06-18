import { supabase } from "./supabase"
import * as fallbackAuth from "./auth-fallback"

export interface User {
  id: string
  email: string
  username: string
  first_name: string
  last_name: string
  avatar_url?: string
  bio?: string
  location?: string
  growing_zone?: string
  created_at: string
}

// Simple hash function for demo purposes
function simpleHash(password: string): string {
  return Buffer.from(password).toString("base64")
}

function verifySimpleHash(password: string, hash: string): boolean {
  return Buffer.from(password).toString("base64") === hash
}

// Check if we should use Supabase or fallback
let useSupabase = true

async function checkSupabaseAvailability() {
  try {
    // Skip Supabase check for now and use fallback
    console.log("Using fallback authentication system")
    useSupabase = false
    return false
  } catch (error) {
    console.log("Using fallback authentication")
    useSupabase = false
    return false
  }
}

export async function createUser(userData: {
  email: string
  username: string
  firstName: string
  lastName: string
  password: string
}) {
  try {
    console.log("Using fallback authentication for user creation")
    return await fallbackAuth.createUser(userData)
  } catch (error: any) {
    console.error("Error in createUser:", error)
    throw error
  }
}

export async function authenticateUser(email: string, password: string) {
  try {
    console.log("Using fallback authentication for login")
    return await fallbackAuth.authenticateUser(email, password)
  } catch (error: any) {
    console.error("Error in authenticateUser:", error)
    throw error
  }
}

export async function getUserById(id: string) {
  try {
    if (!useSupabase) {
      return await fallbackAuth.getUserById(id)
    }

    const { data: user, error } = await supabase.from("users").select("*").eq("id", id).single()

    if (error) {
      console.error("Supabase error in getUserById, falling back:", error)
      useSupabase = false
      return await fallbackAuth.getUserById(id)
    }

    const { password_hash, ...userWithoutPassword } = user
    return userWithoutPassword
  } catch (error: any) {
    console.error("Error in getUserById, trying fallback:", error)

    if (error.message && error.message.includes("JSON")) {
      useSupabase = false
      return await fallbackAuth.getUserById(id)
    }

    throw error
  }
}
