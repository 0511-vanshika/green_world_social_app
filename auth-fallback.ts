// Fallback authentication using localStorage for demo purposes
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

// In-memory storage for demo (in production, this would be a real database)
const users: User[] = [
  {
    id: "1",
    email: "test@example.com",
    username: "testuser",
    first_name: "Test",
    last_name: "User",
    created_at: new Date().toISOString(),
  },
  {
    id: "2",
    email: "jane.doe@example.com",
    username: "plantlover123",
    first_name: "Jane",
    last_name: "Doe",
    bio: "Urban gardener passionate about houseplants and sustainable gardening practices.",
    location: "Portland, OR",
    growing_zone: "8b",
    created_at: new Date().toISOString(),
  },
  {
    id: "3",
    email: "john.smith@example.com",
    username: "gardenguru",
    first_name: "John",
    last_name: "Smith",
    bio: "Professional landscaper with 15 years of experience in organic gardening.",
    location: "Austin, TX",
    growing_zone: "8a",
    created_at: new Date().toISOString(),
  },
  {
    id: "4",
    email: "sarah.green@example.com",
    username: "greenthumb",
    first_name: "Sarah",
    last_name: "Green",
    bio: "Succulent enthusiast and indoor plant collector. Love sharing growing tips!",
    location: "San Diego, CA",
    growing_zone: "10a",
    created_at: new Date().toISOString(),
  },
]

const userPasswords: Record<string, string> = {
  "test@example.com": simpleHash("test"),
  "jane.doe@example.com": simpleHash("password"),
  "john.smith@example.com": simpleHash("garden123"),
  "sarah.green@example.com": simpleHash("plants456"),
}

export async function createUser(userData: {
  email: string
  username: string
  firstName: string
  lastName: string
  password: string
}) {
  try {
    console.log("Creating user with fallback system:", userData.email)

    // Check if user already exists
    const existingUser = users.find(
      (u) =>
        u.email.toLowerCase() === userData.email.toLowerCase() ||
        u.username.toLowerCase() === userData.username.toLowerCase(),
    )

    if (existingUser) {
      throw new Error("Email or username already exists")
    }

    // Create new user
    const newUser: User = {
      id: (users.length + 1).toString(),
      email: userData.email.toLowerCase(),
      username: userData.username.toLowerCase(),
      first_name: userData.firstName,
      last_name: userData.lastName,
      created_at: new Date().toISOString(),
    }

    // Store user and password
    users.push(newUser)
    userPasswords[userData.email.toLowerCase()] = simpleHash(userData.password)

    console.log("User created successfully with fallback system")
    return newUser
  } catch (error) {
    console.error("Error in createUser (fallback):", error)
    throw error
  }
}

export async function authenticateUser(email: string, password: string) {
  try {
    console.log("Authenticating user with fallback system:", email)

    const user = users.find((u) => u.email.toLowerCase() === email.toLowerCase())

    if (!user) {
      console.log("User not found:", email)
      throw new Error("Invalid credentials")
    }

    const storedPasswordHash = userPasswords[email.toLowerCase()]
    if (!storedPasswordHash) {
      console.log("No password found for user:", email)
      throw new Error("Invalid credentials")
    }

    const isValid = verifySimpleHash(password, storedPasswordHash)
    if (!isValid) {
      console.log("Password verification failed")
      throw new Error("Invalid credentials")
    }

    console.log("Authentication successful with fallback system")
    return user
  } catch (error) {
    console.error("Error in authenticateUser (fallback):", error)
    throw error
  }
}

export async function getUserById(id: string) {
  try {
    const user = users.find((u) => u.id === id)
    if (!user) {
      throw new Error("User not found")
    }
    return user
  } catch (error) {
    console.error("Error in getUserById (fallback):", error)
    throw error
  }
}
