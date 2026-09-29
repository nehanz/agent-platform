// src/components/ChatWindow.jsx
import { useState } from "react";
import { sendChat } from "../api/client";

export default function ChatWindow({ onPendingApproval, onExecutionUpdate }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  const send = async () => {
    if (!input.trim() || busy) return;
    const userMsg = { role: "user", content: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setBusy(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res = await sendChat(userMsg.content, history);
      setMessages((m) => [...m, { role: "assistant", content: res.response, meta: res }]);
      onExecutionUpdate?.(res);
      if (res.status === "pending_approval") {
        onPendingApproval?.(res);
      }
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", content: `Error: ${e.message}` }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
              </svg>
            </div>
            <p className="text-sm text-slate-500 max-w-xs">
              Ask about an order, request a refund, or ask a policy question to get started.
            </p>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm ${
                m.role === "user"
                  ? "bg-indigo-600 text-white rounded-br-md shadow-indigo-900/30"
                  : "bg-slate-800/80 text-slate-200 border border-slate-700/40 rounded-bl-md"
              }`}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>
              {m.meta?.execution_id && (
                <div className="flex items-center gap-2 mt-2 pt-2 border-t border-white/10">
                  <span className="text-[10px] font-mono text-slate-400/80 bg-black/20 px-1.5 py-0.5 rounded">
                    exec: {m.meta.execution_id}
                  </span>
                  <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${
                    m.meta.status === "pending_approval"
                      ? "bg-amber-500/15 text-amber-400 border border-amber-500/20"
                      : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
                  }`}>
                    {m.meta.status}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}

        {busy && (
          <div className="flex justify-start">
            <div className="bg-slate-800/80 border border-slate-700/40 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-slate-800/60 bg-slate-900/50 backdrop-blur-sm p-4">
        <div className="flex gap-2.5 max-w-4xl mx-auto">
          <input
            className="flex-1 bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-sm text-slate-200 
                       placeholder-slate-500 focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30 
                       transition-all duration-200"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
            placeholder="Ask about an order, request a refund, or ask a policy question..."
            disabled={busy}
          />
          <button
            onClick={send}
            disabled={busy || !input.trim()}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed 
                       px-5 py-2.5 rounded-xl text-sm font-medium text-white shadow-lg shadow-indigo-900/30 
                       transition-all duration-200 flex items-center gap-2"
          >
            {busy ? (
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
              </svg>
            )}
            Send
          </button>
        </div>
      </div>
    </div>
  );
}