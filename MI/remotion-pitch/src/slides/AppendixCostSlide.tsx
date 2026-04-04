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

interface BOMRow {
  component: string;
  cost: string;
  isTotal?: boolean;
}

const obuRows: BOMRow[] = [
  { component: "UHF RFID Tag", cost: "~$1\u20133" },
  { component: "UHF Reader/Writer (M6E Nano)", cost: "~$50\u201370" },
  { component: "CAN Bus Bridge (STM32G431)", cost: "~$3\u20135" },
  { component: "Total", cost: "~$55\u201378 (prototype)", isTotal: true },
];

const rsuRows: BOMRow[] = [
  { component: "Application Processor (NXP I.MX8M)", cost: "~$20\u201335" },
  { component: "Internet Module (Quectel AG55xQ)", cost: "~$40\u201360" },
  { component: "Relay Module", cost: "~$50\u201370" },
  { component: "UHF RFID Reader (STid SPECTRE)", cost: "~$300\u2013500" },
  { component: "Total", cost: "~$410\u2013665 (prototype)", isTotal: true },
];

const BOMTable: React.FC<{
  title: string;
  rows: BOMRow[];
  color: string;
  baseDelay: number;
}> = ({ title, rows, color, baseDelay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headerOpacity = useFadeIn(baseDelay);

  const tableStyle: React.CSSProperties = {
    background: `linear-gradient(135deg, ${theme.colors.primary}ee, ${theme.colors.secondary}88)`,
    border: `1px solid ${color}44`,
    borderRadius: 14,
    overflow: "hidden",
    flex: 1,
    boxShadow: `0 0 25px ${color}15, 0 8px 32px rgba(0,0,0,0.3)`,
  };

  return (
    <div style={tableStyle}>
      <div
        style={{
          padding: "16px 24px",
          background: `linear-gradient(90deg, ${color}22, transparent)`,
          borderBottom: `1px solid ${color}33`,
          fontSize: 22,
          fontWeight: 700,
          color,
          opacity: headerOpacity,
        }}
      >
        {title}
      </div>
      <div style={{ padding: "8px 0" }}>
        {rows.map((row, i) => {
          const delay = baseDelay + 10 + i * 8;
          const rowProgress = spring({
            frame: frame - delay,
            fps,
            config: { damping: 15, stiffness: 120, mass: 0.7 },
          });
          const opacity = interpolate(rowProgress, [0, 0.3], [0, 1], {
            extrapolateRight: "clamp",
          });
          const translateX = interpolate(rowProgress, [0, 1], [30, 0]);

          return (
            <div
              key={i}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "10px 24px",
                borderTop: row.isTotal
                  ? `1px solid ${color}44`
                  : i > 0
                    ? `1px solid ${theme.colors.secondary}44`
                    : "none",
                opacity,
                transform: `translateX(${translateX}px)`,
                background: row.isTotal
                  ? `${color}11`
                  : "transparent",
              }}
            >
              <span
                style={{
                  fontSize: row.isTotal ? 18 : 16,
                  fontWeight: row.isTotal ? 700 : 400,
                  color: row.isTotal ? color : theme.colors.white,
                }}
              >
                {row.component}
              </span>
              <span
                style={{
                  fontSize: row.isTotal ? 18 : 16,
                  fontWeight: row.isTotal ? 700 : 500,
                  color: row.isTotal ? color : theme.colors.gray,
                  fontFamily: theme.fonts.mono,
                }}
              >
                {row.cost}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const AppendixCostSlide: React.FC = () => {
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

  const subtitleOpacity = useFadeIn(10);
  const subtitleStyle: React.CSSProperties = {
    fontSize: 18,
    color: theme.colors.gray,
    opacity: subtitleOpacity,
    marginTop: 4,
    marginBottom: 28,
    textAlign: "center",
  };

  const noteDelay = 70;
  const noteAnim = useSlideIn(noteDelay, "up");
  const noteStyle: React.CSSProperties = {
    fontSize: 18,
    fontWeight: 500,
    color: theme.colors.accentGreen,
    textAlign: "center",
    marginTop: 28,
    padding: "14px 28px",
    borderRadius: 10,
    background: `${theme.colors.accentGreen}11`,
    border: `1px solid ${theme.colors.accentGreen}33`,
    ...noteAnim,
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
        <h1 style={titleStyle}>Appendix A: Hardware Cost Breakdown</h1>
        <p style={subtitleStyle}>Bill of Materials — Prototype Stage</p>

        <div
          style={{
            display: "flex",
            gap: 32,
            width: "100%",
            maxWidth: 1000,
          }}
        >
          <BOMTable
            title="OBU BOM"
            rows={obuRows}
            color={theme.colors.accent}
            baseDelay={15}
          />
          <BOMTable
            title="RSU BOM"
            rows={rsuRows}
            color={theme.colors.accentOrange}
            baseDelay={25}
          />
        </div>

        <div style={noteStyle}>
          At scale (50k+ units): OBU drops to{" "}
          <span style={{ fontWeight: 700 }}>~$212</span>, RSU drops to{" "}
          <span style={{ fontWeight: 700 }}>~$300/gate</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default AppendixCostSlide;
