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

interface StakeholderColumn {
  accentColor: string;
  label: string;
  audience: string;
  point1: string;
  point2: string;
}

const columns: StakeholderColumn[] = [
  {
    accentColor: theme.colors.accent,
    label: "Primary Customer (B2B)",
    audience: "Automotive OEMs (GM, Ford)",
    point1: "Need to differentiate AVs in feature war",
    point2: "AutoPark is a high-value, licensable software module",
  },
  {
    accentColor: theme.colors.accentGreen,
    label: "End User (B2C)",
    audience: "AV Owners / Riders",
    point1: "True curbside-to-curbside experience",
    point2: "Car handles parking entirely on its own",
  },
  {
    accentColor: theme.colors.accentOrange,
    label: "Key Partners",
    audience: "Infrastructure & Data",
    point1: "Parking lot owners (municipalities, malls, airports)",
    point2: "Data aggregators (Google Maps) for lot discovery",
  },
];

const StakeholdersSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title slides in
  const titleAnim = useSlideIn(5, "up");
  const titleStyle: React.CSSProperties = {
    fontSize: 52,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 56,
    letterSpacing: -1,
    ...titleAnim,
  };

  const columnsContainerStyle: React.CSSProperties = {
    display: "flex",
    gap: 32,
    justifyContent: "center",
    alignItems: "stretch",
    width: "100%",
    maxWidth: 1400,
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
        <h1 style={titleStyle}>Stakeholders &amp; Impacts</h1>

        <div style={columnsContainerStyle}>
          {columns.map((col, i) => {
            const delay = useStagger(i, 20, 12);
            const anim = useSlideIn(delay, "up");

            const cardStyle: React.CSSProperties = {
              flex: 1,
              background: "#1a2a40",
              borderRadius: 16,
              padding: "0 36px 36px 36px",
              display: "flex",
              flexDirection: "column",
              borderTop: `4px solid ${col.accentColor}`,
              boxShadow: "0 4px 30px rgba(0,0,0,0.25)",
              ...anim,
            };

            const labelStyle: React.CSSProperties = {
              fontSize: 14,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: 2,
              color: col.accentColor,
              marginTop: 28,
              marginBottom: 8,
            };

            const audienceStyle: React.CSSProperties = {
              fontSize: 24,
              fontWeight: 700,
              color: theme.colors.white,
              margin: 0,
              marginBottom: 20,
              lineHeight: 1.3,
            };

            const bulletStyle: React.CSSProperties = {
              fontSize: 17,
              fontWeight: 400,
              color: theme.colors.gray,
              lineHeight: 1.6,
              margin: 0,
              marginBottom: 12,
              paddingLeft: 16,
              borderLeft: `2px solid ${col.accentColor}33`,
            };

            return (
              <div key={i} style={cardStyle}>
                <p style={labelStyle}>{col.label}</p>
                <p style={audienceStyle}>{col.audience}</p>
                <p style={bulletStyle}>{col.point1}</p>
                <p style={bulletStyle}>{col.point2}</p>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default StakeholdersSlide;
