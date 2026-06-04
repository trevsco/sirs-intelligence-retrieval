/**
 * IEEEComplianceReport.jsx
 * -------------------------
 * React component to display IEEE Compliance Check results in the SIRS dashboard.
 *
 * Props:
 *   report  — the compliance_report object from /query or /compliance/check API response
 *   loading — boolean, shows skeleton while compliance check is running
 *
 * Usage in your existing Dashboard/QueryResult component:
 *   import IEEEComplianceReport from './IEEEComplianceReport';
 *   <IEEEComplianceReport report={queryResult.compliance_report} loading={isLoading} />
 */

import { useState } from "react";

const STANDARD_COLORS = {
  "IEEE 12207": { bg: "#1a2744", accent: "#4da6ff", label: "Life Cycle" },
  "IEEE 830":   { bg: "#1a2e1a", accent: "#4caf82", label: "Requirements" },
  "IEEE 829":   { bg: "#2e2414", accent: "#f0a045", label: "Testing" },
  "IEEE 1016":  { bg: "#2a1a2e", accent: "#b07aff", label: "Design" },
  "IEEE 730":   { bg: "#1a2a2e", accent: "#4dd9dc", label: "Quality" },
};

function ScoreBar({ score, accent }) {
  return (
    <div style={{
      height: 6,
      borderRadius: 3,
      background: "rgba(255,255,255,0.08)",
      overflow: "hidden",
      marginTop: 8,
    }}>
      <div style={{
        height: "100%",
        width: `${score}%`,
        borderRadius: 3,
        background: accent,
        transition: "width 0.6s ease",
      }} />
    </div>
  );
}

function CheckList({ checks, failures }) {
  return (
    <div style={{ marginTop: 12 }}>
      {Object.entries(checks).map(([key, passed]) => (
        <div key={key} style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "3px 0",
          fontSize: 12,
          color: passed ? "rgba(255,255,255,0.75)" : "rgba(255,255,255,0.35)",
        }}>
          <span style={{
            width: 16,
            height: 16,
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 10,
            flexShrink: 0,
            background: passed ? "rgba(78,200,140,0.2)" : "rgba(255,80,80,0.15)",
            color: passed ? "#4ec88c" : "#ff5a5a",
            fontWeight: 600,
          }}>
            {passed ? "✓" : "✗"}
          </span>
          {key.replace(/_/g, " ")}
        </div>
      ))}
    </div>
  );
}

