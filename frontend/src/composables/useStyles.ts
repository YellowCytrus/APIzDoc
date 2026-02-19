import type { ElementType } from '../types/api';
import { API_BASE } from '../config';

const ALL_ELEMENT_PATHS: ElementType[] = [
  'page',
  'document',
  'par',
  'heading',
  'heading_1',
  'heading_2',
  'heading_3',
  'heading_4',
  'heading_5',
  'heading_6',
  'bullet_list',
  'numbered_list',
  'table',
  'figure',
  'footnote',
  'quote',
  'raw',
  'equation',
  'terms',
  'outline',
];

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

type DTO = Record<string, unknown>;

function pageLine(e: DTO): string {
  const args: string[] = [typstStr(e.paper as string ?? 'a4')];
  if (e.flipped) args.push('flipped: true');
  const mp: string[] = [];
  if ((e.margin_top as number) !== 2.5) mp.push(`top: ${e.margin_top}cm`);
  if ((e.margin_bottom as number) !== 2.5) mp.push(`bottom: ${e.margin_bottom}cm`);
  if ((e.margin_left as number) !== 2.5) mp.push(`left: ${e.margin_left}cm`);
  if ((e.margin_right as number) !== 2.5) mp.push(`right: ${e.margin_right}cm`);
  if (mp.length) args.push(`margin: (${mp.join(', ')})`);
  if ((e.columns as number) !== 1) args.push(`columns: ${e.columns}`);
  if (e.numbering !== 'none') args.push(`numbering: ${typstStr(e.numbering as string)}`);
  if (e.number_align !== 'center+bottom') args.push(`number-align: ${e.number_align}`);
  return `#set page(${args.join(', ')})`;
}

function documentLine(e: DTO): string {
  const ta: string[] = [`size: ${e.font_size ?? 12}pt`];
  if (e.font && e.font !== 'libertinus serif') ta.push(`font: ${typstStr(e.font as string)}`);
  if (e.weight && e.weight !== 'regular') ta.push(`weight: ${typstStr(e.weight as string)}`);
  if (e.style && e.style !== 'normal') ta.push(`style: ${typstStr(e.style as string)}`);
  if (e.fill && e.fill !== 'black') ta.push(`fill: ${e.fill}`);
  if (e.lang && e.lang !== 'en') ta.push(`lang: ${typstStr(e.lang as string)}`);
  if (e.tracking && (e.tracking as number) !== 0) ta.push(`tracking: ${e.tracking}pt`);
  if (e.word_spacing && (e.word_spacing as number) !== 100) ta.push(`spacing: ${e.word_spacing}%`);
  if (!e.ligatures && e.ligatures !== undefined) ta.push('ligatures: false');
  return `#set text(${ta.join(', ')})\n#set par(leading: ${e.line_spacing ?? 1.2}em)`;
}

function parLine(e: DTO): string {
  const a: string[] = [`spacing: ${e.spacing ?? 1}em`];
  if (e.first_line_indent && (e.first_line_indent as number) !== 0) a.push(`first-line-indent: (amount: ${e.first_line_indent}em, all: true)`);
  if (e.hanging_indent && (e.hanging_indent as number) !== 0) a.push(`hanging-indent: ${e.hanging_indent}em`);
  if (e.justify) a.push('justify: true');
  if (e.linebreaks && e.linebreaks !== 'auto') a.push(`linebreaks: ${typstStr(e.linebreaks as string)}`);
  return `#set par(${a.join(', ')})`;
}

function headingLine(e: DTO): string {
  const num = (e.numbering as string) ?? '1.1.1';
  return num === 'none'
    ? '#set heading(numbering: none)'
    : `#set heading(numbering: ${typstStr(num)})`;
}

function headingLevelLine(e: DTO, level: number): string {
  const args: string[] = [];
  if (e.outlined === false) args.push('outlined: false');
  if (e.bookmarked && e.bookmarked !== 'auto') args.push(`bookmarked: ${e.bookmarked}`);
  if (e.offset && (e.offset as number) !== 0) args.push(`offset: ${e.offset}`);
  const suffix = args.length ? `, ${args.join(', ')}` : '';
  return `#show heading.where(level: ${level}): it => heading(it.body${suffix})`;
}

function equationLine(_e: DTO): string {
  return '';
}

function bulletListLine(e: DTO): string {
  const markers = (e.marker as string[]) ?? ['- ', '‣', '–'];
  const markersStr = markers.map(typstStr).join(', ');
  return `#set list(tight: ${e.tight ?? true}, indent: ${e.indent ?? 0}pt, body-indent: ${e.body_indent ?? 0.5}em, spacing: ${typstListSpacing((e.spacing as string) ?? 'auto')}, marker: (${markersStr}))`;
}

function numberedListLine(e: DTO): string {
  const a: string[] = [
    `tight: ${e.tight ?? true}`,
    `indent: ${e.indent ?? 0}pt`,
    `body-indent: ${e.body_indent ?? 0.5}em`,
    `spacing: ${typstListSpacing((e.spacing as string) ?? 'auto')}`,
  ];
  if (e.numbering && e.numbering !== '1.') a.push(`numbering: ${typstStr(e.numbering as string)}`);
  if (e.reversed) a.push('reversed: true');
  if (e.full) a.push('full: true');
  return `#set enum(${a.join(', ')})`;
}

