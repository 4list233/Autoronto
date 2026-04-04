import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Img,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import { useFadeIn, useSlideIn, useStagger } from "../utils/animations";

const agendaItems = [
  "Problem Statement",
  "Stakeholders & Impacts",
  "Benchmarking & Market Assessment",
  "Our Solution: AutoPark",
  "System Integration",
  "Business Plan",
];

const AgendaItem: React.FC<{ text: string; index: number }> = ({
  text,
  index,
}) => {
  const delay = useStagger(index, 20, 10);
  const slideIn = useSlideIn(delay, "left");

  const itemStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: 24,
    ...slideIn,
  };

  const numberCircleStyle: React.CSSProperties = {
    width: 52,
    height: 52,
    minWidth: 52,
    borderRadius: "50%",
    background: `linear-gradient(135deg, ${theme.colors.accent} 0%, ${theme.colors.secondary} 100%)`,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 22,
    fontWeight: 700,
    color: theme.colors.white,
    boxShadow: `0 0 20px ${theme.colors.accent}44`,
  };

  const textStyle: React.CSSProperties = {
    fontSize: 28,
    fontWeight: 500,
    color: theme.colors.white,
    letterSpacing: 0.3,
  };

  return (
    <div style={itemStyle}>
      <div style={numberCircleStyle}>{index + 1}</div>
      <span style={textStyle}>{text}</span>
    </div>
  );
};

const AgendaSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleOpacity = useFadeIn(5);

  // Underline animates width
  const underlineProgress = interpolate(frame - 10, [0, fps * 0.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const underlineWidth = interpolate(underlineProgress, [0, 1], [0, 160]);

  const titleStyle: React.CSSProperties = {
    fontSize: 64,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 8,
    opacity: titleOpacity,
  };

  const underlineStyle: React.CSSProperties = {
    width: underlineWidth,
    height: 4,
    backgroundColor: theme.colors.accent,
    borderRadius: 2,
    marginBottom: 48,
    boxShadow: `0 0 12px ${theme.colors.accent}66`,
  };

  const listStyle: React.CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: 28,
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
          maxWidth: 1000,
          height: "100%",
        }}
      >
        <h1 style={titleStyle}>Agenda</h1>
        <div style={underlineStyle} />
        <div style={listStyle}>
          {agendaItems.map((item, i) => (
            <AgendaItem key={item} text={item} index={i} />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default AgendaSlide;
