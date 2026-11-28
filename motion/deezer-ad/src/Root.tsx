import React from 'react';
import {Composition} from 'remotion';
import {DeezerAd, DURATION, FPS, WIDTH, HEIGHT} from './DeezerAd';

export const RemotionRoot: React.FC = () => (
  <Composition id="DeezerAd" component={DeezerAd} durationInFrames={DURATION} fps={FPS} width={WIDTH} height={HEIGHT} defaultProps={{}} />
);
