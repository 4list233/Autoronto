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

interface CostRow {
  service: string;
  tiers: string[];
  isTotal?: boolean;
}

const costData: CostRow[] = [
  { service: "ECS", tiers: ["$30\u201350", "$80\u2013150", "$200\u2013400", "$500\u20131,200"] },
  { service: "RDS", tiers: ["$50\u201380", "$100\u2013180", "$250\u2013500", "$600\u20131,500"] },
  { service: "SageMaker", tiers: ["$60\u2013100", "$100\u2013200", "$300\u2013600", "$800\u20132,000"] },
  { service: "Data Transfer", tiers: ["$5\u201310", "$15\u201330", "$40\u2013100", "$150\u2013400"] },
  {
    service: "Total/month",
    tiers: ["$145\u2013240", "$295\u2013560", "$790\u20131,600", "$2,050\u20135,100"],
    isTotal: true,
  },
];

const tierHeaders = ["1\u201310 gates", "10\u201350 gates", "50\u2013200 gates", "200+ gates"];

const AppendixCloudSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleScale = useScaleIn(0);
  const titleStyle: React.CSSProperties = {
    fontSize: 42,
    fontWeight: 800,
    color: theme.colors.white,
    textAlign: "center",
    margin: 0,
    ...titleScale,
  };

  const headerDelay = 12;
  const headerOpacity = useFadeIn(headerDelay);

  const tableContainerStyle: React.CSSProperties = {
    width: "100%",
    maxWidth: 1050,
    background: `linear-gradient(135deg, ${theme.colors.primary}ee, ${theme.colors.secondary}88)`,
    border: `1px solid ${theme.colors.accent}33`,
    borderRadius: 16,
    overflow: "hidden",
    marginTop: 28,
    boxShadow: `0 0 30px ${theme.colors.accent}12, 0 8px 32px rgba(0,0,0,0.3)`,
  };

  const headerRowStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: "160px 1fr 1fr 1fr 1fr",
    padding: "14px 24px",
    background: `linear-gradient(90deg, ${theme.colors.accent}22, ${theme.colors.accent}08)`,
    borderBottom: `1px solid ${theme.colors.accent}33`,
    opacity: headerOpacity,
  };

  const headerCellStyle: React.CSSProperties = {
    fontSize: 14,
    fontWeight: 700,
    color: theme.colors.accent,
    textTransform: "uppercase" as const,
    letterSpacing: 1,
    textAlign: "center",
  };

  const insightDelay = 70;
  const insightAnim = useSlideIn(insightDelay, "up");
  const insightStyle: React.CSSProperties = {
    fontSize: 18,
    fontWeight: 500,
    color: theme.colors.accentGreen,
    textAlign: "center",
    marginTop: 28,
    padding: "16px 32px",
    borderRadius: 12,
    background: `${theme.colors.accentGreen}11`,
    border: `1px solid ${theme.colors.accentGreen}33`,
    maxWidth: 850,
    lineHeight: 1.5,
    boxShadow: `0 0 20px ${theme.colors.accentGreen}10`,
    ...insightAnim,
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
        }}
      >
        <h1 style={titleStyle}>Appendix B: Cloud Service Costs</h1>

        <div style={tableContainerStyle}>
          {/* Header row */}
          <div style={headerRowStyle}>
            <div style={{ ...headerCellStyle, textAlign: "left" }}>Service</div>
            {tierHeaders.map((h, i) => (
              <div key={i} style={headerCellStyle}>
                {h}
              </div>
            ))}
          </div>

          {/* Data rows */}
          {costData.map((row, i) => {
            const delay = useStagger(i, 20, 8);
            const rowProgress = spring({
              frame: frame - delay,
              fps,
              config: { damping: 15, stiffness: 120, mass: 0.7 },
            });
            const opacity = interpolate(rowProgress, [0, 0.3], [0, 1], {
              extrapolateRight: "clamp",
            });
            const translateY = interpolate(rowProgress, [0, 1], [15, 0]);

            return (
              <div
                key={i}
                style={{
                  display: "grid",
                  gridTemplateColumns: "160px 1fr 1fr 1fr 1fr",
                  padding: "12px 24px",
                  borderTop:
                    i > 0
                      ? `1px solid ${row.isTotal ? theme.colors.accent + "44" : theme.colors.secondary + "44"}`
                      : "none",
                  background: row.isTotal
                    ? `${theme.colors.accent}11`
                    : "transparent",
                  opacity,
                  transform: `translateY(${translateY}px)`,
                }}
              >
                <div
                  style={{
                    fontSize: row.isTotal ? 16 : 15,
                    fontWeight: row.isTotal ? 700 : 500,
                    color: row.isTotal
                      ? theme.colors.accent
                      : theme.colors.white,
                  }}
                >
                  {row.service}
                </div>
                {row.tiers.map((val, j) => (
                  <div
                    key={j}
                    style={{
                      fontSize: row.isTotal ? 16 : 15,
                      fontWeight: row.isTotal ? 700 : 400,
                      color: row.isTotal
                        ? theme.colors.accent
                        : theme.colors.gray,
                      fontFamily: theme.fonts.mono,
                      textAlign: "center",
                    }}
                  >
                    {val}
                  </div>
                ))}
              </div>
            );
          })}
        </div>

        <div style={insightStyle}>
          Cloud costs scale{" "}
          <span style={{ fontWeight: 700, color: theme.colors.highlight }}>
            sub-linearly
          </span>{" "}
          while revenue scales{" "}
          <span style={{ fontWeight: 700, color: theme.colors.highlight }}>
            linearly
          </span>{" "}
          — margins improve with every gate
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default AppendixCloudSlide;
