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

interface ResearchRow {
  firm: string;
  val2024: string;
  val2025: string;
}

const researchData: ResearchRow[] = [
  { firm: "Straits Research", val2024: "$7.98B", val2025: "$9.37B" },
  { firm: "Precedence Research", val2024: "$9.15B", val2025: "$11.18B" },
  { firm: "The Business Research Co.", val2024: "$8.5B", val2025: "$10.27B" },
];

const tailwinds = [
  "Urbanization & Congestion",
  "Environmental Concerns",
  "Smart City + IoT Initiatives",
];

const BenchmarkingSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title slides in from left
  const titleAnim = useSlideIn(5, "left");
  const titleStyle: React.CSSProperties = {
    fontSize: 48,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 40,
    letterSpacing: -1,
    alignSelf: "flex-start",
    ...titleAnim,
  };

  // Big market size scales in
  const marketAnim = useScaleIn(15);
  const marketStyle: React.CSSProperties = {
    fontSize: 56,
    fontWeight: 900,
    color: theme.colors.accent,
    margin: 0,
    textAlign: "center",
    letterSpacing: -1,
    ...marketAnim,
  };

  const marketSubStyle: React.CSSProperties = {
    fontSize: 20,
    fontWeight: 500,
    color: theme.colors.gray,
    margin: 0,
    marginTop: 4,
    textAlign: "center",
    ...marketAnim,
  };

  // Arrow + future value
  const arrowFade = useFadeIn(30);
  const arrowContainerStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 24,
    marginTop: 16,
    marginBottom: 8,
    opacity: arrowFade,
  };

  const arrowStyle: React.CSSProperties = {
    fontSize: 36,
    color: theme.colors.accent,
  };

  const futureValueStyle: React.CSSProperties = {
    fontSize: 40,
    fontWeight: 800,
    color: theme.colors.accentGreen,
    margin: 0,
  };

  // CAGR pulsing
  const pulse = interpolate(
    Math.sin((frame / fps) * Math.PI * 2 * 0.8),
    [-1, 1],
    [0.92, 1.08]
  );
  const cagrFade = useFadeIn(35);
  const cagrStyle: React.CSSProperties = {
    fontSize: 32,
    fontWeight: 800,
    color: theme.colors.highlight,
    margin: 0,
    marginBottom: 32,
    transform: `scale(${pulse})`,
    opacity: cagrFade,
    textAlign: "center",
  };

  // Research table
  const tableContainerStyle: React.CSSProperties = {
    width: "100%",
    maxWidth: 900,
    marginBottom: 32,
  };

  const headerRowStyle: React.CSSProperties = {
    display: "flex",
    padding: "12px 24px",
    borderBottom: `2px solid ${theme.colors.accent}44`,
    marginBottom: 4,
  };

  const headerCellStyle: React.CSSProperties = {
    fontSize: 14,
    fontWeight: 700,
    color: theme.colors.accent,
    textTransform: "uppercase",
    letterSpacing: 1.5,
  };

  // Tailwind cards
  const tailwindContainerStyle: React.CSSProperties = {
    display: "flex",
    gap: 24,
    justifyContent: "center",
    width: "100%",
    maxWidth: 1000,
  };

  return (
    <AbsoluteFill style={slideStyle}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "flex-start",
          width: "100%",
          height: "100%",
          paddingTop: 60,
          paddingBottom: 40,
          paddingLeft: 64,
          paddingRight: 64,
          boxSizing: "border-box",
        }}
      >
        <h1 style={titleStyle}>Market Assessment</h1>

        {/* Big market size */}
        <p style={marketStyle}>$9.3 – $11.2 Billion</p>
        <p style={marketSubStyle}>Estimated market size in 2025</p>

        {/* Arrow to future */}
        <div style={arrowContainerStyle}>
          <span style={arrowStyle}>→</span>
          <p style={futureValueStyle}>$33+ Billion by 2033</p>
        </div>

        {/* CAGR */}
        <p style={cagrStyle}>17.4% CAGR</p>

        {/* Research table */}
        <div style={tableContainerStyle}>
          <div style={headerRowStyle}>
            <span style={{ ...headerCellStyle, flex: 2 }}>Research Firm</span>
            <span
              style={{ ...headerCellStyle, flex: 1, textAlign: "center" }}
            >
              2024
            </span>
            <span
              style={{ ...headerCellStyle, flex: 1, textAlign: "center" }}
            >
              2025
            </span>
          </div>

          {researchData.map((row, i) => {
            const rowDelay = useStagger(i, 42, 10);
            const rowFade = useFadeIn(rowDelay);

            const rowStyle: React.CSSProperties = {
              display: "flex",
              padding: "14px 24px",
              borderBottom: `1px solid ${theme.colors.secondary}`,
              opacity: rowFade,
              background:
                i % 2 === 0 ? "rgba(255,255,255,0.03)" : "transparent",
              borderRadius: 8,
            };

            const cellStyle: React.CSSProperties = {
              fontSize: 18,
              fontWeight: 500,
              color: theme.colors.white,
            };

            return (
              <div key={i} style={rowStyle}>
                <span style={{ ...cellStyle, flex: 2, color: theme.colors.gray }}>
                  {row.firm}
                </span>
                <span
                  style={{
                    ...cellStyle,
                    flex: 1,
                    textAlign: "center",
                    color: theme.colors.white,
                  }}
                >
                  {row.val2024}
                </span>
                <span
                  style={{
                    ...cellStyle,
                    flex: 1,
                    textAlign: "center",
                    color: theme.colors.accentGreen,
                    fontWeight: 700,
                  }}
                >
                  {row.val2025}
                </span>
              </div>
            );
          })}
        </div>

        {/* Tailwind cards */}
        <div style={tailwindContainerStyle}>
          {tailwinds.map((label, i) => {
            const delay = useStagger(i, 70, 10);
            const anim = useScaleIn(delay);

            const cardStyle: React.CSSProperties = {
              flex: 1,
              background: `linear-gradient(135deg, ${theme.colors.secondary}, #1a2a40)`,
              borderRadius: 14,
              padding: "24px 28px",
              textAlign: "center",
              border: `1px solid ${theme.colors.accent}33`,
              boxShadow: "0 4px 20px rgba(0,0,0,0.2)",
              ...anim,
            };

            const labelStyle: React.CSSProperties = {
              fontSize: 18,
              fontWeight: 600,
              color: theme.colors.white,
              margin: 0,
            };

            return (
              <div key={i} style={cardStyle}>
                <p style={labelStyle}>{label}</p>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default BenchmarkingSlide;
