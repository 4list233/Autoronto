import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import {
  useFadeIn,
  useSlideIn,
  useScaleIn,
  useCountUp,
  useStagger,
  useTypewriter,
} from "../utils/animations";

const phases = [
  {
    num: 1,
    title: "Discovery",
    desc: "Car polls server every 100m for parking recommendations. ML model ranks nearby spots by distance, price, and availability.",
  },
  {
    num: 2,
    title: "Payment",
    desc: "User selects spot & pays via app. Unique ID written to UHF RFID tag on OBU via CAN bus.",
  },
  {
    num: 3,
    title: "Gate Access",
    desc: "UHF reader at gate scans RFID tag. RSU verifies payment with backend. Gate opens automatically.",
  },
  {
    num: 4,
    title: "Parking",
    desc: "Car autonomously navigates to spot. Backend updates real-time availability. Session complete.",
  },
];

const SystemFlowSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSlide = useSlideIn(0, "left");

  const titleStyle: React.CSSProperties = {
    fontSize: 52,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 56,
    ...titleSlide,
  };

  const timelineStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "center",
    gap: 0,
    width: "100%",
    maxWidth: 1700,
    position: "relative",
  };

  return (
    <AbsoluteFill style={slideStyle}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "100%",
        }}
      >
        <h1 style={titleStyle}>How AutoPark Works</h1>

        <div style={timelineStyle}>
          {phases.map((phase, i) => {
            const phaseDelay = 20 + i * 20;

            const cardProgress = spring({
              frame: frame - phaseDelay,
              fps,
              config: { damping: 14, stiffness: 100, mass: 0.7 },
            });

            const cardOpacity = interpolate(cardProgress, [0, 0.4], [0, 1], {
              extrapolateRight: "clamp",
            });
            const cardScale = interpolate(cardProgress, [0, 1], [0.6, 1]);

            // Connector line between phases
            const lineDelay = phaseDelay + 10;
            const lineProgress = interpolate(
              frame - lineDelay,
              [0, fps * 0.4],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );

            const circleStyle: React.CSSProperties = {
              width: 48,
              height: 48,
              borderRadius: "50%",
              background: theme.colors.accent,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 22,
              fontWeight: 800,
              color: theme.colors.white,
              marginBottom: 16,
              boxShadow: `0 0 24px ${theme.colors.accent}66`,
              flexShrink: 0,
            };

            const cardStyle: React.CSSProperties = {
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              width: 320,
              textAlign: "center" as const,
              transform: `scale(${cardScale})`,
              opacity: cardOpacity,
            };

            const phaseCardStyle: React.CSSProperties = {
              background: "#162238",
              borderRadius: 12,
              padding: "20px 20px",
              width: "100%",
              boxSizing: "border-box" as const,
            };

            return (
              <div
                key={phase.num}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  flexShrink: 0,
                }}
              >
                <div style={cardStyle}>
                  <div style={circleStyle}>{phase.num}</div>
                  <div style={phaseCardStyle}>
                    <div
                      style={{
                        fontSize: 20,
                        fontWeight: 700,
                        color: theme.colors.accent,
                        marginBottom: 10,
                      }}
                    >
                      {phase.title}
                    </div>
                    <div
                      style={{
                        fontSize: 14,
                        fontWeight: 400,
                        color: theme.colors.gray,
                        lineHeight: 1.5,
                      }}
                    >
                      {phase.desc}
                    </div>
                  </div>
                </div>

                {i < phases.length - 1 && (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      height: 48,
                      paddingLeft: 4,
                      paddingRight: 4,
                      flexShrink: 0,
                    }}
                  >
                    <div
                      style={{
                        width: interpolate(lineProgress, [0, 1], [0, 60]),
                        height: 3,
                        background: `linear-gradient(90deg, ${theme.colors.accent}, ${theme.colors.accent}44)`,
                        boxShadow: `0 0 10px ${theme.colors.accent}44`,
                        borderRadius: 2,
                      }}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default SystemFlowSlide;
