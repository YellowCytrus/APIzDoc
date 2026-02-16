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

// Element DTOs (API responses)
export interface DocumentStyles {
  font_size: number;
  line_spacing: number;
}

export interface DocumentStylesUpdate {
  font_size?: number;
  line_spacing?: number;
}

export interface HeadingStyles {
  numbering: string;
}

export interface HeadingStylesUpdate {
  numbering?: string;
}

export interface TableStyles {
  stroke: string;
}

export interface TableStylesUpdate {
  stroke?: string;
}

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

export interface NumberedListStyles {
  tight: boolean;
  indent: number;
  body_indent: number;
  spacing: 'auto' | 'tight' | 'loose';
}

export interface NumberedListStylesUpdate {
  tight?: boolean;
  indent?: number;
  body_indent?: number;
  spacing?: 'auto' | 'tight' | 'loose';
}

export interface ParStyles {
  spacing: number;
}

export interface ParStylesUpdate {
  spacing?: number;
}

export interface QuoteStyles {
  indent: number;
}

export interface QuoteStylesUpdate {
  indent?: number;
}

export interface FigureStyles {
  width: number;
  height: number;
}

export interface FigureStylesUpdate {
  width?: number;
  height?: number;
}

export interface FootnoteStyles {
  marker_format: '1' | 'a' | 'A' | 'i' | 'I' | '*';
}

export interface FootnoteStylesUpdate {
  marker_format?: '1' | 'a' | 'A' | 'i' | 'I' | '*';
}

// Element types for preamble generation
export type ElementType =
  | 'bullet_list'
  | 'document'
  | 'figure'
  | 'footnote'
  | 'heading'
  | 'numbered_list'
  | 'par'
  | 'quote'
  | 'table';

export interface ProfileElementLike {
  element_type: ElementType;
  tight: boolean;
  marker1: string;
  marker2: string;
  marker3: string;
  indent_pt: number;
  body_indent_em: number;
  spacing: string;
  spacing_em: number;
  font_size_pt: number;
  line_spacing_em: number;
  figure_width_em: number;
  figure_height_em: number;
  table_stroke: string;
  heading_numbering: string;
  quote_indent_em: number;
  footnote_marker_fmt: string;
}
