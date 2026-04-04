import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const useFadeIn = (delay = 0) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return interpolate(frame - delay, [0, fps * 0.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

export const useSlideIn = (
  delay = 0,
  direction: "left" | "right" | "up" | "down" = "up"
) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 15, stiffness: 120, mass: 0.8 },
  });

  const offsets = {
    left: { x: interpolate(progress, [0, 1], [-120, 0]), y: 0 },
    right: { x: interpolate(progress, [0, 1], [120, 0]), y: 0 },
    up: { x: 0, y: interpolate(progress, [0, 1], [80, 0]) },
    down: { x: 0, y: interpolate(progress, [0, 1], [-80, 0]) },
  };

  return {
    transform: `translate(${offsets[direction].x}px, ${offsets[direction].y}px)`,
    opacity: interpolate(progress, [0, 0.3], [0, 1], {
      extrapolateRight: "clamp",
    }),
  };
};

export const useScaleIn = (delay = 0) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 100, mass: 0.6 },
  });

  return {
    transform: `scale(${interpolate(progress, [0, 1], [0.7, 1])})`,
    opacity: interpolate(progress, [0, 0.4], [0, 1], {
      extrapolateRight: "clamp",
    }),
  };
};

export const useCountUp = (target: number, delay = 0, duration = 1.5) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = interpolate(
    frame - delay,
    [0, fps * duration],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const eased = 1 - Math.pow(1 - progress, 3);
  return Math.round(target * eased);
};

export const useStagger = (index: number, baseDelay = 0, gap = 8) => {
  return baseDelay + index * gap;
};

export const useTypewriter = (text: string, delay = 0, charsPerFrame = 0.8) => {
  const frame = useCurrentFrame();
  const adjustedFrame = Math.max(0, frame - delay);
  const numChars = Math.min(
    Math.floor(adjustedFrame * charsPerFrame),
    text.length
  );
  return text.slice(0, numChars);
};

export const useProgressBar = (delay = 0, duration = 1) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return interpolate(
    frame - delay,
    [0, fps * duration],
    [0, 100],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
};
