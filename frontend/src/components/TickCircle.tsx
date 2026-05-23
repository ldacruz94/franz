import "./TickCircle.css";

const SIZE = 600;
const CENTER = SIZE / 2;
const TICK_RADIUS = 188;
const TICK_COUNT = 60;

const ticks = Array.from({ length: TICK_COUNT }, (_, i) => ({
  angle: i * (360 / TICK_COUNT),
  isMajor: i % 5 === 0,
}));

const innerDots = Array.from({ length: 72 }, (_, i) => {
  const a = (i * 2 * Math.PI) / 72;
  return { x: Math.cos(a) * 126, y: Math.sin(a) * 126, major: i % 6 === 0 };
});

const outerDots = Array.from({ length: 36 }, (_, i) => {
  const a = (i * 2 * Math.PI) / 36;
  return { x: Math.cos(a) * 248, y: Math.sin(a) * 248, major: i % 4 === 0 };
});

interface Props {
  isSpeaking?: boolean;
  isThinking?: boolean;
}

export default function TickCircle({ isSpeaking = false, isThinking = false }: Props) {
  return (
    <div className={`tick-circle-wrapper${isThinking ? " tick-circle-wrapper--thinking" : ""}`}>
      {isSpeaking && (
        <>
          <div className="speak-ring speak-ring--1" />
          <div className="speak-ring speak-ring--2" />
          <div className="speak-ring speak-ring--3" />
        </>
      )}

      <svg
        width={SIZE}
        height={SIZE}
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        className="jarvis-svg"
      >
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="glow-sm" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%"   style={{ stopColor: "var(--franz-primary)", stopOpacity: 0.18 }} />
            <stop offset="65%"  style={{ stopColor: "var(--franz-primary)", stopOpacity: 0.05 }} />
            <stop offset="100%" style={{ stopColor: "var(--franz-primary)", stopOpacity: 0 }} />
          </radialGradient>
        </defs>

        <g transform={`translate(${CENTER}, ${CENTER})`}>

          {/* ── Center glow ── */}
          <circle r={110} fill="url(#centerGlow)" />
          <circle r={104} fill="none" style={{ stroke: "var(--franz-primary)" }} strokeWidth={0.8} opacity={0.45} filter="url(#glow-sm)" />

          {/* ── Speaking glow ── */}
          {isSpeaking && (
            <>
              <circle r={110} style={{ fill: "var(--franz-primary)" }} className="center-speaking-fill" filter="url(#glow)" />
              <circle r={104} fill="none" style={{ stroke: "var(--franz-bright)" }} strokeWidth={3} className="center-speaking-ring" filter="url(#glow)" />
            </>
          )}

          {/* ── Inner dot ring ── */}
          {innerDots.map(({ x, y, major }, i) => (
            <circle
              key={i} cx={x} cy={y}
              r={major ? 2.5 : 1.5}
              style={{ fill: major ? "var(--franz-bright)" : "var(--franz-dim)" }}
              opacity={major ? 0.9 : 0.55}
            />
          ))}

          {/* ── Inner segmented arc ring ── */}
          <circle
            r={152} fill="none"
            style={{ stroke: "var(--franz-primary)" }} strokeWidth={1.5}
            strokeDasharray="67 29"
            opacity={0.7}
            filter="url(#glow-sm)"
          />

          {/* ── Rotating tick ring ── */}
          <g className={`ticks-group${isThinking ? " ticks-group--thinking" : ""}`}>
            {ticks.map(({ angle, isMajor }) => {
              const w = isMajor ? 6 : 2;
              const h = isMajor ? 16 : 11;
              return (
                <rect
                  key={angle}
                  x={-w / 2} y={-TICK_RADIUS}
                  width={w} height={h} rx={1}
                  style={{ fill: isMajor ? "var(--franz-bright)" : "var(--franz-dim)" }}
                  transform={`rotate(${angle})`}
                  filter={isMajor ? "url(#glow-sm)" : undefined}
                />
              );
            })}
          </g>

          {/* ── Outer segmented arc ring (counter-rotates) ── */}
          <g className="outer-arcs-group">
            <circle
              r={220} fill="none"
              style={{ stroke: "var(--franz-primary)" }} strokeWidth={2}
              strokeDasharray="130 43"
              opacity={0.75}
              filter="url(#glow-sm)"
            />
          </g>

          {/* ── Outer dot ring ── */}
          {outerDots.map(({ x, y, major }, i) => (
            <circle
              key={i} cx={x} cy={y}
              r={major ? 3 : 1.5}
              style={{ fill: major ? "var(--franz-primary)" : "var(--franz-deep-dim)" }}
              opacity={major ? 0.85 : 0.45}
              filter={major ? "url(#glow-sm)" : undefined}
            />
          ))}

          {/* ── Hairline outer ring ── */}
          <circle r={268} fill="none" style={{ stroke: "var(--franz-primary)" }} strokeWidth={0.5} opacity={0.25} />

          {/* ── Center label ── */}
          <text
            y={9}
            textAnchor="middle"
            style={{ fill: "var(--franz-bright)", userSelect: "none" }}
            fontSize={24}
            fontFamily="sans-serif"
            letterSpacing={7}
            filter="url(#glow)"
          >
            FRANZ
          </text>

        </g>
      </svg>
    </div>
  );
}
