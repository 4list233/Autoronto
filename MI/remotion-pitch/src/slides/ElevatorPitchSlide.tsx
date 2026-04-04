import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Img,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import {
  useFadeIn,
  useSlideIn,
  useCountUp,
  useTypewriter,
} from "../utils/animations";

const ElevatorPitchSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title fades in
  const titleOpacity = useFadeIn(5);

  // Key stat "$72.7B" counts up
  const statValue = useCountUp(727, 15, 2);
  const statDisplay = `$${(statValue / 10).toFixed(1)}B`;
  const statOpacity = useFadeIn(15);

  // Second stat fades in
  const stat2Opacity = useFadeIn(50);

  // Pitch text typewriters in
  const pitchText =
    "We are aUToronto AutoPark \u2014 a full-stack autonomous self-parking system. We let the car drop you at the door and handle parking entirely on its own.";
  const typedPitch = useTypewriter(pitchText, 70, 1.2);

  // Bottom text slides up
  const bottomSlide = useSlideIn(140, "up");

  // Final line slides up after
  const finalSlide = useSlideIn(160, "up");

  const titleStyle: React.CSSProperties = {
    fontSize: 56,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 48,
    opacity: titleOpacity,
  };

  const statsRow: React.CSSProperties = {
    display: "flex",
    gap: 80,
    marginBottom: 48,
    alignItems: "flex-start",
  };

  const statBlockStyle: React.CSSProperties = {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
  };

  const statNumberStyle: React.CSSProperties = {
    fontSize: 80,
    fontWeight: 800,
    color: theme.colors.accent,
    margin: 0,
    lineHeight: 1,
    textShadow: `0 0 30px ${theme.colors.accent}44`,
  };

  const stat2NumberStyle: React.CSSProperties = {
    fontSize: 80,
    fontWeight: 800,
    color: theme.colors.accentOrange,
    margin: 0,
    lineHeight: 1,
    textShadow: `0 0 30px ${theme.colors.accentOrange}44`,
  };

  const statLabelStyle: React.CSSProperties = {
    fontSize: 18,
    fontWeight: 400,
    color: theme.colors.gray,
    marginTop: 8,
    maxWidth: 280,
    lineHeight: 1.4,
  };

  const pitchStyle: React.CSSProperties = {
    fontSize: 24,
    fontWeight: 400,
    color: theme.colors.white,
    lineHeight: 1.7,
    maxWidth: 900,
    minHeight: 90,
    marginBottom: 40,
  };

  const bottomStyle: React.CSSProperties = {
    fontSize: 20,
    fontWeight: 600,
    color: theme.colors.accentGreen,
    margin: 0,
    marginBottom: 12,
    ...bottomSlide,
  };

  const finalStyle: React.CSSProperties = {
    fontSize: 18,
    fontWeight: 400,
    color: theme.colors.highlight,
    margin: 0,
    ...finalSlide,
  };

  return (
    <AbsoluteFill style={slideStyle}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          justifyContent: "center",
          width: "100%",
          maxWidth: 1200,
          height: "100%",
        }}
      >
        <h1 style={titleStyle}>The Opportunity</h1>

        <div style={statsRow}>
          <div style={{ ...statBlockStyle, opacity: statOpacity }}>
            <p style={statNumberStyle}>{statDisplay}</p>
            <p style={statLabelStyle}>
              wasted on parking annually in the US
            </p>
          </div>
          <div style={{ ...statBlockStyle, opacity: stat2Opacity }}>
            <p style={stat2NumberStyle}>107 hrs/year</p>
            <p style={statLabelStyle}>
              lost searching for parking in NYC
            </p>
          </div>
        </div>

        <p style={pitchStyle}>
          {typedPitch}
          <span
            style={{
              opacity: typedPitch.length < pitchText.length ? 1 : 0,
              color: theme.colors.accent,
            }}
          >
            |
          </span>
        </p>

        <p style={bottomStyle}>
          Targeting a $10B+ smart parking market growing at 17% CAGR
        </p>
        <p style={finalStyle}>
          Seeking seed investment to deploy first pilot RSUs
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default ElevatorPitchSlide;
