import React from 'react';
import {Composition} from 'remotion';
import {AirPodsAd} from './AirPodsAd';
import {W, H, FPS, DURATION} from './theme';

export const Root: React.FC = () => (
  <Composition
    id="AirPodsAd"
    component={AirPodsAd}
    durationInFrames={DURATION}
    fps={FPS}
    width={W}
    height={H}
  />
);
