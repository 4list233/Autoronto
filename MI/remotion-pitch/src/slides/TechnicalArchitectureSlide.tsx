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

interface NodeBoxProps {
  label: string;
  color: string;
  delay: number;
  width?: number;
  height?: number;
  subItems?: string[];
  children?: React.ReactNode;
}

const NodeBox: React.FC<NodeBoxProps> = ({
  label,
  color,
  delay,
  width = 200,
  height,
  subItems,
}) => {
  const anim = useScaleIn(delay);

  const style: React.CSSProperties = {
    width,
    minHeight: height || 60,
    background: "#162238",
    border: `2px solid ${color}`,
    borderRadius: 12,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "14px 16px",
    boxSizing: "border-box" as const,
    boxShadow: `0 0 20px ${color}33`,
    ...anim,
  };

  return (
    <div style={style}>
      <div
        style={{
          fontSize: 16,
          fontWeight: 700,
          color,
          textAlign: "center" as const,
          marginBottom: subItems ? 10 : 0,
        }}
      >
        {label}
      </div>
      {subItems &&
        subItems.map((item) => (
          <div
            key={item}
            style={{
              fontSize: 13,
              fontWeight: 400,
              color: theme.colors.gray,
              marginTop: 4,
            }}
          >
            {item}
          </div>
        ))}
    </div>
  );
};

const ConnectionLine: React.FC<{
  delay: number;
  width?: number;
  height?: number;
  vertical?: boolean;
  label?: string;
  color?: string;
}> = ({
  delay,
  width = 80,
  height = 3,
  vertical = false,
  label,
  color = theme.colors.gray,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = interpolate(frame - delay, [0, fps * 0.4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const lineStyle: React.CSSProperties = vertical
    ? {
        width: 3,
        height: interpolate(progress, [0, 1], [0, height]),
        background: `${color}88`,
        borderRadius: 2,
      }
    : {
        width: interpolate(progress, [0, 1], [0, width]),
        height: 3,
        background: `${color}88`,
        borderRadius: 2,
      };

  const labelOpacity = interpolate(progress, [0.5, 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        display: "flex",
        flexDirection: vertical ? "column" : "row",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
      }}
    >
      <div style={lineStyle} />
      {label && (
        <div
          style={{
            position: "absolute",
            top: vertical ? "50%" : -20,
            left: vertical ? 10 : "50%",
            transform: vertical
              ? "translateY(-50%)"
              : "translateX(-50%)",
            fontSize: 11,
            fontWeight: 600,
            color: theme.colors.accent,
            whiteSpace: "nowrap",
            opacity: labelOpacity,
          }}
        >
          {label}
        </div>
      )}
    </div>
  );
};

const TechnicalArchitectureSlide: React.FC = () => {
  const titleSlide = useSlideIn(0, "up");

  const titleStyle: React.CSSProperties = {
    fontSize: 52,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 48,
    ...titleSlide,
  };

  // Layout constants
  const cloudColor = theme.colors.accent;
  const vehicleColor = theme.colors.accentGreen;
  const infraColor = theme.colors.accentOrange;

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
        <h1 style={titleStyle}>Technical Architecture</h1>

        {/* Diagram container */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 0,
            width: "100%",
            maxWidth: 1400,
          }}
        >
          {/* Top row: Mobile App — Cloud — Infotainment */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 0,
            }}
          >
            <NodeBox
              label="Mobile App"
              color={cloudColor}
              delay={10}
              width={180}
            />
            <ConnectionLine
              delay={25}
              width={80}
              label="HTTPS"
              color={cloudColor}
            />
            <NodeBox
              label="Cloud Backend (AWS)"
              color={cloudColor}
              delay={15}
              width={280}
              subItems={["ECS (App)", "RDS (Database)", "SageMaker (ML)"]}
            />
            <ConnectionLine
              delay={30}
              width={80}
              label="HTTPS"
              color={cloudColor}
            />
            <NodeBox
              label="Infotainment"
              color={cloudColor}
              delay={20}
              width={180}
            />
          </div>

          {/* Vertical connections from Cloud down */}
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              width: "100%",
              gap: 500,
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <ConnectionLine
                delay={40}
                height={60}
                vertical
                color={infraColor}
                label="LTE/HTTP"
              />
            </div>
          </div>

          {/* Bottom row: Vehicle side and Infrastructure side */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 0,
            }}
          >
            {/* Vehicle cluster */}
            <NodeBox
              label="Vehicle"
              color={vehicleColor}
              delay={45}
              width={160}
            />
            <ConnectionLine
              delay={55}
              width={60}
              label="CAN Bus"
              color={vehicleColor}
            />
            <NodeBox
              label="OBU"
              color={vehicleColor}
              delay={50}
              width={160}
            />

            {/* OBU <-> RSU connection */}
            <ConnectionLine
              delay={65}
              width={140}
              label="UHF RFID / C-V2X PC5"
              color={theme.colors.highlight}
            />

            {/* Infrastructure cluster */}
            <NodeBox
              label="RSU"
              color={infraColor}
              delay={55}
              width={160}
            />
            <ConnectionLine
              delay={70}
              width={60}
              label="Relay"
              color={infraColor}
            />
            <NodeBox
              label="Parking Gate"
              color={infraColor}
              delay={60}
              width={160}
            />
          </div>

          {/* Legend */}
          <div
            style={{
              display: "flex",
              gap: 32,
              marginTop: 40,
              opacity: useFadeIn(75),
            }}
          >
            {[
              { color: cloudColor, label: "Cloud Layer" },
              { color: vehicleColor, label: "Vehicle Layer" },
              { color: infraColor, label: "Infrastructure Layer" },
            ].map((item) => (
              <div
                key={item.label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                <div
                  style={{
                    width: 14,
                    height: 14,
                    borderRadius: 3,
                    background: item.color,
                  }}
                />
                <span
                  style={{
                    fontSize: 14,
                    color: theme.colors.gray,
                    fontWeight: 500,
                  }}
                >
                  {item.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default TechnicalArchitectureSlide;
