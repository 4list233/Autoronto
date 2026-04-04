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

const ConclusionSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const title = useTypewriter("The Future of Parking is Autonomous", 0, 1.2);

  const titleStyle: React.CSSProperties = {
    fontSize: 52,
    fontWeight: 800,
    color: theme.colors.white,
    textAlign: "center",
    margin: 0,
    lineHeight: 1.15,
    textShadow: `0 0 40px ${theme.colors.accent}44`,
    minHeight: 65,
  };

  const keyPoints = [
    "\u2713 Proven technical architecture: OBU/RSU stack, cloud backend, seamless app",
    "\u2713 Economics that work: $401 RSU payback in 6 days, 40:1 LTV:CAC",
    "\u2713 $10B+ market growing at 17% annually \u2014 no incumbent with end-to-end solution",
    "\u2713 Clear path to $1M+ ARR by Year 3",
  ];

  const ctaDelay = 60;
  const ctaOpacity = useFadeIn(ctaDelay);
  const ctaScale = useScaleIn(ctaDelay);

  const ctaBoxStyle: React.CSSProperties = {
    border: `2px solid ${theme.colors.accent}`,
    borderRadius: 16,
    padding: "28px 40px",
    maxWidth: 900,
    textAlign: "center",
    boxShadow: `0 0 30px ${theme.colors.accent}33, 0 0 60px ${theme.colors.accent}18, inset 0 0 30px ${theme.colors.accent}08`,
    background: `linear-gradient(135deg, ${theme.colors.primary}ee, ${theme.colors.secondary}88)`,
    ...ctaScale,
  };

  const ctaTextStyle: React.CSSProperties = {
    fontSize: 20,
    fontWeight: 400,
    color: theme.colors.white,
    lineHeight: 1.7,
    margin: 0,
  };

  const bottomDelay = 80;
  const bottomOpacity = useFadeIn(bottomDelay);
  const bottomStyle: React.CSSProperties = {
    fontSize: 24,
    fontWeight: 700,
    color: theme.colors.accent,
    textAlign: "center",
    opacity: bottomOpacity,
    marginTop: 28,
    textShadow: `0 0 20px ${theme.colors.accent}44`,
  };

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
          gap: 12,
        }}
      >
        <h1 style={titleStyle}>{title}</h1>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 10,
            marginTop: 24,
            marginBottom: 28,
            maxWidth: 920,
            width: "100%",
          }}
        >
          {keyPoints.map((point, i) => {
            const delay = useStagger(i, 20, 10);
            const anim = useSlideIn(delay, "up");
            return (
              <div
                key={i}
                style={{
                  fontSize: 21,
                  fontWeight: 500,
                  color: theme.colors.white,
                  padding: "10px 20px",
                  borderRadius: 10,
                  background: `linear-gradient(90deg, ${theme.colors.secondary}66, transparent)`,
                  borderLeft: `3px solid ${theme.colors.accent}`,
                  ...anim,
                }}
              >
                {point}
              </div>
            );
          })}
        </div>

        <div style={ctaBoxStyle}>
          <p style={ctaTextStyle}>
            Help us deploy our first{" "}
            <span style={{ color: theme.colors.accent, fontWeight: 700 }}>
              50 pilot RSU gates
            </span>
            , sign our first{" "}
            <span style={{ color: theme.colors.accentGreen, fontWeight: 700 }}>
              commercial lot
            </span>
            , and begin the{" "}
            <span style={{ color: theme.colors.accentOrange, fontWeight: 700 }}>
              OEM pilot
            </span>{" "}
            that puts AutoPark on every autonomous vehicle.
          </p>
        </div>

        <p style={bottomStyle}>
          The future of parking is autonomous. Help us build it.
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default ConclusionSlide;
