"use client";

import React, { useEffect, useState, useRef, FormEvent } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type ChatResponse = {
  session_id: string;
  reply: string;
  history: Message[];
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function HomePage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [healthStatus, setHealthStatus] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const chatBottomRef = useRef<HTMLDivElement | null>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // Ping backend health on load
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/health`);
        if (!res.ok) throw new Error("Health check failed");
        const data = await res.json();
        if (data.status === "ok") {
          setHealthStatus("Online");
        } else {
          setHealthStatus("Degraded");
        }
      } catch {
        setHealthStatus("Offline");
      }
    };
    checkHealth();
  }, []);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isSending) return;

    const newUserMessage: Message = { role: "user", content: trimmed };
    const optimisticMessages = [...messages, newUserMessage];

    setMessages(optimisticMessages);
    setInput("");
    setIsSending(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: trimmed,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Chat error: ${res.status} - ${text}`);
      }

      const data: ChatResponse = await res.json();
      setSessionId(data.session_id);
      setMessages(data.history);
    } catch (err: any) {
      console.error(err);
      setMessages([
        ...optimisticMessages,
        {
          role: "assistant",
          content:
            "GhostSage hit an error talking to the backend. Check the FastAPI server logs.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    setUploadStatus(null);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Upload failed: ${res.status} - ${text}`);
      }

      const data = await res.json();
      if (data.status === "ok") {
        setUploadStatus(
          `Indexed ${data.chunks_indexed} chunks from "${data.filename}". You can now ask questions about it.`
        );
      } else if (data.status === "no_content") {
        setUploadStatus(
          `Uploaded "${data.filename}", but no usable text was extracted.`
        );
      } else {
        setUploadStatus(`Upload completed with status: ${data.status}`);
      }
    } catch (err: any) {
      console.error(err);
      setUploadStatus("Upload failed. Check the backend logs.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    void handleUpload(file);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      {/* Sidebar */}
      <aside className="w-full max-w-sm border-r border-slate-800 bg-slate-900/60 px-4 py-4 flex flex-col gap-4">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold tracking-tight">
              GhostSage <span className="text-xs text-slate-400">v0.3</span>
            </h1>
            <p className="text-xs text-slate-400">
              Personal AI assistant – FastAPI + RAG + Next.js
            </p>
          </div>
          <div
            className={`px-2 py-1 rounded-full text-[10px] font-semibold ${
              healthStatus === "Online"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                : healthStatus === "Offline"
                ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                : "bg-slate-700/60 text-slate-300 border border-slate-600"
            }`}
          >
            API: {healthStatus ?? "Checking..."}
          </div>
        </header>

        <section className="space-y-2">
          <h2 className="text-xs font-semibold text-slate-300 uppercase tracking-[0.16em]">
            Upload document / code
          </h2>
          <p className="text-xs text-slate-400">
            Upload a PDF, text file, or bot script. GhostSage will index it and
            use it when you ask questions.
          </p>
          <label className="flex items-center justify-center rounded-lg border border-dashed border-slate-700 bg-slate-900/60 px-3 py-5 text-xs text-slate-300 hover:border-sky-500 cursor-pointer transition-colors">
            <div className="text-center">
              <div className="mb-1 font-medium text-slate-100">
                Click to upload
              </div>
              <div className="text-[11px] text-slate-400">
                .txt, .pdf, .py, .md · Max a few MB
              </div>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={handleFileChange}
              disabled={uploading}
            />
          </label>
          {uploading && (
            <p className="text-[11px] text-sky-300">
              Uploading & indexing document…
            </p>
          )}
          {uploadStatus && (
            <p className="text-[11px] text-slate-300 whitespace-pre-line">
              {uploadStatus}
            </p>
          )}
        </section>

        <section className="mt-2 space-y-2">
          <h2 className="text-xs font-semibold text-slate-300 uppercase tracking-[0.16em]">
            Hints
          </h2>
          <ul className="text-[11px] text-slate-400 list-disc list-inside space-y-1">
            <li>“Summarize the uploaded Elliott Wave 30m bot.”</li>
            <li>“Scan the uploaded bot for bugs and risky assumptions.”</li>
            <li>“Summarize this URL: https://example.com/article”</li>
          </ul>
        </section>

        <footer className="mt-auto pt-3 border-t border-slate-800 text-[11px] text-slate-500">
          Built by{" "}
          <a
            href="mailto:fourthe4th@gmail.com"
            className="text-sky-400 hover:underline"
          >
            four
          </a>{" "}
          · Backend: FastAPI · Frontend: Next.js
        </footer>
      </aside>

      {/* Main chat panel */}
      <main className="flex-1 flex flex-col max-h-screen">
        <div className="flex-1 overflow-y-auto px-4 py-4 md:px-8 md:py-6">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="max-w-md text-center space-y-3">
                <h2 className="text-xl font-semibold text-slate-100">
                  Welcome to GhostSage
                </h2>
                <p className="text-sm text-slate-400">
                  Start chatting, upload a bot or document, or paste a URL.
                  GhostSage will combine conversation, RAG, and web scraping to
                  answer.
                </p>
                <p className="text-xs text-slate-500">
                  Example: “Scan the uploaded Elliott Wave bot for bugs, risky
                  assumptions, and weak spots.”
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex ${
                    m.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm whitespace-pre-wrap ${
                      m.role === "user"
                        ? "bg-sky-600 text-white rounded-br-sm"
                        : "bg-slate-800 text-slate-100 rounded-bl-sm"
                    }`}
                  >
                    {m.content}
                  </div>
                </div>
              ))}
              <div ref={chatBottomRef} />
            </div>
          )}
        </div>

        {/* Input bar */}
        <form
          onSubmit={handleSend}
          className="border-t border-slate-800 bg-slate-900/80 px-3 py-3 md:px-6"
        >
          <div className="flex items-end gap-2">
            <textarea
              className="flex-1 resize-none rounded-xl border border-slate-700 bg-slate-900/80 px-3 py-2 text-sm text-slate-100 shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 max-h-32 min-h-[42px]"
              placeholder="Ask GhostSage anything…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isSending}
            />
            <button
              type="submit"
              disabled={isSending || !input.trim()}
              className="inline-flex items-center justify-center rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-sky-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSending ? "Sending…" : "Send"}
            </button>
          </div>
          {sessionId && (
            <p className="mt-1 text-[10px] text-slate-500">
              Session: <span className="font-mono">{sessionId}</span>
            </p>
          )}
        </form>
      </main>
    </div>
  );
}
