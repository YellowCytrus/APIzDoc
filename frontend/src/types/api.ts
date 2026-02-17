// Profile
export interface Profile {
  id: number;
  name: string;
}

export interface ProfileCreate {
  name: string;
}

export interface ProfileUpdate {
  name?: string;
}

// ---------------------------------------------------------------------------
// Element style DTOs (match backend Pydantic schemas)
// ---------------------------------------------------------------------------

export interface BulletListStyles {
  tight: boolean;
  marker: string[];
  indent: number;
  body_indent: number;
  spacing: 'auto' | 'tight' | 'loose';
}

export interface BulletListStylesUpdate {
  tight?: boolean;
  marker?: string[];
  indent?: number;
  body_indent?: number;
  spacing?: 'auto' | 'tight' | 'loose';
}

export interface DocumentStyles {
  font_size: number;
  line_spacing: number;
  font: string;
  weight: string;
  style: string;
  fill: string;
  lang: string;
  region: string | null;
  tracking: number;
  word_spacing: number;
  hyphenate: boolean | null;
  ligatures: boolean;
  number_type: string;
  number_width: string;
}

export interface DocumentStylesUpdate {
  font_size?: number;
  line_spacing?: number;
  font?: string;
  weight?: string;
  style?: string;
  fill?: string;
  lang?: string;
  region?: string | null;
  tracking?: number;
  word_spacing?: number;
  hyphenate?: boolean | null;
  ligatures?: boolean;
  number_type?: string;
  number_width?: string;
}

export interface FigureStyles {
  width: number;
  height: number;
  placement: string;
  gap: number;
  outlined: boolean;
  fit: string;
}

export interface FigureStylesUpdate {
  width?: number;
  height?: number;
  placement?: string;
  gap?: number;
  outlined?: boolean;
  fit?: string;
}

export interface FootnoteStyles {
  marker_format: '1' | 'a' | 'A' | 'i' | 'I' | '*';
  clearance: number;
  gap: number;
  indent: number;
}

export interface FootnoteStylesUpdate {
  marker_format?: '1' | 'a' | 'A' | 'i' | 'I' | '*';
  clearance?: number;
  gap?: number;
  indent?: number;
}

export interface HeadingStyles {
  numbering: string;
  outlined: boolean;
  bookmarked: string;
  offset: number;
  hanging_indent: number | null;
}

export interface HeadingStylesUpdate {
  numbering?: string;
  outlined?: boolean;
  bookmarked?: string;
  offset?: number;
  hanging_indent?: number | null;
}

export interface NumberedListStyles {
  tight: boolean;
  indent: number;
  body_indent: number;
  spacing: 'auto' | 'tight' | 'loose';
  numbering: string;
  start: number | null;
  full: boolean;
  reversed: boolean;
  number_align: string;
}

export interface NumberedListStylesUpdate {
  tight?: boolean;
  indent?: number;
  body_indent?: number;
  spacing?: 'auto' | 'tight' | 'loose';
  numbering?: string;
  start?: number | null;
  full?: boolean;
  reversed?: boolean;
  number_align?: string;
}

export interface OutlineStyles {
  depth: number | null;
  indent: string;
}

export interface OutlineStylesUpdate {
  depth?: number | null;
  indent?: string;
}

export interface PageStyles {
  paper: string;
  flipped: boolean;
  margin_top: number;
  margin_bottom: number;
  margin_left: number;
  margin_right: number;
  columns: number;
  numbering: string;
  number_align: string;
}

export interface PageStylesUpdate {
  paper?: string;
  flipped?: boolean;
  margin_top?: number;
  margin_bottom?: number;
  margin_left?: number;
  margin_right?: number;
  columns?: number;
  numbering?: string;
  number_align?: string;
}

export interface ParStyles {
  spacing: number;
  first_line_indent: number;
  hanging_indent: number;
  justify: boolean;
  linebreaks: string;
}

export interface ParStylesUpdate {
  spacing?: number;
  first_line_indent?: number;
  hanging_indent?: number;
  justify?: boolean;
  linebreaks?: string;
}

export interface QuoteStyles {
  indent: number;
  block: boolean;
  quotes: string;
}

export interface QuoteStylesUpdate {
  indent?: number;
  block?: boolean;
  quotes?: string;
}

export interface RawStyles {
  tab_size: number;
  align: string;
  theme: string;
}

export interface RawStylesUpdate {
  tab_size?: number;
  align?: string;
  theme?: string;
}

export interface StrongStyles {
  delta: number;
}

export interface StrongStylesUpdate {
  delta?: number;
}

export interface TableStyles {
  stroke: string;
  align: string;
  inset: string;
  fill: string;
}

export interface TableStylesUpdate {
  stroke?: string;
  align?: string;
  inset?: string;
  fill?: string;
}

export interface TermsStyles {
  tight: boolean;
  indent: number;
  hanging_indent: number;
  spacing: 'auto' | 'tight' | 'loose';
}

export interface TermsStylesUpdate {
  tight?: boolean;
  indent?: number;
  hanging_indent?: number;
  spacing?: 'auto' | 'tight' | 'loose';
}

// Element types for API paths
export type ElementType =
  | 'bullet_list'
  | 'document'
  | 'figure'
  | 'footnote'
  | 'heading'
  | 'numbered_list'
  | 'outline'
  | 'page'
  | 'par'
  | 'quote'
  | 'raw'
  | 'strong'
  | 'table'
  | 'terms';
