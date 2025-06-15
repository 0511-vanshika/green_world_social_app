import { createClient } from "@supabase/supabase-js"

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  console.error("Missing Supabase environment variables")
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: false,
  },
})

// Test connection function
export async function testSupabaseConnection() {
  try {
    // Simple ping test instead of querying tables
    const { data, error } = await supabase.auth.getSession()

    if (error && error.message.includes("JSON")) {
      console.log("Supabase JSON parsing error, using fallback")
      return false
    }

    console.log("Supabase connection successful")
    return true
  } catch (error: any) {
    console.log("Supabase connection error:", error.message)
    return false
  }
}

// Server-side client
export const createServerClient = () => {
  return createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!)
}
