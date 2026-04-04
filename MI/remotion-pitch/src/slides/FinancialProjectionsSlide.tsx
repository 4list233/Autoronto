import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import { useFadeIn, useSlideIn, useScaleIn, useCountUp, useStagger, useTypewriter } from "../utils/animations";

const FinancialProjectionsSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = useFadeIn(0);

  // J-curve bar data: negative values for years 1-2, positive for 3-5
  const barData = [
    { year: "Y1", value: -30, color: theme.colors.accentOrange },
    { year: "Y2", value: -12, color: theme.colors.accentOrange },
    { year: "Y3", value: 35, color: theme.colors.accentGreen },
    { year: "Y4", value: 70, color: theme.colors.accentGreen },
    { year: "Y5", value: 100, color: theme.colors.accentGreen },
  ];

  const maxAbsValue = 100;
  const chartHeight = 300;
  const zeroY = chartHeight * 0.35; // zero line position (35% from top)

  // Scenario cards
  const scenario0Delay = useStagger(0, 65, 10);
  const scenario1Delay = useStagger(1, 65, 10);
  const scenario2Delay = useStagger(2, 65, 10);
  const scenario0 = useScaleIn(scenario0Delay);
  const scenario1 = useScaleIn(scenario1Delay);
  const scenario2 = useScaleIn(scenario2Delay);

  const milestoneOpacity = useFadeIn(100);

  const titleStyle: React.CSSProperties = {
    fontSize: 44,
    fontWeight: 700,
    color: theme.colors.white,
    opacity: titleOpacity,
    textAlign: "center",
    margin: 0,
    marginBottom: 24,
    letterSpacing: -1,
  };

  const axisLabelStyle: React.CSSProperties = {
    fontSize: 13,
    color: theme.colors.gray,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: 1,
  };

  const scenarioCard = (
    accentColor: string,
    highlighted: boolean,
    animStyle: React.CSSProperties
  ): React.CSSProperties => ({
    flex: 1,
    background: highlighted ? `${accentColor}18` : `${theme.colors.primary}CC`,
    borderRadius: 12,
    padding: "16px 20px",
    textAlign: "center",
    border: `2px solid ${highlighted ? accentColor : `${theme.colors.secondary}88`}`,
    boxShadow: highlighted ? `0 0 24px ${accentColor}33` : "none",
    ...animStyle,
  });

  return (
    <AbsoluteFill style={slideStyle}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          width: "100%",
          height: "100%",
          justifyContent: "flex-start",
          alignItems: "center",
          paddingTop: 36,
        }}
      >
        <h1 style={titleStyle}>Financial Projections: J-Curve &amp; NPV</h1>

        {/* J-Curve Chart */}
        <div
          style={{
            width: "100%",
            maxWidth: 1100,
            height: chartHeight,
            position: "relative",
            marginBottom: 32,
            display: "flex",
            alignItems: "flex-end",
          }}
        >
          {/* Y-axis label */}
          <div
            style={{
              position: "absolute",
              left: -8,
              top: "50%",
              transform: "rotate(-90deg) translateX(-50%)",
              transformOrigin: "0 0",
              ...axisLabelStyle,
            }}
          >
            Revenue / Cash Flow
          </div>

          {/* Zero line */}
          <div
            style={{
              position: "absolute",
              left: 60,
              right: 0,
              top: zeroY,
              height: 2,
              background: `${theme.colors.gray}55`,
              zIndex: 1,
            }}
          />
          <span
            style={{
              position: "absolute",
              left: 30,
              top: zeroY - 8,
              fontSize: 12,
              color: theme.colors.gray,
            }}
          >
            $0
          </span>

          {/* Bars */}
          <div
            style={{
              display: "flex",
              alignItems: "flex-end",
              justifyContent: "center",
              gap: 32,
              width: "100%",
              height: "100%",
              paddingLeft: 70,
              position: "relative",
            }}
          >
            {barData.map((bar, i) => {
              const barDelay = useStagger(i, 20, 8);
              const barProgress = spring({
                frame: frame - barDelay,
                fps,
                config: { damping: 14, stiffness: 100, mass: 0.7 },
              });

              const isNegative = bar.value < 0;
              const normalizedHeight =
                (Math.abs(bar.value) / maxAbsValue) * (chartHeight - zeroY - 20);
              const animatedHeight = interpolate(barProgress, [0, 1], [0, normalizedHeight]);
              const barOpacity = interpolate(barProgress, [0, 0.3], [0, 1], {
                extrapolateRight: "clamp",
              });

              return (
                <div
                  key={bar.year}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    position: "absolute",
                    left: `${16 + i * 17}%`,
                  }}
                >
                  {/* Bar */}
                  <div
                    style={{
                      width: 80,
                      height: animatedHeight,
                      background: `linear-gradient(${isNegative ? "0deg" : "180deg"}, ${bar.color}, ${bar.color}88)`,
                      borderRadius: isNegative ? "0 0 8 8" : "8px 8px 0 0",
                      position: "absolute",
                      top: isNegative ? zeroY + 2 : zeroY - animatedHeight,
                      opacity: barOpacity,
                      boxShadow: `0 0 20px ${bar.color}33`,
                    }}
                  />
                  {/* Value label */}
                  <span
                    style={{
                      position: "absolute",
                      top: isNegative ? zeroY + animatedHeight + 6 : zeroY - animatedHeight - 22,
                      fontSize: 14,
                      fontWeight: 700,
                      color: bar.color,
                      opacity: barOpacity,
                      fontFamily: theme.fonts.mono,
                    }}
                  >
                    {isNegative ? `−$${Math.abs(bar.value)}k` : `+$${bar.value}k`}
                  </span>
                  {/* Year label */}
                  <span
                    style={{
                      position: "absolute",
                      top: chartHeight - 20,
                      fontSize: 15,
                      fontWeight: 600,
                      color: theme.colors.white,
                      opacity: barOpacity,
                    }}
                  >
                    {bar.year}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Scenario cards */}
        <div style={{ display: "flex", gap: 20, width: "100%", maxWidth: 1400, marginBottom: 20 }}>
          <div style={scenarioCard(theme.colors.accentOrange, false, scenario0)}>
            <div style={{ fontSize: 13, fontWeight: 700, color: theme.colors.accentOrange, textTransform: "uppercase", letterSpacing: 2, marginBottom: 6 }}>
              Bear (8 txns/day)
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, color: theme.colors.white }}>
              ~$26/gate/day net
            </div>
          </div>
          <div style={scenarioCard(theme.colors.accentGreen, true, scenario1)}>
            <div style={{ fontSize: 13, fontWeight: 700, color: theme.colors.accentGreen, textTransform: "uppercase", letterSpacing: 2, marginBottom: 6 }}>
              Base (15 txns/day)
            </div>
            <div style={{ fontSize: 28, fontWeight: 800, color: theme.colors.white }}>
              ~$67/gate/day net
            </div>
          </div>
          <div style={scenarioCard(theme.colors.accent, false, scenario2)}>
            <div style={{ fontSize: 13, fontWeight: 700, color: theme.colors.accent, textTransform: "uppercase", letterSpacing: 2, marginBottom: 6 }}>
              Bull (25 txns/day)
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, color: theme.colors.white }}>
              ~$112/gate/day net
            </div>
          </div>
        </div>

        {/* Revenue milestone */}
        <div
          style={{
            fontSize: 17,
            fontWeight: 600,
            color: theme.colors.highlight,
            textAlign: "center",
            opacity: milestoneOpacity,
            padding: "12px 28px",
            background: `${theme.colors.highlight}11`,
            borderRadius: 10,
            border: `1px solid ${theme.colors.highlight}33`,
            fontFamily: theme.fonts.mono,
          }}
        >
          500 gates &times; 15 txns/day &times; $4.47 &times; 365 = <span style={{ fontSize: 22 }}>~$1.2M ARR by Year 3</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default FinancialProjectionsSlide;
