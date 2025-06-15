import { Leaf } from "lucide-react"
import Link from "next/link"

export function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2">
      <div className="relative h-10 w-10 overflow-hidden rounded-full bg-gradient-to-br from-green-400 to-green-600 p-2 shadow-lg">
        <Leaf className="h-full w-full text-white animate-pulse-slow" />
      </div>
      <div className="flex flex-col">
        <span className="text-xl font-bold tracking-tight text-green-600 dark:text-green-400">GreenVerse</span>
        <span className="text-xs text-green-500 dark:text-green-500">Plant Social Network</span>
      </div>
    </Link>
  )
}
