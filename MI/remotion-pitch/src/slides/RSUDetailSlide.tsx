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

const hardwareComponents = [
  {
    name: "NXP I.MX8M Mini",
    role: "Application Processor",
    color: theme.colors.accent,
    icon: "\u{1F9E0}",
  },
  {
    name: "Quectel AG55xQ",
    role: "Internet Module",
    color: theme.colors.accentGreen,
    icon: "\u{1F4E1}",
  },
  {
    name: "Sequent Microsystems I/O HAT",
    role: "Relay Module",
    color: theme.colors.accentOrange,
    icon: "\u26A1",
  },
  {
    name: "STid SPECTRE",
    role: "UHF RFID Reader",
    color: theme.colors.highlight,
    icon: "\u{1F4F6}",
  },
];

const RSUDetailSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSlide = useSlideIn(0, "up");
  const costValue = useCountUp(401, 70, 1.5);

  const titleStyle: React.CSSProperties = {
    fontSize: 52,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 48,
    ...titleSlide,
  };

  // Compatibility note
  const compatDelay = 55;
  const compatAnim = useSlideIn(compatDelay, "up");

  // Cost callout
  const costDelay = 65;
  const costAnim = useScaleIn(costDelay);

  // Comparison text
  const compDelay = 80;
  const compOpacity = useFadeIn(compDelay);

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
        <h1 style={titleStyle}>Road-Side Unit (RSU)</h1>

        {/* Hardware components horizontal layout */}
        <div
          style={{
            display: "flex",
            gap: 24,
            marginBottom: 40,
            maxWidth: 1500,
          }}
        >
          {hardwareComponents.map((comp, i) => {
            const delay = useStagger(i, 12, 10);
            const anim = useScaleIn(delay);

            const cardStyle: React.CSSProperties = {
              background: "#162238",
              borderRadius: 16,
              padding: "28px 24px",
              width: 280,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center" as const,
              border: `2px solid ${comp.color}33`,
              boxShadow: `0 0 30px ${comp.color}22`,
              ...anim,
            };

            return (
              <div key={comp.name} style={cardStyle}>
                <span
                  style={{
                    fontSize: 40,
                    marginBottom: 16,
                    lineHeight: 1,
                  }}
                >
                  {comp.icon}
                </span>
                <div
                  style={{
                    fontSize: 18,
                    fontWeight: 700,
                    color: theme.colors.white,
                    marginBottom: 8,
                  }}
                >
                  {comp.name}
                </div>
                <div
                  style={{
                    fontSize: 14,
                    fontWeight: 600,
                    color: comp.color,
                    textTransform: "uppercase" as const,
                    letterSpacing: 1,
                  }}
                >
                  {comp.role}
                </div>
              </div>
            );
          })}
        </div>

        {/* Compatibility note */}
        <div
          style={{
            fontSize: 17,
            fontWeight: 400,
            color: theme.colors.gray,
            marginBottom: 32,
            textAlign: "center" as const,
            maxWidth: 900,
            lineHeight: 1.5,
            ...compatAnim,
          }}
        >
          Connects to parking gate's dry contact input — compatible with{" "}
          <span style={{ color: theme.colors.white, fontWeight: 600 }}>
            FAAC, CAME, SKIDATA
          </span>{" "}
          gates
        </div>

        {/* Cost callout */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 12,
            ...costAnim,
          }}
        >
          <div
            style={{
              background: `linear-gradient(135deg, ${theme.colors.accentGreen}, ${theme.colors.accentGreen}CC)`,
              borderRadius: 16,
              padding: "20px 48px",
              boxShadow: `0 0 40px ${theme.colors.accentGreen}44`,
            }}
          >
            <span
              style={{
                fontSize: 36,
                fontWeight: 800,
                color: theme.colors.primary,
              }}
            >
              RSU Cost: ~${costValue}/gate
            </span>
          </div>

          <div
            style={{
              fontSize: 18,
              fontWeight: 500,
              color: theme.colors.gray,
              opacity: compOpacity,
              textAlign: "center" as const,
            }}
          >
            vs.{" "}
            <span style={{ color: theme.colors.accentOrange, fontWeight: 700 }}>
              $5,000–$15,000
            </span>{" "}
            for commercial RSU units —{" "}
            <span style={{ color: theme.colors.accentGreen, fontWeight: 700 }}>
              10-30x cost reduction
            </span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default RSUDetailSlide;
