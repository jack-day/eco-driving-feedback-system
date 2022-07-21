import { AuthedRequest, Response } from 'express';
import * as users from './services';

/** POST /users/ */
export async function usersPost(req: AuthedRequest, res: Response) {
    await users.createUser(req.auth.payload.sub);
    res.sendStatus(201);
}

/** DELETE /myself/ */
export async function myselfDelete(req: AuthedRequest, res: Response) {
    await users.deleteUser(req.auth.payload.sub);
    res.sendStatus(200);
}


/** GET /myself/registered */
export async function myselfRegistered(req: AuthedRequest, res: Response) {
    const registered = await users.userExists(req.auth.payload.sub);
    res.sendStatus(registered ? 200 : 204);
}
