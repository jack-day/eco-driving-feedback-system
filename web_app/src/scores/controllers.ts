import { AuthedRequest, Response } from 'express';
import { removeNullishProps, parseQueryInt } from '../utils'; 
import { getScores, addScores } from './services';

/** GET /scores */
export async function scoresGet(req: AuthedRequest, res: Response) {
    const scores = await getScores(
        req.auth.payload.sub,
        removeNullishProps({
            type: req.query.type as string,
            limit: parseQueryInt(req.query.limit),
            maxDaysAgo: parseQueryInt(req.query.maxDaysAgo),
        })
    );
    res.send(scores);
}

/** POST /scores */
export async function scoresPost(req: AuthedRequest, res: Response) {
    await addScores(req.auth.payload.sub, req.body);
    res.sendStatus(201);
}
