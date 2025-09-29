import { clsx } from 'clsx';

/**
 * Merge class names conditionally.
 */
export function cn(...inputs: any[]) {
  return clsx(inputs);
}