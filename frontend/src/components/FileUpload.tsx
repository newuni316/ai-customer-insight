"use client"
import { useState, useCallback } from "react"
import api from "@/lib/api"

interface Props {
  onSuccess?: () => void
}

export default function FileUpload({ onSuccess }: Props) {
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  const upload = useCallback(async (file: File) => {
    setUploading(true)
    setMessage(null)
    const form = new FormData()
    form.append("file", file)
    try {
      const { data } = await api.post("/api/feedback/upload-csv", form)
      setMessage({ type: "success", text: data.message })
      onSuccess?.()
    } catch (err: any) {
      setMessage({ type: "error", text: err.response?.data?.detail || "上传失败" })
    } finally {
      setUploading(false)
    }
  }, [onSuccess])

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) upload(file)
  }

  return (
    <div
      className={`card border-2 border-dashed transition-all cursor-pointer text-center py-10
        ${dragOver ? "border-primary-500 bg-primary-500/5" : "border-[#2a2a3a] hover:border-primary-500/50"}`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => document.getElementById("csv-input")?.click()}
    >
      <input id="csv-input" type="file" accept=".csv" className="hidden"
        onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
      <div className="text-4xl mb-3">📂</div>
      <p className="text-gray-300 font-medium">
        {uploading ? "上传中..." : "拖拽 CSV 文件到此处，或点击选择"}
      </p>
      <p className="text-gray-600 text-sm mt-2">支持 .csv 格式（列名: date, source, content）</p>
      {message && (
        <p className={`mt-4 text-sm ${message.type === "success" ? "text-green-400" : "text-red-400"}`}>
          {message.text}
        </p>
      )}
    </div>
  )
}
