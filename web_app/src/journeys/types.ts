export interface journey {
    journeyID: number;
    start: string;
    end: string;
    distance: number;
    idleSecs: number;
    gsiAdh?: number;
}

export type journeyNoID = Omit<journey, 'journeyID'>;

export interface getJourneysOpts {
    limit?: number;
    offset?: number;
}
