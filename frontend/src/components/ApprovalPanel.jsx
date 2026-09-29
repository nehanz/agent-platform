// src/components/ApprovalPanel.jsx
import { sendApproval } from "../api/client";

export default function ApprovalPanel({ pending, onResolved }) {
  if (!pending) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-6 text-center space-y-3">
        <div className="w-10 h-10 rounded-full bg-slate-800/50 border border-slate-700/40 flex items-center justify-center">
          <svg className="w-5 h-5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p className="text-sm font-medium text-slate-400">No pending approvals</p>
          <p className="text-xs text-slate-600 mt-1">Actions requiring review will appear here.</p>
        </div>
      </div>
    );
  }

  const { execution_id, pending_action } = pending;

  const decide = async (approved) => {
    const res = await sendApproval(execution_id, approved);
    onResolved?.(res);
  };

  return (
    <div className="p-5 space-y-4 h-full overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
      {/* Header */}
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-amber-500/15 border border-amber-500/25 flex items-center justify-center">
          <svg className="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
        </div>
        <span className="text-sm font-semibold text-amber-400 tracking-tight">Approval Required</span>
      </div>

      {/* Details card */}
      <div className="bg-slate-800/60 border border-slate-700/40 rounded-xl p-4 space-y-3 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Execution</span>
          <span className="font-mono text-xs text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
            {execution_id}
          </span>
        </div>

        <div className="h-px bg-slate-700/40" />

        <div>
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider block mb-1.5">Tool</span>
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            <span className="text-slate-200 font-medium">{pending_action.tool_name}</span>
          </div>
        </div>

        <div>
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider block mb-1.5">Arguments</span>
          <pre className="text-xs font-mono text-slate-300 bg-slate-900/70 border border-slate-700/30 rounded-lg p-3 overflow-x-auto leading-relaxed">
            {JSON.stringify(pending_action.tool_args, null, 2)}
          </pre>
        </div>

        <div>
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider block mb-1.5">Reason</span>
          <p className="text-slate-300 text-xs leading-relaxed bg-slate-900/50 rounded-lg p-3 border border-slate-700/30">
            {pending_action.reason}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-1">
        <button
          onClick={() => decide(true)}
          className="flex-1 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 
                     px-4 py-2.5 rounded-xl text-sm font-medium text-white 
                     shadow-lg shadow-emerald-900/30 transition-all duration-200 
                     flex items-center justify-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
          Approve
        </button>
        <button
          onClick={() => decide(false)}
          className="flex-1 bg-slate-700 hover:bg-red-600 active:bg-red-700 
                     px-4 py-2.5 rounded-xl text-sm font-medium text-slate-200 hover:text-white 
                     shadow-lg shadow-black/20 transition-all duration-200 
                     flex items-center justify-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
          Reject
        </button>
      </div>
    </div>
  );
}