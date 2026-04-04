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

const ProblemSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // --- Section divider phase (first ~20 frames) ---
  const dividerOpacity = interpolate(frame, [0, 10, 20, 30], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const dividerScale = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 100, mass: 0.7 },
  });

  const accentLineWidth = interpolate(frame, [5, 20], [0, 200], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const dividerContainerStyle: React.CSSProperties = {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    opacity: dividerOpacity,
    transform: `scale(${interpolate(dividerScale, [0, 1], [0.8, 1])})`,
  };

  const dividerTitleStyle: React.CSSProperties = {
    fontSize: 72,
    fontWeight: 800,
    color: theme.colors.white,
    letterSpacing: -1,
    margin: 0,
    textAlign: "center",
  };

  const dividerLineStyle: React.CSSProperties = {
    width: accentLineWidth,
    height: 4,
    background: theme.colors.accent,
    borderRadius: 2,
    marginTop: 24,
    boxShadow: `0 0 20px ${theme.colors.accent}88`,
  };

  // --- Content phase (after frame 20) ---
  const contentDelay = 25;
  const contentOpacity = interpolate(frame, [20, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Title
  const titleSlide = useSlideIn(contentDelay, "up");
  const titleStyle: React.CSSProperties = {
    fontSize: 38,
    fontWeight: 700,
    color: theme.colors.white,
    textAlign: "center",
    maxWidth: 1100,
    lineHeight: 1.3,
    margin: 0,
    marginBottom: 48,
    ...titleSlide,
  };

  // Stat cards scale in
  const leftCardAnim = useScaleIn(contentDelay + 10);
  const rightCardAnim = useScaleIn(contentDelay + 18);

  const hoursCount = useCountUp(107, contentDelay + 12);
  const billionRaw = useCountUp(727, contentDelay + 20, 1.8);
  const formattedBillion = (billionRaw / 10).toFixed(1);

  const cardContainerStyle: React.CSSProperties = {
    display: "flex",
    gap: 48,
    justifyContent: "center",
    alignItems: "stretch",
    width: "100%",
    maxWidth: 1200,
    marginBottom: 48,
  };

  const cardBase: React.CSSProperties = {
    background: theme.colors.white,
    borderRadius: 20,
    padding: "48px 56px",
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    boxShadow: "0 8px 40px rgba(0,0,0,0.3)",
  };

  const statNumberStyle: React.CSSProperties = {
    fontSize: 72,
    fontWeight: 900,
    color: theme.colors.accentOrange,
    margin: 0,
    lineHeight: 1.1,
    letterSpacing: -2,
  };

  const statSubtitleStyle: React.CSSProperties = {
    fontSize: 18,
    fontWeight: 500,
    color: theme.colors.primary,
    textAlign: "center",
    marginTop: 16,
    lineHeight: 1.5,
    opacity: 0.85,
  };

  // Bottom text
  const bottomFade = useFadeIn(contentDelay + 35);
  const bottomStyle: React.CSSProperties = {
    fontSize: 22,
    fontWeight: 400,
    color: theme.colors.gray,
    textAlign: "center",
    maxWidth: 900,
    opacity: bottomFade,
    lineHeight: 1.6,
  };

  return (
    <AbsoluteFill style={slideStyle}>
      {/* Section Divider */}
      <div style={dividerContainerStyle}>
        <h1 style={dividerTitleStyle}>Problem Statement</h1>
        <div style={dividerLineStyle} />
      </div>

      {/* Content */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "100%",
          opacity: contentOpacity,
        }}
      >
        <h2 style={titleStyle}>
          Urban parking is time-consuming, inefficient, and stressful.
        </h2>

        <div style={cardContainerStyle}>
          {/* Left card */}
          <div style={{ ...cardBase, ...leftCardAnim }}>
            <p style={statNumberStyle}>{hoursCount} hours/year</p>
            <p style={statSubtitleStyle}>
              spent searching for parking in NYC — over 4.4 days
            </p>
          </div>

          {/* Right card */}
          <div style={{ ...cardBase, ...rightCardAnim }}>
            <p style={statNumberStyle}>
              ${formattedBillion} billion
            </p>
            <p style={statSubtitleStyle}>
              annual costs from wasted time and fuel in the US
            </p>
          </div>
        </div>

        <p style={bottomStyle}>
          This wastes time, fuel, and creates unnecessary stress and emissions.
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default ProblemSlide;
