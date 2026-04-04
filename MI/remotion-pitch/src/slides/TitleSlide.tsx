import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Img,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import { useFadeIn, useSlideIn, useScaleIn } from "../utils/animations";

const TitleSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Giant "AutoPark" scales in with spring
  const titleScale = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 80, mass: 0.9 },
  });
  const titleStyle: React.CSSProperties = {
    fontSize: 120,
    fontWeight: 800,
    letterSpacing: -3,
    color: theme.colors.white,
    transform: `scale(${interpolate(titleScale, [0, 1], [0.3, 1])})`,
    opacity: interpolate(titleScale, [0, 0.5], [0, 1], {
      extrapolateRight: "clamp",
    }),
    textShadow: `0 0 60px ${theme.colors.accent}44, 0 0 120px ${theme.colors.accent}22`,
    margin: 0,
    lineHeight: 1,
  };

  // Subtitle fades in after title
  const subtitleOpacity = useFadeIn(20);
  const subtitleStyle: React.CSSProperties = {
    fontSize: 32,
    fontWeight: 300,
    color: theme.colors.gray,
    opacity: subtitleOpacity,
    marginTop: 16,
    letterSpacing: 1,
  };

  // Glowing accent line animates width from 0 to 300px
  const lineProgress = interpolate(frame - 30, [0, fps * 0.6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const lineWidth = interpolate(lineProgress, [0, 1], [0, 300]);
  const lineStyle: React.CSSProperties = {
    width: lineWidth,
    height: 3,
    background: `linear-gradient(90deg, transparent, ${theme.colors.accent}, transparent)`,
    boxShadow: `0 0 20px ${theme.colors.accent}88, 0 0 40px ${theme.colors.accent}44`,
    borderRadius: 2,
    marginTop: 32,
    marginBottom: 32,
  };

  // Team names fade in
  const teamOpacity = useFadeIn(45);
  const teamStyle: React.CSSProperties = {
    fontSize: 18,
    fontWeight: 400,
    color: theme.colors.gray,
    opacity: teamOpacity,
    letterSpacing: 0.5,
  };

  // Bottom org line slides up
  const orgSlide = useSlideIn(55, "up");
  const orgStyle: React.CSSProperties = {
    fontSize: 16,
    fontWeight: 500,
    color: theme.colors.accent,
    textTransform: "uppercase" as const,
    letterSpacing: 3,
    marginTop: 24,
    ...orgSlide,
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
        <h1 style={titleStyle}>AutoPark</h1>
        <p style={subtitleStyle}>Autonomous Self-Parking for the AV Era</p>
        <div style={lineStyle} />
        <p style={teamStyle}>
          Prithvi Seran &middot; Amanda Liu &middot; Forest Li &middot; Ailing
          Ji &middot; Nevan Kho
        </p>
        <p style={orgStyle}>aUToronto | Mobility Innovation Challenge</p>
      </div>
    </AbsoluteFill>
  );
};

export default TitleSlide;
