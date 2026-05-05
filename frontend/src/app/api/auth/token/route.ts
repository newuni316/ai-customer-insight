import { NextRequest, NextResponse } from "next/server"

// 设置 httpOnly cookie
export async function POST(request: NextRequest) {
  const { token } = await request.json()
  if (!token) {
    return NextResponse.json({ error: "token required" }, { status: 400 })
  }
  const response = NextResponse.json({ ok: true })
  response.cookies.set("token", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 86400, // 24h
  })
  return response
}

// 删除 cookie（退出登录）
export async function DELETE() {
  const response = NextResponse.json({ ok: true })
  response.cookies.delete("token")
  return response
}
