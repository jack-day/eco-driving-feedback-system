const auth0script = document.createElement('script');
auth0script.src = 'https://cdn.auth0.com/js/auth0-spa-js/1.13/auth0-spa-js.production.js';
document.body.append(auth0script);

const script = document.createElement('script');
script.type = 'module';
script.src = '/api-docs/js/swagger.js';
document.body.append(script);
