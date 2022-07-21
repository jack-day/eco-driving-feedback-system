import express from 'express';
import api from './api';
import swagger from './swagger';
import config from './config';
import { handleErrors } from './errors';

const PORT = 8080;
const app = express();

app.use('/', express.static('public', { extensions: ['html'] }));
app.use('/api', api);
app.use('/api-docs', swagger);

app.get('/auth/config', (req, res) => {
    res.send(config.auth);
});

app.use(handleErrors);

app.listen(PORT, () => {
    console.log(`EcoDriven Launched, Listening on port ${PORT}`);
});
