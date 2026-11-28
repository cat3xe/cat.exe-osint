import React from 'react';
import {Composition} from 'remotion';
import {IphoneAd, IPHONE_AD_DURATION, FPS, WIDTH, HEIGHT} from './IphoneAd';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="IphoneAd"
    component={IphoneAd}
    durationInFrames={IPHONE_AD_DURATION}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
    defaultProps={{}}
  />
);
