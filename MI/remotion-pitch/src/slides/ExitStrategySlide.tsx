import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import { useFadeIn, useSlideIn, useScaleIn, useStagger } from "../utils/animations";

const ExitStrategySlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleStyle = useSlideIn(0, "left");
  const thesisFade = useFadeIn(15);
  const whyGmFade = useFadeIn(30);

  const valuations = [
    { method: "Revenue Multiple", detail: "$1.2M ARR × 15x SaaS multiple = ~$18M" },
    { method: "DCF / NPV", detail: "5-year discounted cash flow at 25% WACC" },
    { method: "Precedent Transactions", detail: "GM/Cruise ~$1B, Ford/Argo — 5-15x revenue premium" },
  ];

  const targetScale = useScaleIn(80);
  const glowIntensity = interpolate(Math.sin(frame * 0.08), [-1, 1], [15, 35]);

  return (
    <AbsoluteFill style={slideStyle}>
      <div style={{ width: "100%", maxWidth: 1400, display: "flex", flexDirection: "column" as const, gap: 28 }}>
        <h1 style={{ fontSize: 52, fontWeight: 800, margin: 0, ...titleStyle }}>
          Exit Strategy: <span style={{ color: theme.colors.accent }}>OEM Acquisition</span>
        </h1>

        <p style={{ fontSize: 22, lineHeight: 1.6, opacity: thesisFade, color: theme.colors.gray, margin: 0, maxWidth: 900 }}>
          Autonomous vehicle OEMs need a differentiated self-parking feature. Acquisition is more efficient than building in-house.
        </p>

        <div style={{ background: "rgba(0, 166, 255, 0.08)", border: `2px solid ${theme.colors.accent}`, borderRadius: 12, padding: "16px 24px", opacity: whyGmFade }}>
          <h3 style={{ fontSize: 20, fontWeight: 700, margin: "0 0 8px 0", color: theme.colors.accent }}>Why GM / Cruise</h3>
          <p style={{ fontSize: 17, margin: 0, lineHeight: 1.5 }}>
            GM's Cruise division is building the full AV software stack. AutoPark fills the curbside-to-curbside gap, and our RSU network creates a defensible data & infrastructure moat.
          </p>
        </div>

        <div style={{ display: "flex", flexDirection: "column" as const, gap: 14 }}>
          {valuations.map((v, i) => {
            const delay = useStagger(i, 45, 12);
            const animStyle = useSlideIn(delay, "right");
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 20, background: "rgba(255,255,255,0.04)", borderRadius: 10, padding: "14px 24px", ...animStyle }}>
                <div style={{ width: 36, height: 36, borderRadius: "50%", background: theme.colors.secondary, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 700, color: theme.colors.accent, flexShrink: 0 }}>{i + 1}</div>
                <div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: theme.colors.white }}>{v.method}</div>
                  <div style={{ fontSize: 15, color: theme.colors.gray }}>{v.detail}</div>
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ display: "flex", justifyContent: "center", marginTop: 10, ...targetScale }}>
          <div style={{ background: `linear-gradient(135deg, ${theme.colors.secondary}, ${theme.colors.primary})`, border: `2px solid ${theme.colors.highlight}`, borderRadius: 16, padding: "20px 48px", textAlign: "center" as const, boxShadow: `0 0 ${glowIntensity}px ${theme.colors.highlight}40` }}>
            <div style={{ fontSize: 14, textTransform: "uppercase" as const, letterSpacing: 2, color: theme.colors.gray, marginBottom: 8 }}>Target Exit Range</div>
            <div style={{ fontSize: 52, fontWeight: 900, color: theme.colors.highlight }}>$50M – $200M</div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default ExitStrategySlide;
