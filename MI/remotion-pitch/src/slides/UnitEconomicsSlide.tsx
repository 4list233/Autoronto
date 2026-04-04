import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import { useFadeIn, useSlideIn, useScaleIn, useCountUp, useStagger, useTypewriter } from "../utils/animations";

const UnitEconomicsSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = useFadeIn(0);

  // Staggered scale-in for metric cards
  const card0Delay = useStagger(0, 15, 12);
  const card1Delay = useStagger(1, 15, 12);
  const card2Delay = useStagger(2, 15, 12);
  const card3Delay = useStagger(3, 15, 12);

  const card0Style = useScaleIn(card0Delay);
  const card1Style = useScaleIn(card1Delay);
  const card2Style = useScaleIn(card2Delay);
  const card3Style = useScaleIn(card3Delay);

  // Count up values
  const rsuCost = useCountUp(401, card0Delay + 10, 1.2);
  const netRevenue = useCountUp(447, card2Delay + 10, 1.2); // will show as $4.47

  // Math section fade in
  const mathDelay = 70;
  const math1Opacity = useFadeIn(useStagger(0, mathDelay, 10));
  const math2Opacity = useFadeIn(useStagger(1, mathDelay, 10));
  const math3Opacity = useFadeIn(useStagger(2, mathDelay, 10));
  const bottomOpacity = useFadeIn(100);

  const titleStyle: React.CSSProperties = {
    fontSize: 48,
    fontWeight: 700,
    color: theme.colors.white,
    opacity: titleOpacity,
    textAlign: "center",
    margin: 0,
    marginBottom: 36,
    letterSpacing: -1,
  };

  const metricCard = (
    accentColor: string,
    extraStyle: React.CSSProperties
  ): React.CSSProperties => ({
    flex: 1,
    background: `${theme.colors.primary}DD`,
    borderRadius: 16,
    padding: "28px 24px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 8,
    borderTop: `4px solid ${accentColor}`,
    boxShadow: `0 8px 32px ${accentColor}18`,
    backdropFilter: "blur(10px)",
    ...extraStyle,
  });

  const metricLabel: React.CSSProperties = {
    fontSize: 14,
    fontWeight: 600,
    color: theme.colors.gray,
    textTransform: "uppercase",
    letterSpacing: 2,
  };

  const metricValueStyle = (color: string): React.CSSProperties => ({
    fontSize: 44,
    fontWeight: 800,
    color,
    lineHeight: 1.1,
    margin: 0,
  });

  const mathLine = (opacity: number): React.CSSProperties => ({
    fontSize: 17,
    color: theme.colors.white,
    fontFamily: theme.fonts.mono,
    opacity,
    padding: "8px 16px",
    background: `${theme.colors.secondary}66`,
    borderRadius: 8,
    borderLeft: `3px solid ${theme.colors.accent}55`,
  });

  const bottomStyle: React.CSSProperties = {
    fontSize: 15,
    color: theme.colors.accentGreen,
    fontWeight: 500,
    textAlign: "center",
    opacity: bottomOpacity,
    padding: "10px 20px",
    background: `${theme.colors.accentGreen}11`,
    borderRadius: 10,
    border: `1px solid ${theme.colors.accentGreen}33`,
  };

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
          paddingTop: 40,
        }}
      >
        <h1 style={titleStyle}>Unit Economics</h1>

        {/* Metric cards grid */}
        <div style={{ display: "flex", gap: 24, width: "100%", maxWidth: 1500, marginBottom: 32 }}>
          <div style={metricCard(theme.colors.accent, card0Style)}>
            <span style={metricLabel}>RSU Cost</span>
            <p style={metricValueStyle(theme.colors.accent)}>${rsuCost}</p>
            <span style={{ fontSize: 13, color: theme.colors.gray }}>per gate</span>
          </div>
          <div style={metricCard(theme.colors.accentGreen, card1Style)}>
            <span style={metricLabel}>Payback Period</span>
            <p style={metricValueStyle(theme.colors.accentGreen)}>~6 days</p>
            <span
              style={{
                fontSize: 13,
                color: theme.colors.accentGreen,
                fontWeight: 600,
                background: `${theme.colors.accentGreen}22`,
                padding: "3px 10px",
                borderRadius: 6,
              }}
            >
              Industry-leading
            </span>
          </div>
          <div style={metricCard(theme.colors.accentOrange, card2Style)}>
            <span style={metricLabel}>Net Revenue/Txn</span>
            <p style={metricValueStyle(theme.colors.accentOrange)}>
              ${(netRevenue / 100).toFixed(2)}
            </p>
            <span style={{ fontSize: 13, color: theme.colors.gray }}>after all costs</span>
          </div>
          <div style={metricCard(theme.colors.highlight, card3Style)}>
            <span style={metricLabel}>LTV:CAC</span>
            <p style={metricValueStyle(theme.colors.highlight)}>40:1</p>
            <span style={{ fontSize: 13, color: theme.colors.gray }}>5-year horizon</span>
          </div>
        </div>

        {/* The math */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10, width: "100%", maxWidth: 1500, marginBottom: 24 }}>
          <div style={mathLine(math1Opacity)}>
            15 transactions/gate/day &times; $4.47 net = <span style={{ color: theme.colors.accent, fontWeight: 700 }}>$67/gate/day</span>
          </div>
          <div style={mathLine(math2Opacity)}>
            $401 RSU cost &divide; $67/day = <span style={{ color: theme.colors.accentGreen, fontWeight: 700 }}>~6 day payback</span>
          </div>
          <div style={mathLine(math3Opacity)}>
            5-Year LTV per gate: <span style={{ color: theme.colors.highlight, fontWeight: 700 }}>~$81,600</span>
          </div>
        </div>

        {/* Bottom note */}
        <div style={bottomStyle}>
          Cloud costs scale sub-linearly: $190/mo at 10 gates &rarr; $1,300/mo at 200 gates
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default UnitEconomicsSlide;
