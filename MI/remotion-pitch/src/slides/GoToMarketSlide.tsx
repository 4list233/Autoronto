import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  AbsoluteFill,
} from "remotion";
import { theme, slideStyle } from "../utils/theme";
import { useFadeIn, useSlideIn, useScaleIn, useCountUp, useStagger, useTypewriter } from "../utils/animations";

const GoToMarketSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = useFadeIn(0);
  const phase1Slide = useSlideIn(15, "left");
  const phase2Slide = useSlideIn(15, "right");

  const revenueDelay1 = useStagger(0, 50, 10);
  const revenueDelay2 = useStagger(1, 50, 10);
  const revenueDelay3 = useStagger(2, 50, 10);
  const revenue1Opacity = useFadeIn(revenueDelay1);
  const revenue2Opacity = useFadeIn(revenueDelay2);
  const revenue3Opacity = useFadeIn(revenueDelay3);
  const moatOpacity = useFadeIn(85);

  const titleStyle: React.CSSProperties = {
    fontSize: 48,
    fontWeight: 700,
    color: theme.colors.white,
    opacity: titleOpacity,
    textAlign: "center",
    margin: 0,
    marginBottom: 32,
    letterSpacing: -1,
  };

  const cardBase: React.CSSProperties = {
    flex: 1,
    background: `${theme.colors.primary}CC`,
    borderRadius: 16,
    padding: 28,
    display: "flex",
    flexDirection: "column",
    gap: 12,
    backdropFilter: "blur(10px)",
  };

  const phase1Card: React.CSSProperties = {
    ...cardBase,
    borderLeft: `4px solid ${theme.colors.accent}`,
    boxShadow: `0 0 30px ${theme.colors.accent}22`,
    ...phase1Slide,
  };

  const phase2Card: React.CSSProperties = {
    ...cardBase,
    borderLeft: `4px solid ${theme.colors.accentGreen}`,
    boxShadow: `0 0 30px ${theme.colors.accentGreen}22`,
    ...phase2Slide,
  };

  const phaseLabel = (color: string): React.CSSProperties => ({
    fontSize: 13,
    fontWeight: 700,
    color,
    textTransform: "uppercase",
    letterSpacing: 2,
  });

  const phaseTitle: React.CSSProperties = {
    fontSize: 22,
    fontWeight: 700,
    color: theme.colors.white,
    margin: 0,
    lineHeight: 1.3,
  };

  const bulletStyle: React.CSSProperties = {
    fontSize: 15,
    color: theme.colors.gray,
    lineHeight: 1.6,
    margin: 0,
  };

  const revenueChip = (opacity: number): React.CSSProperties => ({
    background: `${theme.colors.secondary}AA`,
    borderRadius: 10,
    padding: "10px 18px",
    fontSize: 15,
    color: theme.colors.white,
    fontWeight: 500,
    opacity,
    textAlign: "center",
    border: `1px solid ${theme.colors.accent}33`,
  });

  const moatStyle: React.CSSProperties = {
    fontSize: 15,
    fontWeight: 600,
    color: theme.colors.highlight,
    textAlign: "center",
    opacity: moatOpacity,
    padding: "12px 24px",
    background: `${theme.colors.highlight}11`,
    borderRadius: 10,
    border: `1px solid ${theme.colors.highlight}44`,
    maxWidth: 800,
  };

  return (
    <AbsoluteFill style={slideStyle}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          width: "100%",
          height: "100%",
          justifyContent: "flex-start",
          alignItems: "center",
          paddingTop: 40,
        }}
      >
        <h1 style={titleStyle}>Go-to-Market: Two-Phase Strategy</h1>

        {/* Phase cards */}
        <div style={{ display: "flex", gap: 28, width: "100%", maxWidth: 1600, marginBottom: 28 }}>
          <div style={phase1Card}>
            <span style={phaseLabel(theme.colors.accent)}>Phase 1 &mdash; 2026-2028</span>
            <h3 style={phaseTitle}>Bridge Revenue via Smart Parking App</h3>
            <p style={bulletStyle}>
              &bull; Launch as SpotHero-style aggregator<br />
              &bull; 15-30% dynamic commission per transaction<br />
              &bull; Build brand, sign lot partnerships, validate OBU/RSU hardware
            </p>
          </div>
          <div style={phase2Card}>
            <span style={phaseLabel(theme.colors.accentGreen)}>Phase 2 &mdash; 2028+</span>
            <h3 style={phaseTitle}>Full Autonomous Parking Platform</h3>
            <p style={bulletStyle}>
              &bull; L4/L5 integration play<br />
              &bull; OEM SDK licensing + per-vehicle subscriptions<br />
              &bull; Premium lot access tiers
            </p>
          </div>
        </div>

        {/* Revenue streams */}
        <div style={{ display: "flex", gap: 20, width: "100%", maxWidth: 1600, marginBottom: 20 }}>
          <div style={revenueChip(revenue1Opacity)}>
            15-30% commission on parking transactions
          </div>
          <div style={revenueChip(revenue2Opacity)}>
            $50/gate/month SaaS fee for lot operators
          </div>
          <div style={revenueChip(revenue3Opacity)}>
            OEM licensing fees for SDK access
          </div>
        </div>

        {/* Competitive moat */}
        <div style={moatStyle}>
          Competitive Moat: RSU hardware creates physical switching costs — once installed, lots are locked in
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default GoToMarketSlide;
