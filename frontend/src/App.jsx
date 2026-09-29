// src/App.jsx
import { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import ApprovalPanel from "./components/ApprovalPanel";
import AuditViewer from "./components/AuditViewer";

export default function App() {
  const [tenant, setTenant] = useState(localStorage.getItem("tenant_id") || "tenantA");
  const [pending, setPending] = useState(null);
  const [lastExecution, setLastExecution] = useState(null);

  const switchTenant = (t) => {
    setTenant(t);
    localStorage.setItem("tenant_id", t);
  };

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-slate-100 antialiased">
      {/* Header */}
      <header className="border-b border-slate-800/60 bg-slate-900/70 backdrop-blur-sm px-6 py-3 flex items-center justify-between shadow-lg shadow-black/20">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-indigo-500 shadow-lg shadow-indigo-500/50" />
          <span className="font-semibold tracking-tight text-slate-100">Agent Platform</span>
          <span className="text-xs font-medium text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full border border-indigo-500/20">
            MVP
          </span>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-slate-500 text-xs uppercase tracking-wider font-medium">Tenant</span>
          <select
            value={tenant}
            onChange={(e) => switchTenant(e.target.value)}
            className="bg-slate-800/80 border border-slate-700/50 rounded-lg px-3 py-1.5 text-sm text-slate-200 
                       focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30 
                       transition-all duration-200 cursor-pointer hover:border-slate-600"
          >
            <option value="tenantA">tenantA</option>
            <option value="tenantB">tenantB</option>
          </select>
        </div>
      </header>

      {/* Main layout */}
      <div className="flex-1 grid grid-cols-3 overflow-hidden">
        <div className="col-span-2 border-r border-slate-800/60 overflow-hidden bg-slate-900/30">
          <ChatWindow
            onPendingApproval={setPending}
            onExecutionUpdate={(r) => setLastExecution(r.execution_id)}
          />
        </div>
        <div className="grid grid-rows-2 overflow-hidden bg-slate-900/20">
          <div className="border-b border-slate-800/60 overflow-hidden">
            <ApprovalPanel pending={pending} onResolved={() => setPending(null)} />
          </div>
          <div className="overflow-hidden">
            <AuditViewer activeExecutionId={lastExecution} />
          </div>
        </div>
      </div>
    </div>
  );
}