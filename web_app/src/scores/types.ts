export interface scores {
    calculatedAt: string;
    ecoDriving: number;
    drivAccSmoothness?: number;
    startAccSmoothness?: number;
    decSmoothness?: number;
    gsiAdh?: number;
    speedLimitAdh?: number;
    motorwaySpeed?: number;
    idleDuration?: number;
    journeyIdlePct?: number;
    journeyDistance?: number;
}

export interface getScoresOpts {
    type?: string;
    limit?: number;
    maxDaysAgo?: number;
}
