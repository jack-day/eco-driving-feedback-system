import { AuthedRequest, Response } from 'express';
import { removeNullishProps, parseQueryInt } from '../utils'; 
import * as journeys from './services';

/** GET /journeys/ */
export async function journeysGet(req: AuthedRequest, res: Response) {
    const limit = parseQueryInt(req.query.limit);
    const jrnys = await journeys.getJourneys(
        req.auth.payload.sub,
        removeNullishProps({
            limit: limit ? limit + 1 : undefined,
            offset: parseQueryInt(req.query.offset),
        })
    );

    if (limit) {
        const moreEntries = jrnys.length > limit;
        res.set('More-Entries', [`${moreEntries}`]);
        if (moreEntries) jrnys.pop();
    }

    res.send(jrnys);
}

/** POST /journeys/ */
export async function journeysPost(req: AuthedRequest, res: Response) {
    const id = await journeys.createJourney(req.auth.payload.sub, req.body);
    res.status(201).send({ id });
}

/** GET /journeys/:journeyID */
export async function journeyGet(req: AuthedRequest, res: Response) {
    const journey = await journeys.getJourney(
        req.auth.payload.sub,
        parseInt(req.params.journeyID)
    );
   
    if (journey) {
        res.send(journey);
    } else {
        res.status(404).send('Journey does not exist');
    }
}

/** PUT /journeys/:journeyID */
export async function journeysPut(req: AuthedRequest, res: Response) {
    await journeys.updateJourney(
        req.auth.payload.sub,
        parseInt(req.params.journeyID),
        req.body
    );
    res.sendStatus(204);
}
