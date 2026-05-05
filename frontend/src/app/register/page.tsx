"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import api from "@/lib/api"

export default function RegisterPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirm, setConfirm] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    if (password !== confirm) { setError("两次密码不一致"); return }
    setLoading(true)
    try {
      await api.post("/api/auth/register", { email, password })
      router.push("/login")
    } catch (err: any) {
      setError(err.response?.data?.detail || "注册失败")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-8">注册</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input className="input" type="email" placeholder="邮箱" value={email} onChange={e => setEmail(e.target.value)} required />
          <input className="input" type="password" placeholder="密码" value={password} onChange={e => setPassword(e.target.value)} required />
          <input className="input" type="password" placeholder="确认密码" value={confirm} onChange={e => setConfirm(e.target.value)} required />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button className="btn-primary w-full" type="submit" disabled={loading}>
            {loading ? "注册中..." : "注册"}
          </button>
        </form>
        <p className="text-center text-gray-500 text-sm mt-6">
          已有账号？ <Link href="/login" className="text-primary-400 hover:underline">登录</Link>
        </p>
      </div>
    </div>
  )
}