function tableLine(e: DTO): string {
  const a: string[] = [`stroke: ${e.stroke ?? '0.5pt'}`];
  if (e.align && e.align !== 'auto') a.push(`align: ${e.align}`);
  if (e.inset && e.inset !== '5pt') a.push(`inset: ${e.inset}`);
  if (e.fill && e.fill !== 'none') a.push(`fill: ${e.fill}`);
  return `#set table(${a.join(', ')})`;
}

function figureLine(e: DTO): string {
  const w = (e.width as number) ? `${e.width}em` : 'auto';
  const h = (e.height as number) ? `${e.height}em` : 'auto';
  const ia: string[] = [`width: ${w}`, `height: ${h}`];
  if (e.fit && e.fit !== 'cover') ia.push(`fit: ${typstStr(e.fit as string)}`);
  const parts: string[] = [`#set image(${ia.join(', ')})`];
  const fa: string[] = [];
  if (e.placement && e.placement !== 'none') fa.push(`placement: ${e.placement}`);
  if (e.gap && (e.gap as number) !== 0.65) fa.push(`gap: ${e.gap}em`);
  if (e.outlined === false) fa.push('outlined: false');
  if (fa.length) parts.push(`#set figure(${fa.join(', ')})`);
  return parts.join('\n');
}

function footnoteLine(e: DTO): string {
  const parts: string[] = [`#set footnote(numbering: ${typstStr((e.marker_format as string) ?? '1')})`];
  const ea: string[] = [];
  if (e.clearance && (e.clearance as number) !== 1) ea.push(`clearance: ${e.clearance}em`);
  if (e.gap && (e.gap as number) !== 0.5) ea.push(`gap: ${e.gap}em`);
  if (e.indent && (e.indent as number) !== 1) ea.push(`indent: ${e.indent}em`);
  if (ea.length) parts.push(`#set footnote.entry(${ea.join(', ')})`);
  return parts.join('\n');
}

function quoteLine(e: DTO): string {
  const qa: string[] = [`block: ${e.block ?? true}`];
  if (e.quotes && e.quotes !== 'auto') qa.push(`quotes: ${e.quotes}`);
  return `#set quote(${qa.join(', ')})\n#show quote: set pad(x: ${e.indent ?? 1.5}em)`;
}

function rawLine(e: DTO): string {
  const a: string[] = [];
  if (e.tab_size && (e.tab_size as number) !== 2) a.push(`tab-size: ${e.tab_size}`);
  if (e.align && e.align !== 'start') a.push(`align: ${e.align}`);
  if (e.theme === 'none') a.push('theme: none');
  return a.length ? `#set raw(${a.join(', ')})` : '';
}

function termsLine(e: DTO): string {
  const a: string[] = [`tight: ${e.tight ?? true}`];
  if (e.indent && (e.indent as number) !== 0) a.push(`indent: ${e.indent}pt`);
  if (e.hanging_indent && (e.hanging_indent as number) !== 2) a.push(`hanging-indent: ${e.hanging_indent}em`);
  if (e.spacing && e.spacing !== 'auto') a.push(`spacing: ${typstListSpacing(e.spacing as string)}`);
  return `#set terms(${a.join(', ')})`;
}

function outlineLine(e: DTO): string {
  const a: string[] = [];
  if (e.depth != null) a.push(`depth: ${e.depth}`);
  if (e.indent && e.indent !== 'auto') a.push(`indent: ${e.indent}`);
  return a.length ? `#set outline(${a.join(', ')})` : '';
}

const BUILDERS: Record<ElementType, (e: DTO) => string> = {
  page: pageLine,
  document: documentLine,
  par: parLine,
  heading: headingLine,
  heading_1: (e) => headingLevelLine(e, 1),
  heading_2: (e) => headingLevelLine(e, 2),
  heading_3: (e) => headingLevelLine(e, 3),
  heading_4: (e) => headingLevelLine(e, 4),
  heading_5: (e) => headingLevelLine(e, 5),
  heading_6: (e) => headingLevelLine(e, 6),
  bullet_list: bulletListLine,
  numbered_list: numberedListLine,
  table: tableLine,
  figure: figureLine,
  footnote: footnoteLine,
  quote: quoteLine,
  raw: rawLine,
  equation: equationLine,
  terms: termsLine,
  outline: outlineLine,
};

function buildTypstPreamble(elements: Map<ElementType, DTO>): string {
  const lines: string[] = [];
  for (const type of ALL_ELEMENT_PATHS) {
    const e = elements.get(type);
    if (!e) continue;
    const fn = BUILDERS[type];
    if (!fn) continue;
    const part = fn(e);
    if (part) lines.push(...part.split('\n'));
  }
  return lines.length ? lines.join('\n') + '\n' : '';
}

export async function loadProfileStyles(profileId: number): Promise<string> {
  const elements = new Map<ElementType, DTO>();

  await Promise.all(
    ALL_ELEMENT_PATHS.map(async (type) => {
      try {
        const path = /^heading_\d$/.test(type)
          ? `heading/${type.replace('heading_', '')}`
          : type === 'equation'
            ? 'equation'
            : type;
        const res = await fetch(`${API_BASE}/profiles/${profileId}/${path}`);
        if (res.ok) {
          elements.set(type, await res.json());
        }
      } catch {
        // skip failed elements
      }
    }),
  );

  return buildTypstPreamble(elements);
}
