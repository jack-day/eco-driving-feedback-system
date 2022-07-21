/**
 * @module
 * @description Swagger functionality to host API documentation.
 */
import path from 'path';
import { readFileSync } from 'fs';
import { Router } from 'express';
import YAML from 'yaml';
import { serve, setup, JsonObject } from 'swagger-ui-express';

/**
 * Combines objects by adding all properties from one object to another.
 * 
 * Needed for adding values to Swagger's fixed fields from multiple files. For
 * example, most of the imported files will contain the 'paths' field to specify
 * available paths and operations for the API. However, there can only be one
 * 'paths' field in the final yaml file given to swagger, thus we must combine
 * all of the imported 'paths' objects.
 */
function combineObjects(target: JsonObject, objToCopy: JsonObject): void {
    for (const [key, value] of Object.entries(objToCopy)) {
        if (
            target[key] &&
            typeof target[key] === 'object' &&
            typeof value === 'object'
        ) {
            combineObjects(target[key], value);
        } else {
            target[key] = value;
        }
    }
}

/**
 * Loads YAML file imports by:
 * - Identifying members with the key '$import'
 * - Processing it's value as either a string or array of strings containing the
 *   path to each yaml file to import.
 * - Importing the specified yaml file in-place at the same depth level
 * - Finally removing $import member
 * 
 * Custom import member structure: `$import: string | [string]`
 * 
 * For example:
 * ```
 * $import: example/swagger.yml
 * ```
 * OR
 * ```
 * $import:
 *   - example.yml
 *   - example/swagger.yml
 * ```
 * 
 * @param yml YAML parsed as a JSON object
 */
function loadImports(yml: JsonObject): void {
    /* eslint-disable-next-line prefer-const */
    for (let [key, value] of Object.entries(yml)) {
        if (typeof value === 'object' && !Array.isArray(value)) {
            loadImports(value);
        } else if (key === '$import') {
            if (typeof value === 'string') value = [value];

            for (const file of value) {
                const filepath = path.resolve('./swagger', file);
                const fileContents = readFileSync(filepath, 'utf8');
                const importedYml = YAML.parse(fileContents);
                loadImports(importedYml);
                combineObjects(yml, importedYml);
            }

            delete (yml[key]);
        }
    }
}

const swaggerPath = path.resolve('./swagger/index.yaml');
const swaggerYaml: JsonObject = YAML.parse(readFileSync(swaggerPath, 'utf8'));
loadImports(swaggerYaml);

const router = Router();
router.use('/', serve);
router.get('/', setup(swaggerYaml, {
    customSiteTitle: 'API Reference - EcoDriven',
    customfavIcon: '/assets/img/logo-icon.svg',
    customCssUrl: '/api-docs/css/index.css',
    customJs: '/api-docs/js/index.js',
}));

export default router;
