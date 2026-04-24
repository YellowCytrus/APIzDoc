const SPACING_COMMANDS = ['\\!', '\\,', '\\:', '\\;', '\\quad', '\\qquad'];

function stripSimpleCommands(input: string, commands: string[]) {
  let out = input;
  for (const cmd of commands) {
    out = out.split(cmd).join('');
  }
  return out;
}

function convertPairedCommand(input: string, command: string, mapper: (a: string, b: string) => string) {
  const pattern = new RegExp(String.raw`\\${command}\{([^{}]*)\}\{([^{}]*)\}`, 'g');
  let out = input;
  let guard = 0;
  while (guard < 20 && pattern.test(out)) {
    pattern.lastIndex = 0;
    out = out.replace(pattern, (_m, a: string, b: string) => mapper(a, b));
    guard += 1;
  }
  return out;
}

function unwrapOneArgCommand(input: string, command: string) {
  const pattern = new RegExp(String.raw`\\${command}\{([^{}]*)\}`, 'g');
  let out = input;
  let guard = 0;
  while (guard < 20 && pattern.test(out)) {
    pattern.lastIndex = 0;
    out = out.replace(pattern, '$1');
    guard += 1;
  }
  return out;
}

export function sanitizeLatex(input: string): string {
  let out = input;

  out = out.replace(/\\(?:dfrac|tfrac|cfrac)\b/g, '\\frac');
  out = out.replace(/\\middle\s*\|/g, '|');
  out = out.replace(/\\bigm\s*\|/g, '|');

  out = stripSimpleCommands(out, ['\\left', '\\right', '\\big', '\\Big', '\\bigl', '\\bigr', '\\bigm']);
  out = stripSimpleCommands(out, SPACING_COMMANDS);

  out = unwrapOneArgCommand(out, 'operatorname');
  out = unwrapOneArgCommand(out, 'text');

  out = convertPairedCommand(out, 'overset', (a, b) => `${b}^{${a}}`);
  out = convertPairedCommand(out, 'underset', (a, b) => `${b}_{${a}}`);
  out = convertPairedCommand(out, 'binom', (a, b) => `(${a}, ${b})`);

  out = out.replace(/\s+/g, ' ').trim();
  return out;
}
