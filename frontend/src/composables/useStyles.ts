import type { ElementType, ProfileElementLike } from '../types/api';
import { API_BASE } from '../config';

const ELEMENT_PATHS: ElementType[] = [
  'document',
  'heading',
  'table',
  'bullet_list',
  'numbered_list',
  'par',
  'quote',
  'figure',
  'footnote',
];

const GOST_DEFAULTS: ProfileElementLike = {
  element_type: 'document',
  tight: true,
  marker1: '- ',
  marker2: '‣',
  marker3: '–',
  indent_pt: 0,
  body_indent_em: 0.5,
  spacing: 'auto',
  spacing_em: 1,
  font_size_pt: 12,
  line_spacing_em: 1.2,
  figure_width_em: 1,
  figure_height_em: 0,
  table_stroke: '0.5pt',
  heading_numbering: '1.1.1',
  quote_indent_em: 1.5,
  footnote_marker_fmt: '1',
};

function typstStr(s: string): string {
  const escaped = s.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  return `"${escaped}"`;
}

function typstListSpacing(s: string): string {
  if (s === 'auto') return 'auto';
  if (s === 'tight') return '0.5em';
  if (s === 'loose') return '1em';
  return 'auto';
}

function bulletListLine(e: ProfileElementLike): string {
  const markers = [e.marker1, e.marker2, e.marker3];
  const markersStr = markers.map(typstStr).join(', ');
  return `#set list(tight: ${e.tight}, indent: ${e.indent_pt}pt, body-indent: ${e.body_indent_em}em, spacing: ${typstListSpacing(e.spacing)}, marker: (${markersStr}))`;
}

function documentLine(e: ProfileElementLike): string {
  return `#set text(size: ${e.font_size_pt}pt)\n#set par(leading: ${e.line_spacing_em}em)`;
}

function figureLine(e: ProfileElementLike): string {
  const w = e.figure_width_em ? `${e.figure_width_em}em` : 'auto';
  const h = e.figure_height_em ? `${e.figure_height_em}em` : 'auto';
  return `#set image(width: ${w}, height: ${h})`;
}

function footnoteLine(e: ProfileElementLike): string {
  return `#set footnote(numbering: ${typstStr(e.footnote_marker_fmt)})`;
}

function headingLine(e: ProfileElementLike): string {
  const num = e.heading_numbering !== 'none' ? typstStr(e.heading_numbering) : 'none';
  return `#set heading(numbering: ${num})`;
}

function numberedListLine(e: ProfileElementLike): string {
  return `#set enum(tight: ${e.tight}, indent: ${e.indent_pt}pt, body-indent: ${e.body_indent_em}em, spacing: ${typstListSpacing(e.spacing)})`;
}

function parLine(e: ProfileElementLike): string {
  return `#set par(spacing: ${e.spacing_em}em)`;
}

function quoteLine(e: ProfileElementLike): string {
  return `#set quote(block: true)\n#show quote: set pad(x: ${e.quote_indent_em}em)`;
}

function tableLine(e: ProfileElementLike): string {
  return `#set table(stroke: ${e.table_stroke})`;
}

const BUILDERS: Record<ElementType, (e: ProfileElementLike) => string> = {
  bullet_list: bulletListLine,
  document: documentLine,
  figure: figureLine,
  footnote: footnoteLine,
  heading: headingLine,
  numbered_list: numberedListLine,
  par: parLine,
  quote: quoteLine,
  table: tableLine,
};

function buildTypstPreamble(elements: Map<ElementType, ProfileElementLike>): string {
  const lines: string[] = [];
  for (const type of ELEMENT_PATHS) {
    const e = elements.get(type);
    if (!e) continue;
    const fn = BUILDERS[type];
    if (!fn) continue;
    const part = fn(e);
    lines.push(...part.split('\n'));
  }
  return (lines.length ? lines.join('\n') + '\n' : '');
}

function dtoToElement(
  type: ElementType,
  dto: Record<string, unknown>
): ProfileElementLike {
  const base = { ...GOST_DEFAULTS, element_type: type };
  switch (type) {
    case 'document':
      return {
        ...base,
        font_size_pt: (dto.font_size as number) ?? 12,
        line_spacing_em: (dto.line_spacing as number) ?? 1.2,
      };
    case 'heading':
      return { ...base, heading_numbering: (dto.numbering as string) ?? '1.1.1' };
    case 'table':
      return { ...base, table_stroke: (dto.stroke as string) ?? '0.5pt' };
    case 'bullet_list':
      const bl = dto;
      const m = (bl.marker as string[]) ?? ['- ', '‣', '–'];
      return {
        ...base,
        tight: (bl.tight as boolean) ?? true,
        marker1: m[0] ?? '- ',
        marker2: m[1] ?? '‣',
        marker3: m[2] ?? '–',
        indent_pt: (bl.indent as number) ?? 0,
        body_indent_em: (bl.body_indent as number) ?? 0.5,
        spacing: (bl.spacing as string) ?? 'auto',
      };
    case 'numbered_list':
      const nl = dto;
      return {
        ...base,
        tight: (nl.tight as boolean) ?? true,
        indent_pt: (nl.indent as number) ?? 0,
        body_indent_em: (nl.body_indent as number) ?? 0.5,
        spacing: (nl.spacing as string) ?? 'auto',
      };
    case 'par':
      return { ...base, spacing_em: (dto.spacing as number) ?? 1 };
    case 'quote':
      return { ...base, quote_indent_em: (dto.indent as number) ?? 1.5 };
    case 'figure':
      const f = dto;
      return {
        ...base,
        figure_width_em: (f.width as number) ?? 1,
        figure_height_em: (f.height as number) ?? 0,
      };
    case 'footnote':
      return { ...base, footnote_marker_fmt: (dto.marker_format as string) ?? '1' };
    default:
      return base as ProfileElementLike;
  }
}

export async function loadProfileStyles(profileId: number): Promise<string> {
  const elements = new Map<ElementType, ProfileElementLike>();

  await Promise.all(
    ELEMENT_PATHS.map(async (type) => {
      try {
        const res = await fetch(`${API_BASE}/profiles/${profileId}/${type}`);
        if (res.ok) {
          const dto = await res.json();
          elements.set(type, dtoToElement(type, dto));
        } else {
          elements.set(type, { ...GOST_DEFAULTS, element_type: type });
        }
      } catch {
        elements.set(type, { ...GOST_DEFAULTS, element_type: type });
      }
    })
  );

  return buildTypstPreamble(elements);
}
