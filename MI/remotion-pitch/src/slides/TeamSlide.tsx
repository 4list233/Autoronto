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

interface TeamMember {
  name: string;
  role: string;
}

const teamMembers: TeamMember[] = [
  { name: "Prithvi Seran", role: "MI Lead" },
  { name: "Amanda Liu", role: "MI Lead" },
  { name: "Forest Li", role: "Member" },
  { name: "Ailing Ji", role: "Member" },
  { name: "Nevan Kho", role: "Member" },
  { name: "Chad Paik", role: "Team Principal" },
];

const TeamCard: React.FC<{ member: TeamMember; index: number }> = ({
  member,
  index,
}) => {
  const delay = useStagger(index, 15, 10);
  const slideIn = useSlideIn(delay, "left");

  const cardStyle: React.CSSProperties = {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    padding: "28px 32px",
    borderLeft: `4px solid ${theme.colors.accent}`,
    background: `linear-gradient(135deg, ${theme.colors.secondary}88 0%, ${theme.colors.primary}66 100%)`,
    borderRadius: 12,
    backdropFilter: "blur(10px)",
    boxShadow: `0 4px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.05)`,
    ...slideIn,
  };

  const nameStyle: React.CSSProperties = {
    fontSize: 24,
    fontWeight: 700,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 6,
  };

  const roleStyle: React.CSSProperties = {
    fontSize: 16,
    fontWeight: 400,
    color: theme.colors.accent,
    margin: 0,
    letterSpacing: 0.5,
  };

  return (
    <div style={cardStyle}>
      <p style={nameStyle}>{member.name}</p>
      <p style={roleStyle}>{member.role}</p>
    </div>
  );
};

const TeamSlide: React.FC = () => {
  const titleSlide = useSlideIn(5, "left");

  const titleStyle: React.CSSProperties = {
    fontSize: 64,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 48,
    ...titleSlide,
  };

  const gridStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: 24,
    width: "100%",
    maxWidth: 1100,
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
          maxWidth: 1200,
          height: "100%",
        }}
      >
        <h1 style={titleStyle}>Our Team</h1>
        <div style={gridStyle}>
          {teamMembers.map((member, i) => (
            <TeamCard key={member.name} member={member} index={i} />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default TeamSlide;
