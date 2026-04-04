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

interface CompetitorRow {
  name: string;
  approach: string;
  weakness: string;
  isAutopark?: boolean;
}

const competitors: CompetitorRow[] = [
  {
    name: "Bosch AVP",
    approach: "$200k+ per garage",
    weakness: "Too expensive",
  },
  {
    name: "Tesla Enhanced Summon",
    approach: "Cloud only (Uu)",
    weakness: "Fails underground",
  },
  {
    name: "Stanley Robotics",
    approach: "Forklift robots",
    weakness: "Dedicated garages only",
  },
  {
    name: "Valeo AVP",
    approach: "Valeo-specific vehicles",
    weakness: "Not licensable",
  },
  {
    name: "AutoPark",
    approach: "Custom RSU <$500/gate",
    weakness: "C-V2X PC5 + gate handshake",
    isAutopark: true,
  },
];

const CompetitiveLandscapeSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title fades in
  const titleFade = useFadeIn(5);
  const titleStyle: React.CSSProperties = {
    fontSize: 48,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 48,
    letterSpacing: -1,
    opacity: titleFade,
  };

  // Table header
  const headerFade = useFadeIn(12);
  const headerStyle: React.CSSProperties = {
    display: "flex",
    padding: "16px 32px",
    borderBottom: `2px solid ${theme.colors.accent}55`,
    opacity: headerFade,
    marginBottom: 4,
  };

  const headerCellStyle: React.CSSProperties = {
    fontSize: 14,
    fontWeight: 700,
    color: theme.colors.accent,
    textTransform: "uppercase",
    letterSpacing: 2,
  };

  // Bottom callout
  const calloutDelay = 75;
  const calloutAnim = useScaleIn(calloutDelay);
  const calloutStyle: React.CSSProperties = {
    marginTop: 48,
    padding: "24px 40px",
    background: `linear-gradient(135deg, ${theme.colors.accent}18, ${theme.colors.accentGreen}12)`,
    border: `1px solid ${theme.colors.accent}44`,
    borderRadius: 16,
    maxWidth: 1000,
    textAlign: "center",
    ...calloutAnim,
  };

  const calloutTextStyle: React.CSSProperties = {
    fontSize: 20,
    fontWeight: 600,
    color: theme.colors.white,
    margin: 0,
    lineHeight: 1.6,
  };

  const calloutHighlight: React.CSSProperties = {
    color: theme.colors.highlight,
    fontWeight: 800,
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
        <h1 style={titleStyle}>Competitive Landscape</h1>

        {/* Comparison table */}
        <div style={{ width: "100%", maxWidth: 1100 }}>
          {/* Header */}
          <div style={headerStyle}>
            <span style={{ ...headerCellStyle, flex: 1.5 }}>Solution</span>
            <span style={{ ...headerCellStyle, flex: 2 }}>Approach</span>
            <span style={{ ...headerCellStyle, flex: 2 }}>Limitation / Edge</span>
          </div>

          {/* Rows */}
          {competitors.map((row, i) => {
            const rowDelay = useStagger(i, 18, 10);
            const rowAnim = useSlideIn(rowDelay, "right");
            const isAP = row.isAutopark;

            const rowStyle: React.CSSProperties = {
              display: "flex",
              padding: "18px 32px",
              borderRadius: 12,
              marginBottom: 6,
              background: isAP
                ? `linear-gradient(135deg, ${theme.colors.accent}22, ${theme.colors.accent}11)`
                : "rgba(255,255,255,0.03)",
              border: isAP
                ? `2px solid ${theme.colors.accent}66`
                : "1px solid rgba(255,255,255,0.06)",
              alignItems: "center",
              ...rowAnim,
            };

            const nameStyle: React.CSSProperties = {
              fontSize: 20,
              fontWeight: isAP ? 800 : 600,
              color: isAP ? theme.colors.accent : theme.colors.white,
              flex: 1.5,
            };

            const approachStyle: React.CSSProperties = {
              fontSize: 18,
              fontWeight: 500,
              color: isAP ? theme.colors.accentGreen : theme.colors.gray,
              flex: 2,
            };

            const weaknessStyle: React.CSSProperties = {
              fontSize: 18,
              fontWeight: isAP ? 600 : 400,
              color: isAP ? theme.colors.white : theme.colors.accentOrange,
              flex: 2,
              fontStyle: isAP ? "normal" : "italic",
            };

            return (
              <div key={i} style={rowStyle}>
                <span style={nameStyle}>{row.name}</span>
                <span style={approachStyle}>{row.approach}</span>
                <span style={weaknessStyle}>{row.weakness}</span>
              </div>
            );
          })}
        </div>

        {/* Bottom callout */}
        <div style={calloutStyle}>
          <p style={calloutTextStyle}>
            <span style={calloutHighlight}>Only solution</span> combining: cheap
            infrastructure + V2X gate handshake + payment + recommendation engine
          </p>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default CompetitiveLandscapeSlide;
