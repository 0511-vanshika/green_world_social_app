import { Button } from "@/components/ui/button"
import { ModeToggle } from "@/components/mode-toggle"
import { Logo } from "@/components/logo"
import Link from "next/link"
import { Leaf, Users, Cloud, ShoppingBag, MessageSquare, Zap, ChevronRight } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-md">
        <div className="container flex h-16 items-center justify-between">
          <Logo />

          <nav className="hidden md:flex items-center gap-6">
            <Link href="#features" className="text-sm font-medium hover:text-primary">
              Features
            </Link>
            <Link href="#community" className="text-sm font-medium hover:text-primary">
              Community
            </Link>
            <Link href="#ai" className="text-sm font-medium hover:text-primary">
              AI Tools
            </Link>
            <Link href="#marketplace" className="text-sm font-medium hover:text-primary">
              Marketplace
            </Link>
          </nav>

          <div className="flex items-center gap-4">
            <ModeToggle />
            <Link href="/auth/login">
              <Button variant="outline">Login</Button>
            </Link>
            <Link href="/auth/register" className="hidden md:block">
              <Button>Sign Up</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-20 md:py-32 overflow-hidden">
          <div className="container flex flex-col items-center text-center">
            <div className="absolute inset-0 -z-10">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,200,100,0.1),transparent_70%)]" />
            </div>

            <div className="max-w-3xl space-y-6 animate-fade-in">
              <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
                The Social Network for
                <span className="text-primary"> Plant Enthusiasts</span>
              </h1>
              <p className="text-xl text-muted-foreground">
                Connect with fellow gardeners, identify plants with AI, track your garden's progress, and discover the
                perfect crops for your climate.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center pt-6">
                <Link href="/auth/register">
                  <Button size="lg" className="w-full sm:w-auto">
                    Get Started
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="#features">
                  <Button size="lg" variant="outline" className="w-full sm:w-auto">
                    Explore Features
                  </Button>
                </Link>
              </div>
            </div>

            <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-5xl">
              <div className="flex flex-col items-center p-6 rounded-lg bg-card shadow-lg animate-float">
                <div className="h-12 w-12 rounded-full bg-primary/20 flex items-center justify-center mb-4">
                  <Leaf className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-medium mb-2">AI Plant Identification</h3>
                <p className="text-sm text-muted-foreground text-center">
                  Instantly identify any plant with our advanced AI technology
                </p>
              </div>

              <div
                className="flex flex-col items-center p-6 rounded-lg bg-card shadow-lg animate-float"
                style={{ animationDelay: "0.2s" }}
              >
                <div className="h-12 w-12 rounded-full bg-secondary/20 flex items-center justify-center mb-4">
                  <Users className="h-6 w-6 text-secondary" />
                </div>
                <h3 className="text-lg font-medium mb-2">Community Garden</h3>
                <p className="text-sm text-muted-foreground text-center">
                  Share your garden progress and connect with plant enthusiasts worldwide
                </p>
              </div>

              <div
                className="flex flex-col items-center p-6 rounded-lg bg-card shadow-lg animate-float"
                style={{ animationDelay: "0.4s" }}
              >
                <div className="h-12 w-12 rounded-full bg-accent/20 flex items-center justify-center mb-4">
                  <Cloud className="h-6 w-6 text-accent" />
                </div>
                <h3 className="text-lg font-medium mb-2">Weather-Based Recommendations</h3>
                <p className="text-sm text-muted-foreground text-center">
                  Get personalized crop recommendations based on your local climate
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20 bg-muted/50">
          <div className="container">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold mb-4">Powerful Features for Plant Lovers</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                GreenVerse combines social networking with advanced gardening tools to create the ultimate platform for
                plant enthusiasts
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div className="bg-card p-6 rounded-lg shadow-md animate-slide-up" style={{ animationDelay: "0.1s" }}>
                <Leaf className="h-10 w-10 text-primary mb-4" />
                <h3 className="text-xl font-medium mb-2">AI Plant Identification</h3>
                <p className="text-muted-foreground">
                  Take a photo of any plant and our AI will instantly identify it, providing care tips and growing
                  information.
                </p>
              </div>

              <div className="bg-card p-6 rounded-lg shadow-md animate-slide-up" style={{ animationDelay: "0.2s" }}>
                <Users className="h-10 w-10 text-primary mb-4" />
                <h3 className="text-xl font-medium mb-2">Social Garden Sharing</h3>
                <p className="text-muted-foreground">
                  Share photos of your garden, follow other gardeners, and get inspired by beautiful plant collections
                  worldwide.
                </p>
              </div>

              <div className="bg-card p-6 rounded-lg shadow-md animate-slide-up" style={{ animationDelay: "0.3s" }}>
                <Cloud className="h-10 w-10 text-primary mb-4" />
                <h3 className="text-xl font-medium mb-2">Climate-Based Recommendations</h3>
                <p className="text-muted-foreground">
                  Our system analyzes your local weather patterns to recommend the perfect crops for your specific
                  climate zone.
                </p>
              </div>

              <div className="bg-card p-6 rounded-lg shadow-md animate-slide-up" style={{ animationDelay: "0.4s" }}>
                <ShoppingBag className="h-10 w-10 text-primary mb-4" />
                <h3 className="text-xl font-medium mb-2">Gardening Marketplace</h3>
                <p className="text-muted-foreground">
                  Shop for seeds, tools, and gardening supplies from verified vendors, with reviews from fellow
                  gardeners.
                </p>
              </div>

              <div className="bg-card p-6 rounded-lg shadow-md animate-slide-up" style={{ animationDelay: "0.5s" }}>
                <MessageSquare className="h-10 w-10 text-primary mb-4" />
                <h3 className="text-xl font-medium mb-2">Expert Community</h3>
                <p className="text-muted-foreground">
                  Ask questions and get advice from experienced gardeners and horticulture experts in our active
                  community.
                </p>
              </div>

              <div className="bg-card p-6 rounded-lg shadow-md animate-slide-up" style={{ animationDelay: "0.6s" }}>
                <Zap className="h-10 w-10 text-primary mb-4" />
                <h3 className="text-xl font-medium mb-2">Garden Planning Tools</h3>
                <p className="text-muted-foreground">
                  Design your garden layout, track planting schedules, and receive maintenance reminders for your
                  plants.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20">
          <div className="container">
            <div className="rounded-2xl bg-gradient-to-r from-primary/20 to-secondary/20 p-8 md:p-12 shadow-lg">
              <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="max-w-md">
                  <h2 className="text-3xl font-bold mb-4">Ready to grow with us?</h2>
                  <p className="text-muted-foreground mb-6">
                    Join thousands of plant enthusiasts already using GreenVerse to grow better, connect with
                    like-minded gardeners, and learn from experts.
                  </p>
                  <Link href="/auth/register">
                    <Button size="lg">
                      Get Started for Free
                      <ChevronRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </div>

                <div className="relative w-full max-w-sm aspect-square">
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/30 to-secondary/30 rounded-full animate-pulse-slow" />
                  <div
                    className="absolute inset-4 bg-gradient-to-tr from-primary/40 to-secondary/40 rounded-full animate-pulse-slow"
                    style={{ animationDelay: "0.5s" }}
                  />
                  <div
                    className="absolute inset-8 bg-gradient-to-bl from-primary/50 to-secondary/50 rounded-full animate-pulse-slow"
                    style={{ animationDelay: "1s" }}
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Leaf className="h-20 w-20 text-primary-foreground" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t py-12 bg-muted/30">
        <div className="container">
          <div className="flex flex-col md:flex-row justify-between gap-8">
            <div className="space-y-4 max-w-xs">
              <Logo />
              <p className="text-sm text-muted-foreground">
                Connecting plant enthusiasts worldwide through our social platform for gardeners of all experience
                levels.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
              <div className="space-y-4">
                <h4 className="text-sm font-medium">Platform</h4>
                <ul className="space-y-2 text-sm">
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      Features
                    </Link>
                  </li>
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      Community
                    </Link>
                  </li>
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      Marketplace
                    </Link>
                  </li>
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      AI Tools
                    </Link>
                  </li>
                </ul>
              </div>

              <div className="space-y-4">
                <h4 className="text-sm font-medium">Company</h4>
                <ul className="space-y-2 text-sm">
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      About
                    </Link>
                  </li>
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      Blog
                    </Link>
                  </li>
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      Careers
                    </Link>
                  </li>
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      Contact
                    </Link>
                  </li>
                </ul>
              </div>

              <div className="space-y-4">
                <h4 className="text-sm font-medium">Legal</h4>
                <ul className="space-y-2 text-sm">
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      Privacy Policy
                    </Link>
                  </li>
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      Terms of Service
                    </Link>
                  </li>
                  <li>
                    <Link href="#" className="text-muted-foreground hover:text-foreground">
                      Cookie Policy
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t text-center text-sm text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} GreenVerse. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
