/**
 * Minimal, XSS-safe markdown → React renderer for advisories and chat replies.
 * It never uses innerHTML: text becomes React text nodes, so "<script>" is shown, not executed.
 * Supports: ## / ### headings, - * • bullets, 1. lists, **bold**, *italic* / _italic_, `code`, paragraphs.
 */
import { Fragment, type ReactNode } from "react";

function inline(text: string, keyBase: string): ReactNode[] {
  const out: ReactNode[] = [];
  const re = /(\*\*[^*]+\*\*|__[^_]+__|\*[^*\s][^*]*\*|_[^_\s][^_]*_|`[^`]+`)/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let i = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const tok = m[0];
    const k = `${keyBase}-${i++}`;
    if (tok.startsWith("**") || tok.startsWith("__")) out.push(<strong key={k}>{tok.slice(2, -2)}</strong>);
    else if (tok.startsWith("`")) out.push(<code key={k}>{tok.slice(1, -1)}</code>);
    else out.push(<em key={k}>{tok.slice(1, -1)}</em>);
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

type Block = { kind: "h" | "p" | "ul" | "ol"; level?: number; lines: string[] };

export function parseBlocks(src: string): Block[] {
  const blocks: Block[] = [];
  let cur: Block | null = null;
  const flush = () => {
    if (cur) blocks.push(cur);
    cur = null;
  };
  for (const raw of (src || "").replace(/\r/g, "").split("\n")) {
    const line = raw.trimEnd();
    const t = line.trim();
    if (!t) {
      flush();
      continue;
    }
    const h = /^(#{1,6})\s+(.*)$/.exec(t);
    if (h) {
      flush();
      blocks.push({ kind: "h", level: h[1].length, lines: [h[2].replace(/\s*#+$/, "")] });
      continue;
    }
    const ul = /^[-*•]\s+(.*)$/.exec(t);
    const ol = /^\d+[.)]\s+(.*)$/.exec(t);
    if (ul || ol) {
      const kind = ul ? "ul" : "ol";
      if (!cur || cur.kind !== kind) {
        flush();
        cur = { kind, lines: [] };
      }
      cur.lines.push((ul ?? ol)![1]);
      continue;
    }
    if (!cur || cur.kind !== "p") {
      flush();
      cur = { kind: "p", lines: [] };
    }
    cur.lines.push(t);
  }
  flush();
  return blocks;
}

export function Markdown({ text, className }: { text: string; className?: string }) {
  const blocks = parseBlocks(text);
  return (
    <div className={className ?? "advice"}>
      {blocks.map((b, i) => {
        const k = `b${i}`;
        if (b.kind === "h") return <h4 key={k}>{inline(b.lines[0], k)}</h4>;
        if (b.kind === "ul") return <ul key={k}>{b.lines.map((l, j) => <li key={j}>{inline(l, `${k}-${j}`)}</li>)}</ul>;
        if (b.kind === "ol") return <ol key={k}>{b.lines.map((l, j) => <li key={j}>{inline(l, `${k}-${j}`)}</li>)}</ol>;
        return (
          <p key={k}>
            {b.lines.map((l, j) => (
              <Fragment key={j}>
                {j > 0 && <br />}
                {inline(l, `${k}-${j}`)}
              </Fragment>
            ))}
          </p>
        );
      })}
    </div>
  );
}
