import { removeNullishProps, parseQueryInt } from '../src/utils';

describe('removeNullishProps', () => {
    it('removes null properties', () => {
        const result = removeNullishProps({
            stay: 'not null',
            remove: null,
        });
        expect(result).toStrictEqual({ stay: 'not null' });
    });

    it('removes undefined properties', () => {
        const result = removeNullishProps({
            stay: 'not null',
            remove: undefined,
        });
        expect(result).toStrictEqual({ stay: 'not null' });
    });
    
    it('returns an empty object when all properties are nullish', () => {
        const result = removeNullishProps({
            null: null,
            undefined: undefined,
        });
        expect(result).toStrictEqual({});
    });
});

describe('parseQueryInt', () => {
    it('returns an integer when given a integer string', () => {
        expect(parseQueryInt('5')).toBe(5);
    });

    it('returns 0 when given a 0 as a string', () => {
        expect(parseQueryInt('0')).toBe(0);
    });

    it('returns an integer when given a float string', () => {
        expect(parseQueryInt('5.8')).toBe(5);
    });

    it('returns NaN when given an non-numerical string', () => {
        expect(parseQueryInt('invalid')).toBe(NaN);
    });

    it('returns undefined when given an empty string', () => {
        expect(parseQueryInt('')).toBe(undefined);
    });

    it('returns undefined when given undefined', () => {
        expect(parseQueryInt(undefined)).toBeUndefined();
    });

    it('returns undefined when given null', () => {
        expect(parseQueryInt(null)).toBeUndefined();
    });
});
