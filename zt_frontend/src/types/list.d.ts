/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

/**
 * Unique id for a component
 */
export type Id = string;
/**
 * Optional variable name associated with a component
 */
export type VariableName = string;
/**
 * Vue component name
 */
export type Component = string;
/**
 * List of child component ids to be placed within the card
 */
export type Childcomponents = string[];
/**
 * Background color of the card
 */
export type Color = string;
/**
 * Elevation level of the card. Must be between 0 and 24
 */
export type Elevation = number;
/**
 * Density of the component
 */
export type Density = "default" | "comfortable" | "compact";
/**
 * Width of the List
 */
export type Width = number | string;
/**
 * Height of the List
 */
export type Height = number | string;

/**
 * A card is a container for components that should be displayed together.
 * Any child components will be placed in their own row within the card and take up the full width
 */
export interface ListComponent {
  id: Id;
  variable_name?: VariableName;
  component?: Component;
  childComponents?: Childcomponents;
  color?: Color;
  elevation?: Elevation;
  density?: Density;
  width?: Width;
  height?: Height;
  [k: string]: unknown;
}