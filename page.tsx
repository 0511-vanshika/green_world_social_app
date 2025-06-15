import { Navbar } from "@/components/navbar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Settings, Cog } from "lucide-react"

export default function SettingsPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 container py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8 animate-fade-in">
            <h1 className="text-3xl font-bold mb-2">Settings</h1>
            <p className="text-muted-foreground">Customize your GreenVerse experience</p>
          </div>

          <Card className="animate-slide-up">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-6 w-6" />
                Application Settings
              </CardTitle>
              <CardDescription>Settings panel is under development</CardDescription>
            </CardHeader>
            <CardContent className="text-center py-12">
              <div className="space-y-4">
                <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                  <Cog className="h-10 w-10 text-primary" />
                </div>
                <div>
                  <h3 className="text-lg font-medium mb-2">Settings Panel</h3>
                  <p className="text-muted-foreground max-w-md mx-auto">
                    Soon you'll be able to customize notifications, privacy settings, and app preferences.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
