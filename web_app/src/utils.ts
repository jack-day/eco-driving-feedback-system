/**
 * @module
 * @description Helper functions used by multiple files.
 */

/**
 * Remove properties with a value of null of undefined from an object.
 * 
 * Modified from: {@link https://medium.com/mizyind-singularity/remove-blank-attributes-from-an-object-in-typescript-with-type-safe-ad4fd78a061c}
 */
export function removeNullishProps<T>(obj: T) {
    return Object.fromEntries(
        Object.entries(obj).filter(([, val]) => val != null)
    ) as { [K in keyof T as T[K] extends null | undefined ? never : K]: T[K] };
}

/** Parses a query parameter as an integer */
export function parseQueryInt(val: any) {
    return val != undefined && val !== '' ? parseInt(val as string) : undefined;
}
