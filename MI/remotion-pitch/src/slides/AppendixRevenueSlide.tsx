import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import { useFadeIn, useSlideIn, useCountUp, useStagger } from "../utils/animations";

const AppendixRevenueSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleStyle = useSlideIn(0, "left");

  const revenueItems = [
    { label: "Average ticket", value: "$15" },
    { label: "Gross commission (35%)", value: "$5.25" },
    { label: "Payment fees (Stripe)", value: "−$0.78" },
    { label: "Net per transaction", value: "$4.47", highlight: true },
  ];

  const dailyRevenue = useCountUp(67, 60, 1.2);

  const scaleCards = [
    { gates: "50 gates", revenue: "$122K/yr", color: theme.colors.accent },
    { gates: "200 gates", revenue: "$490K/yr", color: theme.colors.accentGreen },
    { gates: "500 gates", revenue: "$1.2M/yr", color: theme.colors.highlight },
  ];

  return (
    <AbsoluteFill style={slideStyle}>
      <div style={{ width: "100%", maxWidth: 1400, display: "flex", flexDirection: "column" as const, gap: 28 }}>
        <h1 style={{ fontSize: 44, fontWeight: 800, margin: 0, ...titleStyle }}>
          Appendix C: <span style={{ color: theme.colors.accent }}>Revenue Model & Unit Economics</span>
        </h1>

        <div style={{ display: "flex", flexDirection: "column" as const, gap: 10, background: "rgba(255,255,255,0.04)", borderRadius: 12, padding: 24 }}>
          {revenueItems.map((item, i) => {
            const delay = useStagger(i, 10, 10);
            const fade = useFadeIn(delay);
            return (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 16px", borderRadius: 8, background: item.highlight ? "rgba(0, 166, 255, 0.12)" : "transparent", borderBottom: item.highlight ? "none" : "1px solid rgba(255,255,255,0.06)", opacity: fade }}>
                <span style={{ fontSize: 20, fontWeight: item.highlight ? 700 : 400 }}>{item.label}</span>
                <span style={{ fontSize: 24, fontWeight: 700, color: item.highlight ? theme.colors.accent : theme.colors.white }}>{item.value}</span>
              </div>
            );
          })}
        </div>

        <div style={{ background: "rgba(0, 214, 143, 0.1)", border: `1px solid ${theme.colors.accentGreen}`, borderRadius: 12, padding: "16px 24px", textAlign: "center" as const, opacity: useFadeIn(50) }}>
          <div style={{ fontSize: 16, color: theme.colors.gray }}>Daily Revenue Per Gate (15 txns/day)</div>
          <div style={{ fontSize: 40, fontWeight: 900, color: theme.colors.accentGreen, marginTop: 4 }}>${dailyRevenue}/day</div>
        </div>

        <div style={{ display: "flex", gap: 20 }}>
          {scaleCards.map((card, i) => {
            const delay = useStagger(i, 70, 12);
            const animStyle = useSlideIn(delay, "up");
            return (
              <div key={i} style={{ flex: 1, background: "rgba(255,255,255,0.04)", borderRadius: 12, padding: "20px 16px", textAlign: "center" as const, borderTop: `3px solid ${card.color}`, ...animStyle }}>
                <div style={{ fontSize: 18, color: theme.colors.gray, marginBottom: 8 }}>{card.gates}</div>
                <div style={{ fontSize: 32, fontWeight: 800, color: card.color }}>{card.revenue}</div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default AppendixRevenueSlide;
