import { type NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/session"

// Fallback storage for plant analyses
const plantAnalyses: any[] = []

export async function POST(request: NextRequest) {
  try {
    const session = await getSession()
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const data = await request.json()

    // Create analysis record
    const analysis = {
      id: (plantAnalyses.length + 1).toString(),
      user_id: session.user.id,
      image_url: data.image_url,
      plant_name: data.plantName,
      dehydration_level: data.dehydrationLevel,
      confidence_score: data.confidenceScore / 100,
      stress_level: data.stressLevel,
      stress_score: data.stressScore,
      sunlight_exposure: data.sunlightExposure,
      sunlight_warning: data.sunlightWarning,
      overall_health_score: data.overallHealthScore,
      recommendations: data.recommendations,
      watering_schedule: data.wateringSchedule,
      created_at: new Date().toISOString(),
    }

    plantAnalyses.push(analysis)

    console.log("Plant analysis saved successfully")
    return NextResponse.json({ success: true })
  } catch (error: any) {
    console.error("Error saving plant analysis:", error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const session = await getSession()
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const userAnalyses = plantAnalyses
      .filter((analysis) => analysis.user_id === session.user.id)
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

    return NextResponse.json(userAnalyses)
  } catch (error: any) {
    console.error("Error fetching plant analyses:", error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