function StandardCard({ standard, defaultOpen }) {
  const [open, setOpen] = useState(defaultOpen || false);
  const colors = STANDARD_COLORS[standard.id] || { bg: "#1a1f2e", accent: "#4da6ff", label: "" };
  const passed = standard.passed;

  return (
    <div style={{
      background: colors.bg,
      border: `1px solid ${passed ? colors.accent + "44" : "rgba(255,80,80,0.25)"}`,
      borderRadius: 10,
      overflow: "hidden",
      transition: "border-color 0.2s",
    }}>
      {/* Card header */}
      <div
        onClick={() => setOpen(!open)}
        style={{
          padding: "12px 16px",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          gap: 12,
          userSelect: "none",
        }}
      >
        {/* Status dot */}
        <div style={{
          width: 10,
          height: 10,
          borderRadius: "50%",
          background: passed ? "#4ec88c" : "#ff5a5a",
          flexShrink: 0,
          boxShadow: passed ? "0 0 6px #4ec88c88" : "0 0 6px #ff5a5a88",
        }} />

        {/* Title area */}
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: colors.accent }}>
              {standard.id}
            </span>
            <span style={{
              fontSize: 11,
              background: colors.accent + "22",
              color: colors.accent,
              borderRadius: 4,
              padding: "1px 6px",
            }}>
              {colors.label}
            </span>
          </div>
          <div style={{ fontSize: 11, color: "rgba(255,255,255,0.45)", marginTop: 1 }}>
            {standard.name}
          </div>
        </div>

        {/* Score badge */}
        <div style={{ textAlign: "right", minWidth: 48 }}>
          <div style={{
            fontSize: 18,
            fontWeight: 700,
            color: passed ? "#4ec88c" : "#ff7070",
            fontVariantNumeric: "tabular-nums",
          }}>
            {standard.score_pct}%
          </div>
        </div>

        {/* Chevron */}
        <div style={{
          color: "rgba(255,255,255,0.3)",
          fontSize: 12,
          transform: open ? "rotate(180deg)" : "rotate(0deg)",
          transition: "transform 0.2s",
        }}>▼</div>
      </div>

      {/* Score bar always visible */}
      <div style={{ padding: "0 16px 8px" }}>
        <ScoreBar score={standard.score_pct} accent={colors.accent} />
      </div>

      {/* Expandable detail */}
      {open && (
        <div style={{ padding: "0 16px 16px", borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <CheckList checks={standard.checks} failures={standard.failures} />

          {standard.suggestions && standard.suggestions.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                Suggestions
              </div>
              {standard.suggestions.map((s, i) => (
                <div key={i} style={{
                  fontSize: 12,
                  color: "rgba(255,220,100,0.8)",
                  padding: "4px 0 4px 10px",
                  borderLeft: "2px solid rgba(255,200,50,0.3)",
                  marginBottom: 4,
                  lineHeight: 1.5,
                }}>
                  {s}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SkeletonCard() {
  return (
    <div style={{
      background: "#151c30",
      border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 10,
      padding: "14px 16px",
      animation: "pulse 1.5s ease-in-out infinite",
    }}>
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <div style={{ width: 10, height: 10, borderRadius: "50%", background: "rgba(255,255,255,0.1)" }} />
        <div style={{ flex: 1 }}>
          <div style={{ height: 13, width: "40%", background: "rgba(255,255,255,0.08)", borderRadius: 4, marginBottom: 6 }} />
          <div style={{ height: 11, width: "65%", background: "rgba(255,255,255,0.05)", borderRadius: 4 }} />
        </div>
        <div style={{ height: 18, width: 40, background: "rgba(255,255,255,0.08)", borderRadius: 4 }} />
      </div>
      <div style={{ height: 6, borderRadius: 3, background: "rgba(255,255,255,0.06)", marginTop: 12 }} />
    </div>
  );
}

export default function IEEEComplianceReport({ report, loading }) {
  if (loading) {
    return (
      <div style={{ marginTop: 24 }}>
        <div style={{ fontSize: 13, color: "rgba(255,255,255,0.4)", marginBottom: 12, letterSpacing: "0.05em" }}>
          IEEE COMPLIANCE CHECK
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {[1, 2, 3, 4, 5].map(i => <SkeletonCard key={i} />)}
        </div>
        <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }`}</style>
      </div>
    );
  }

  if (!report) return null;

  const passedCount = report.standards.filter(s => s.passed).length;
  const isCompliant = report.overall_passed;

  return (
    <div style={{ marginTop: 24 }}>
      {/* Section header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <div style={{ fontSize: 13, color: "rgba(255,255,255,0.4)", letterSpacing: "0.05em" }}>
          IEEE COMPLIANCE CHECK
        </div>
        <div style={{ fontSize: 11, color: "rgba(255,255,255,0.3)" }}>
          {report.timestamp?.slice(0, 19).replace("T", " ")}
        </div>
      </div>

      {/* Overall verdict banner */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: 16,
        padding: "14px 18px",
        borderRadius: 10,
        background: isCompliant ? "rgba(78,200,140,0.08)" : "rgba(255,90,90,0.08)",
        border: `1px solid ${isCompliant ? "rgba(78,200,140,0.3)" : "rgba(255,90,90,0.25)"}`,
        marginBottom: 12,
      }}>
        <div style={{
          fontSize: 28,
          fontWeight: 800,
          color: isCompliant ? "#4ec88c" : "#ff7070",
          fontVariantNumeric: "tabular-nums",
          lineHeight: 1,
        }}>
          {report.overall_score_pct}%
        </div>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: 14,
            fontWeight: 600,
            color: isCompliant ? "#4ec88c" : "#ff7070",
          }}>
            {isCompliant ? "Fully Compliant" : "Needs Improvement"}
          </div>
          <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", marginTop: 2 }}>
            {passedCount} of 5 IEEE standards passed
          </div>
        </div>
        {/* Mini bar chart of 5 standards */}
        <div style={{ display: "flex", gap: 4, alignItems: "flex-end", height: 32 }}>
          {report.standards.map((s) => (
            <div
              key={s.id}
              title={`${s.id}: ${s.score_pct}%`}
              style={{
                width: 10,
                height: `${Math.max(s.score_pct / 100 * 32, 4)}px`,
                borderRadius: 2,
                background: s.passed
                  ? STANDARD_COLORS[s.id]?.accent || "#4ec88c"
                  : "rgba(255,90,90,0.5)",
              }}
            />
          ))}
        </div>
      </div>

      {/* Per-standard cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {report.standards.map((standard, i) => (
          <StandardCard
            key={standard.id}
            standard={standard}
            defaultOpen={!standard.passed}   /* auto-open failing ones */
          />
        ))}
      </div>

      {/* Footer */}
      <div style={{ marginTop: 10, fontSize: 11, color: "rgba(255,255,255,0.2)", textAlign: "right" }}>
        SIRS · IEEE 12207 · 830 · 829 · 1016 · 730
      </div>
    </div>
  );
}