/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export type Cellid = string;
export type Hidecell = boolean;

export interface HideCellRequest {
  cellId: Cellid;
  hideCell: Hidecell;
  [k: string]: unknown;
}
