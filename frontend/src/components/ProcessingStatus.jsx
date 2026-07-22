import React from "react";
import { useTimer } from "../context/TimerContext";

function ProcessingStatus() {
  const {
    isRunning,
    status,
    formattedTime,
  } = useTimer();

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-6 shadow-sm">

      <div className="flex items-center justify-between">

        <div>
          <h3 className="text-sm font-bold uppercase tracking-wide text-slate-700">
            Processing Status
          </h3>

          <p className="text-xs text-slate-500 mt-1">
            Current AI request status
          </p>
        </div>

        <div className="text-right">

          <div
            className={`font-semibold ${
              isRunning
                ? "text-amber-600"
                : "text-green-600"
            }`}
          >
            {isRunning ? "🟡 Processing..." : `🟢 ${status}`}
          </div>

          <div className="mt-2 text-lg font-mono font-bold text-slate-800">
            ⏱ {formattedTime}
          </div>

        </div>

      </div>

    </div>
  );
}

export default ProcessingStatus;