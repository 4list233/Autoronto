import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import { useFadeIn, useScaleIn, useSlideIn, useStagger } from "../utils/animations";

const TableCard: React.FC<{ name: string; fields: string[]; color: string; delay: number }> = ({ name, fields, color, delay }) => {
  const style = useScaleIn(delay);
  return (
    <div style={{ background: "rgba(255,255,255,0.04)", borderRadius: 12, overflow: "hidden", minWidth: 260, ...style }}>
      <div style={{ background: color, padding: "10px 16px", fontWeight: 700, fontSize: 16, fontFamily: "monospace" }}>{name}</div>
      <div style={{ padding: "8px 16px" }}>
        {fields.map((field, i) => {
          const fieldFade = useFadeIn(delay + 5 + i * 4);
          return (
            <div key={i} style={{ fontSize: 13, fontFamily: "monospace", padding: "4px 0", borderBottom: i < fields.length - 1 ? "1px solid rgba(255,255,255,0.06)" : "none", color: "#8899A6", opacity: fieldFade }}>{field}</div>
          );
        })}
      </div>
    </div>
  );
};

const AppendixDatabaseSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleStyle = useSlideIn(0, "left");

  const tables = [
    { name: "users", fields: ["id (PK)", "car_id", "name", "email", "phone", "created_at", "password_hash"], color: theme.colors.accent },
    { name: "payment_history", fields: ["id (PK)", "user_id (FK → users)", "date", "payment_token_hash", "amount", "currency"], color: theme.colors.accentGreen },
    { name: "parking_waiting", fields: ["id (PK)", "car_id", "payment_hash"], color: theme.colors.accentOrange },
    { name: "real_time_parking", fields: ["id (PK)", "name", "address", "live_count", "capacity"], color: theme.colors.highlight },
  ];

  const mlFade = useFadeIn(60);
  const lineProgress = spring({ frame: frame - 40, fps, config: { damping: 20, stiffness: 80 } });

  return (
    <AbsoluteFill style={slideStyle}>
      <div style={{ width: "100%", maxWidth: 1400, display: "flex", flexDirection: "column" as const, gap: 24 }}>
        <h1 style={{ fontSize: 44, fontWeight: 800, margin: 0, ...titleStyle }}>
          Appendix D: <span style={{ color: theme.colors.accent }}>Database & System Design</span>
        </h1>

        <div style={{ display: "flex", gap: 16, flexWrap: "wrap" as const, justifyContent: "center" }}>
          {tables.map((table, i) => (
            <TableCard key={i} name={table.name} fields={table.fields} color={table.color} delay={useStagger(i, 10, 10)} />
          ))}
        </div>

        <div style={{ display: "flex", justifyContent: "center", gap: 20, opacity: interpolate(lineProgress, [0, 1], [0, 1]) }}>
          <div style={{ fontSize: 14, fontFamily: "monospace", color: "#8899A6", background: "rgba(255,255,255,0.04)", padding: "8px 16px", borderRadius: 8 }}>
            payment_history.user_id → users.id
          </div>
          <div style={{ fontSize: 14, fontFamily: "monospace", color: "#8899A6", background: "rgba(255,255,255,0.04)", padding: "8px 16px", borderRadius: 8 }}>
            payment_history.payment_token_hash → parking_waiting.payment_hash
          </div>
        </div>

        <div style={{ background: "rgba(255, 215, 0, 0.06)", border: `1px solid ${theme.colors.highlight}`, borderRadius: 12, padding: "16px 24px", opacity: mlFade }}>
          <h3 style={{ fontSize: 20, fontWeight: 700, margin: "0 0 10px 0", color: theme.colors.highlight }}>ML Model: LGMRanker</h3>
          <div style={{ display: "flex", gap: 32, fontSize: 15, color: "#8899A6" }}>
            <span>Optimized for parking data</span>
            <span>Lowest latency, CPU-only inference</span>
            <span>ml.c5.xlarge SageMaker instance</span>
          </div>
          <div style={{ fontSize: 15, color: theme.colors.white, marginTop: 8 }}>
            Ranks ~50 nearby spots by utility (distance, price, availability) — not collaborative filtering
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default AppendixDatabaseSlide;
