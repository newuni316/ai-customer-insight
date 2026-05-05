"use client"
import Link from "next/link"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import api from "@/lib/api"

export default function Navbar() {
  const router = useRouter()
  const [email, setEmail] = useState<string | null>(null)

  useEffect(() => {
    // 通过后端接口获取用户信息（而非客户端解析 JWT）
    api.get("/api/auth/me")
      .then(({ data }) => setEmail(data.email))
      .catch(() => setEmail(null))
  }, [])

  const logout = async () => {
    await api.delete("/api/auth/token") // 清除 httpOnly cookie
    setEmail(null)
    router.push("/")
  }

  return (
    <nav className="fixed top-0 w-full z-50 bg-[#0a0a0f]/80 backdrop-blur-xl border-b border-[#1e1e2e]">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-xl font-bold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
            AI Insight
          </span>
        </Link>
        <div className="flex items-center gap-4">
          {email ? (
            <>
              <Link href="/dashboard" className="btn-ghost text-sm">仪表盘</Link>
              <span className="text-gray-500 text-sm">{email}</span>
              <button onClick={logout} className="btn-ghost text-sm text-red-400">退出</button>
            </>
          ) : (
            <>
              <Link href="/login" className="btn-ghost text-sm">登录</Link>
              <Link href="/register" className="btn-primary text-sm !py-2 !px-4">注册</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
