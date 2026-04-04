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

const cards = [
  {
    icon: "\u{1F4F1}",
    title: "Mobile App",
    desc: "Browse and select parking spots",
  },
  {
    icon: "\u2601\uFE0F",
    title: "Cloud Backend",
    desc: "Smart recommendations & data management",
  },
  {
    icon: "\u{1F697}",
    title: "OBU (On-Board Unit)",
    desc: "Vehicle authentication at gates",
  },
  {
    icon: "\u{1F3D7}\uFE0F",
    title: "RSU (Road-Side Unit)",
    desc: "Parking lot communication & access",
  },
];

const SolutionOverviewSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title animation
  const titleSlide = useSlideIn(0, "up");

  // Accent underline
  const lineProgress = interpolate(frame - 15, [0, fps * 0.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const lineWidth = interpolate(lineProgress, [0, 1], [0, 420]);

  // Subtitle typewriter
  const subtitleText =
    "A smart self-parking system that enables vehicles to autonomously locate, navigate to, and park in available spots without driver input.";
  const typedSubtitle = useTypewriter(subtitleText, 25, 1.2);

  // Card stagger base delay
  const cardBaseDelay = 70;

  const titleStyle: React.CSSProperties = {
    fontSize: 56,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    lineHeight: 1.2,
    ...titleSlide,
  };

  const underlineStyle: React.CSSProperties = {
    width: lineWidth,
    height: 4,
    background: `linear-gradient(90deg, ${theme.colors.accent}, ${theme.colors.accent}88)`,
    boxShadow: `0 0 20px ${theme.colors.accent}66`,
    borderRadius: 2,
    marginTop: 8,
    marginBottom: 24,
  };

  const subtitleStyle: React.CSSProperties = {
    fontSize: 22,
    fontWeight: 300,
    color: theme.colors.gray,
    maxWidth: 900,
    textAlign: "center" as const,
    lineHeight: 1.6,
    minHeight: 70,
    margin: 0,
  };

  const gridStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 24,
    marginTop: 48,
    width: "100%",
    maxWidth: 900,
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
        <h1 style={titleStyle}>Our Solution: AutoPark</h1>
        <div style={underlineStyle} />
        <p style={subtitleStyle}>{typedSubtitle}</p>

        <div style={gridStyle}>
          {cards.map((card, i) => {
            const delay = useStagger(i, cardBaseDelay, 10);
            const cardAnim = useScaleIn(delay);

            const cardStyle: React.CSSProperties = {
              background: "#162238",
              borderRadius: 12,
              padding: "24px 28px",
              borderLeft: `4px solid ${theme.colors.accent}`,
              display: "flex",
              alignItems: "flex-start",
              gap: 16,
              ...cardAnim,
            };

            return (
              <div key={card.title} style={cardStyle}>
                <span style={{ fontSize: 36, lineHeight: 1 }}>{card.icon}</span>
                <div>
                  <div
                    style={{
                      fontSize: 20,
                      fontWeight: 700,
                      color: theme.colors.white,
                      marginBottom: 6,
                    }}
                  >
                    {card.title}
                  </div>
                  <div
                    style={{
                      fontSize: 15,
                      fontWeight: 400,
                      color: theme.colors.gray,
                      lineHeight: 1.4,
                    }}
                  >
                    {card.desc}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default SolutionOverviewSlide;
