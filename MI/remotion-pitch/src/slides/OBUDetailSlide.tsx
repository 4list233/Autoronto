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

const components = [
  { label: "UHF RFID Tag", detail: "NXP UCODE DNA RAIN" },
  { label: "UHF Reader/Writer", detail: "SparkFun M6E Nano" },
  { label: "CAN Bus Bridge", detail: "STM32G431" },
  { label: "Placement", detail: "Connected via CAN bus, placed below dashboard" },
];

const firmwarePhases = [
  "Phase 1: Poll GPS \u2192 fetch recommendations every 100m",
  "Phase 2: Receive SSE \u2192 write parking ID to RFID tag",
  "Phase 3: Geofence detection \u2192 tag is passive for gate reader",
  "Phase 4: Park confirmed \u2192 clear tag, finalize session",
];

const OBUDetailSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSlide = useSlideIn(0, "up");

  const titleStyle: React.CSSProperties = {
    fontSize: 52,
    fontWeight: 800,
    color: theme.colors.white,
    margin: 0,
    marginBottom: 48,
    ...titleSlide,
  };

  const columnStyle: React.CSSProperties = {
    display: "flex",
    gap: 64,
    width: "100%",
    maxWidth: 1500,
    alignItems: "flex-start",
  };

  const sectionTitleStyle: React.CSSProperties = {
    fontSize: 20,
    fontWeight: 700,
    color: theme.colors.accent,
    marginBottom: 20,
    textTransform: "uppercase" as const,
    letterSpacing: 2,
  };

  // Bottom note
  const bottomDelay = 80;
  const bottomAnim = useSlideIn(bottomDelay, "up");

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
        <h1 style={titleStyle}>On-Board Unit (OBU)</h1>

        <div style={columnStyle}>
          {/* Left: Hardware components */}
          <div style={{ flex: 1 }}>
            <div style={sectionTitleStyle}>Hardware Components</div>
            {components.map((comp, i) => {
              const delay = useStagger(i, 15, 10);
              const anim = useSlideIn(delay, "left");

              return (
                <div
                  key={comp.label}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 16,
                    marginBottom: 16,
                    ...anim,
                  }}
                >
                  <div
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: theme.colors.accentGreen,
                      flexShrink: 0,
                      boxShadow: `0 0 10px ${theme.colors.accentGreen}66`,
                    }}
                  />
                  <div>
                    <span
                      style={{
                        fontSize: 18,
                        fontWeight: 700,
                        color: theme.colors.white,
                      }}
                    >
                      {comp.label}
                    </span>
                    <span
                      style={{
                        fontSize: 18,
                        fontWeight: 400,
                        color: theme.colors.gray,
                      }}
                    >
                      {" \u2014 "}
                      {comp.detail}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right: Firmware phases vertical timeline */}
          <div style={{ flex: 1 }}>
            <div style={sectionTitleStyle}>Firmware Flow</div>
            {firmwarePhases.map((phase, i) => {
              const delay = useStagger(i, 25, 12);
              const anim = useSlideIn(delay, "right");

              return (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 16,
                    marginBottom: 20,
                    ...anim,
                  }}
                >
                  {/* Timeline dot + line */}
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      flexShrink: 0,
                    }}
                  >
                    <div
                      style={{
                        width: 14,
                        height: 14,
                        borderRadius: "50%",
                        background: theme.colors.accent,
                        boxShadow: `0 0 12px ${theme.colors.accent}66`,
                      }}
                    />
                    {i < firmwarePhases.length - 1 && (
                      <div
                        style={{
                          width: 2,
                          height: 30,
                          background: `${theme.colors.accent}44`,
                          marginTop: 4,
                        }}
                      />
                    )}
                  </div>
                  <div
                    style={{
                      fontSize: 16,
                      fontWeight: 400,
                      color: theme.colors.white,
                      lineHeight: 1.5,
                      paddingTop: 0,
                    }}
                  >
                    {phase}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom integration note */}
        <div
          style={{
            marginTop: 40,
            background: "#162238",
            borderRadius: 12,
            padding: "16px 32px",
            border: `1px solid ${theme.colors.accent}44`,
            ...bottomAnim,
          }}
        >
          <span
            style={{
              fontSize: 17,
              fontWeight: 500,
              color: theme.colors.accent,
            }}
          >
            Packaged as Adaptive AUTOSAR application for OEM integration
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default OBUDetailSlide;
