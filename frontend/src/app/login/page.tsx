"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import api from "@/lib/api"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      // 1. 获取 JWT
      const { data } = await api.post("/api/auth/login", { email, password })
      // 2. 存入 httpOnly cookie（而非 localStorage）
      await api.post("/api/auth/token", { token: data.access_token })
      router.push("/dashboard")
    } catch (err: any) {
      setError(err.response?.data?.detail || "登录失败")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-8">登录</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input className="input" type="email" placeholder="邮箱" value={email} onChange={e => setEmail(e.target.value)} required />
          <input className="input" type="password" placeholder="密码" value={password} onChange={e => setPassword(e.target.value)} required />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button className="btn-primary w-full" type="submit" disabled={loading}>
            {loading ? "登录中..." : "登录"}
          </button>
        </form>
        <p className="text-center text-gray-500 text-sm mt-6">
          没有账号？ <Link href="/register" className="text-primary-400 hover:underline">注册</Link>
        </p>
      </div>
    </div>
  )
}
