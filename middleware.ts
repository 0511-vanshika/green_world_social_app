import { type NextRequest, NextResponse } from "next/server"
import { getSession } from "./lib/session"

const protectedRoutes = ["/dashboard", "/community", "/dehydration-detector", "/marketplace", "/profile"]
const authRoutes = ["/auth/login", "/auth/register"]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const session = await getSession()

  // Redirect to dashboard if user is authenticated and tries to access auth pages
  if (authRoutes.includes(pathname) && session) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  // Redirect to login if user is not authenticated and tries to access protected routes
  if (protectedRoutes.some((route) => pathname.startsWith(route)) && !session) {
    return NextResponse.redirect(new URL("/auth/login", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
