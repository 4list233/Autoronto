import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import { useFadeIn, useSlideIn, useScaleIn, useCountUp, useStagger, useTypewriter } from "../utils/animations";

const PricingModelSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = useFadeIn(0);
  const formulaOpacity = useFadeIn(15);
  const leftSide = useSlideIn(25, "left");
  const rightSide = useSlideIn(25, "right");

  // Demand slider animation: sweeps from 0 to 1 over time
  const sliderProgress = interpolate(frame - 50, [0, fps * 3], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // Ease the slider
  const demand = 1 - Math.pow(1 - sliderProgress, 2);

  // Calculate dynamic percentages
  const lotCommission = 30 - 15 * demand;
  const userFee = 5 + 15 * demand;

  const sliderOpacity = useFadeIn(45);
  const exampleOpacity = useFadeIn(90);

  const titleStyle: React.CSSProperties = {
    fontSize: 48,
    fontWeight: 700,
    color: theme.colors.white,
    opacity: titleOpacity,
    textAlign: "center",
    margin: 0,
    marginBottom: 28,
    letterSpacing: -1,
  };

  const formulaBox: React.CSSProperties = {
    fontSize: 22,
    fontWeight: 700,
    color: theme.colors.highlight,
    textAlign: "center",
    opacity: formulaOpacity,
    padding: "14px 36px",
    background: `${theme.colors.highlight}15`,
    borderRadius: 12,
    border: `2px solid ${theme.colors.highlight}55`,
    marginBottom: 32,
    fontFamily: theme.fonts.mono,
    boxShadow: `0 0 30px ${theme.colors.highlight}22`,
  };

  const sideCard = (
    animStyle: React.CSSProperties,
    accentColor: string
  ): React.CSSProperties => ({
    flex: 1,
    background: `${theme.colors.primary}DD`,
    borderRadius: 16,
    padding: "24px 28px",
    display: "flex",
    flexDirection: "column",
    gap: 10,
    borderTop: `4px solid ${accentColor}`,
    boxShadow: `0 8px 32px ${accentColor}15`,
    ...animStyle,
  });

  const sideLabel: React.CSSProperties = {
    fontSize: 13,
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: 2,
  };

  const sideFormula: React.CSSProperties = {
    fontSize: 18,
    fontFamily: theme.fonts.mono,
    color: theme.colors.white,
    fontWeight: 600,
  };

  const sideRange: React.CSSProperties = {
    fontSize: 14,
    color: theme.colors.gray,
  };

  // Slider visualization
  const sliderTrackWidth = 700;
  const knobPosition = demand * (sliderTrackWidth - 24);

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
        <h1 style={titleStyle}>Dynamic Pricing Model</h1>

        {/* Formula */}
        <div style={formulaBox}>
          Total AutoPark Take = 35% (constant)
        </div>

        {/* Two sides */}
        <div style={{ display: "flex", gap: 28, width: "100%", maxWidth: 1400, marginBottom: 28 }}>
          <div style={sideCard(leftSide, theme.colors.accent)}>
            <span style={{ ...sideLabel, color: theme.colors.accent }}>Lot Commission</span>
            <div style={sideFormula}>
              L(D) = 30% &minus; 15% &times; D
            </div>
            <div style={sideRange}>Range: 15-30%</div>
            <div style={{ fontSize: 36, fontWeight: 800, color: theme.colors.accent, marginTop: 4 }}>
              {lotCommission.toFixed(1)}%
            </div>
          </div>
          <div style={sideCard(rightSide, theme.colors.accentOrange)}>
            <span style={{ ...sideLabel, color: theme.colors.accentOrange }}>User Fee</span>
            <div style={sideFormula}>
              U(D) = 5% + 15% &times; D
            </div>
            <div style={sideRange}>Range: 5-20%</div>
            <div style={{ fontSize: 36, fontWeight: 800, color: theme.colors.accentOrange, marginTop: 4 }}>
              {userFee.toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Demand slider visualization */}
        <div
          style={{
            width: sliderTrackWidth + 120,
            opacity: sliderOpacity,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            marginBottom: 24,
          }}
        >
          {/* Labels */}
          <div style={{ display: "flex", justifyContent: "space-between", width: sliderTrackWidth + 40, marginBottom: 8 }}>
            <span style={{ fontSize: 13, color: theme.colors.accent, fontWeight: 700 }}>
              Low Demand (D=0)<br />
              <span style={{ fontWeight: 400, color: theme.colors.gray }}>Lot: 30% | User: 5%</span>
            </span>
            <span style={{ fontSize: 13, color: theme.colors.accentOrange, fontWeight: 700, textAlign: "right" }}>
              High Demand (D=1)<br />
              <span style={{ fontWeight: 400, color: theme.colors.gray }}>Lot: 15% | User: 20%</span>
            </span>
          </div>

          {/* Track */}
          <div style={{ position: "relative", width: sliderTrackWidth, height: 28 }}>
            {/* Background track */}
            <div
              style={{
                position: "absolute",
                top: 10,
                left: 0,
                width: "100%",
                height: 8,
                borderRadius: 4,
                background: `linear-gradient(90deg, ${theme.colors.accent}55, ${theme.colors.accentOrange}55)`,
              }}
            />
            {/* Filled portion */}
            <div
              style={{
                position: "absolute",
                top: 10,
                left: 0,
                width: knobPosition + 12,
                height: 8,
                borderRadius: 4,
                background: `linear-gradient(90deg, ${theme.colors.accent}, ${theme.colors.accentOrange})`,
                boxShadow: `0 0 12px ${theme.colors.accent}66`,
              }}
            />
            {/* Knob */}
            <div
              style={{
                position: "absolute",
                top: 2,
                left: knobPosition,
                width: 24,
                height: 24,
                borderRadius: "50%",
                background: theme.colors.white,
                border: `3px solid ${theme.colors.accent}`,
                boxShadow: `0 0 16px ${theme.colors.accent}88, 0 2px 8px rgba(0,0,0,0.3)`,
                transition: "none",
              }}
            />
            {/* Current D value label */}
            <div
              style={{
                position: "absolute",
                top: -20,
                left: knobPosition - 8,
                fontSize: 13,
                fontWeight: 700,
                color: theme.colors.highlight,
                fontFamily: theme.fonts.mono,
              }}
            >
              D={demand.toFixed(2)}
            </div>
          </div>
        </div>

        {/* Bottom example */}
        <div
          style={{
            fontSize: 17,
            fontWeight: 600,
            color: theme.colors.white,
            textAlign: "center",
            opacity: exampleOpacity,
            padding: "14px 28px",
            background: `${theme.colors.secondary}AA`,
            borderRadius: 12,
            border: `1px solid ${theme.colors.accent}33`,
            maxWidth: 800,
          }}
        >
          Game night (D=0.92): $25 ticket &rarr; AutoPark nets{" "}
          <span style={{ color: theme.colors.highlight, fontWeight: 800, fontSize: 20 }}>$7.59/txn</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default PricingModelSlide;
