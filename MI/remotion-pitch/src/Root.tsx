import React from "react";
import { Composition } from "remotion";
import { AutoParkPitchDeck } from "./Composition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AutoParkPitchDeck"
        component={AutoParkPitchDeck}
        durationInFrames={30 * 24 * 15}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
