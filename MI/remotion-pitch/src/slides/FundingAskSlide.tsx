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
  useStagger,
  useTypewriter,
} from "../utils/animations";

const FundingAskSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title with emphasis pulse
  const titleProgress = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100, mass: 0.7 },
  });
  const titleGlow = interpolate(
    Math.sin(frame * 0.08),
    [-1, 1],
    [0.3, 0.7]
  );

  const titleStyle: React.CSSProperties = {
    fontSize: 48,
    fontWeight: 800,
    color: theme.colors.white,
    textAlign: "center",
    margin: 0,
    opacity: interpolate(titleProgress, [0, 0.4], [0, 1], {
      extrapolateRight: "clamp",
    }),
    transform: `scale(${interpolate(titleProgress, [0, 1], [0.8, 1])})`,
    textShadow: `0 0 ${40 * titleGlow}px ${theme.colors.accent}66`,
  };

  // Central ask scales in big
  const askDelay = 15;
  const askScale = useScaleIn(askDelay);
  const askPulse = interpolate(
    Math.sin((frame - askDelay) * 0.06),
    [-1, 1],
    [0.98, 1.02]
  );
  const askStyle: React.CSSProperties = {
    fontSize: 72,
    fontWeight: 900,
    color: theme.colors.accent,
    textAlign: "center",
    margin: "8px 0 4px",
    letterSpacing: -1,
    textShadow: `0 0 50px ${theme.colors.accent}55, 0 0 100px ${theme.colors.accent}22`,
    transform: `${askScale.transform} scale(${askPulse})`,
    opacity: askScale.opacity,
  };

  const funds = [
    {
      label: "50 RSU Gates",
      desc: "~$20K hardware deployment",
      color: theme.colors.accent,
    },
    {
      label: "Cloud Infrastructure",
      desc: "AWS hosting & ML compute",
      color: theme.colors.accentGreen,
    },
    {
      label: "12 Months Runway",
      desc: "First commercial lot + OEM pilot",
      color: theme.colors.accentOrange,
    },
  ];

  const milestones = [
    "Deploy 50 pilot RSU gates",
    "Sign first commercial parking lot",
    "Begin OEM pilot agreement",
  ];

  const milestoneSectionDelay = 65;

  return (
    <AbsoluteFill style={slideStyle}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          width: "100%",
          height: "100%",
          justifyContent: "center",
        }}
      >
        <h1 style={titleStyle}>Investment Ask</h1>
        <h2 style={askStyle}>Seed Capital</h2>

        {/* Use of funds cards */}
        <div
          style={{
            display: "flex",
            gap: 28,
            marginTop: 28,
            marginBottom: 36,
          }}
        >
          {funds.map((fund, i) => {
            const delay = useStagger(i, 30, 10);
            const anim = useSlideIn(delay, "up");
            return (
              <div
                key={i}
                style={{
                  background: `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary}cc)`,
                  border: `2px solid ${fund.color}88`,
                  borderRadius: 16,
                  padding: "28px 32px",
                  width: 260,
                  textAlign: "center",
                  boxShadow: `0 0 25px ${fund.color}22, 0 8px 32px rgba(0,0,0,0.3)`,
                  ...anim,
                }}
              >
                <div
                  style={{
                    fontSize: 26,
                    fontWeight: 700,
                    color: fund.color,
                    marginBottom: 8,
                  }}
                >
                  {fund.label}
                </div>
                <div
                  style={{
                    fontSize: 16,
                    color: theme.colors.gray,
                    fontWeight: 400,
                  }}
                >
                  {fund.desc}
                </div>
              </div>
            );
          })}
        </div>

        {/* Milestones section */}
        <div
          style={{
            fontSize: 20,
            fontWeight: 600,
            color: theme.colors.white,
            marginBottom: 20,
            opacity: useFadeIn(milestoneSectionDelay),
            textTransform: "uppercase" as const,
            letterSpacing: 2,
          }}
        >
          Key Milestones
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 0,
          }}
        >
          {milestones.map((milestone, i) => {
            const delay = useStagger(i, milestoneSectionDelay + 10, 12);
            const dotProgress = spring({
              frame: frame - delay,
              fps,
              config: { damping: 14, stiffness: 120, mass: 0.6 },
            });
            const dotScale = interpolate(dotProgress, [0, 1], [0, 1]);
            const dotOpacity = interpolate(dotProgress, [0, 0.3], [0, 1], {
              extrapolateRight: "clamp",
            });

            // Connecting line animation
            const lineDelay = delay + 5;
            const lineProgress = interpolate(
              frame - lineDelay,
              [0, fps * 0.4],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );

            return (
              <div
                key={i}
                style={{ display: "flex", alignItems: "center" }}
              >
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    width: 220,
                    opacity: dotOpacity,
                  }}
                >
                  <div
                    style={{
                      width: 18,
                      height: 18,
                      borderRadius: "50%",
                      background: theme.colors.accent,
                      boxShadow: `0 0 15px ${theme.colors.accent}88`,
                      transform: `scale(${dotScale})`,
                      marginBottom: 12,
                    }}
                  />
                  <div
                    style={{
                      fontSize: 16,
                      fontWeight: 500,
                      color: theme.colors.white,
                      textAlign: "center",
                      lineHeight: 1.4,
                    }}
                  >
                    {milestone}
                  </div>
                </div>
                {i < milestones.length - 1 && (
                  <div
                    style={{
                      width: 80,
                      height: 3,
                      background: `linear-gradient(90deg, ${theme.colors.accent}, ${theme.colors.accent}44)`,
                      borderRadius: 2,
                      marginBottom: 40,
                      transform: `scaleX(${lineProgress})`,
                      transformOrigin: "left",
                      boxShadow: `0 0 10px ${theme.colors.accent}44`,
                    }}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default FundingAskSlide;
