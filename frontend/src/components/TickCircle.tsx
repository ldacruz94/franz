import "./TickCircle.css";

const SIZE = 520;
const CENTER = SIZE / 2;
const RADIUS = CENTER - 20;
const TICK_COUNT = 60;

interface Tick {
  angle: number;
  isMajor: boolean;
}

const ticks: Tick[] = Array.from({ length: TICK_COUNT }, (_, i) => ({
  angle: i * (360 / TICK_COUNT),
  isMajor: i % 5 === 0,
}));

interface Props {
  isSpeaking?: boolean;
}

export default function TickCircle({ isSpeaking = false }: Props) {
  return (
    <div className="tick-circle-wrapper">
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
        className="tick-circle-svg tick-ring"
      >
        <g transform={`translate(${CENTER}, ${CENTER})`}>
          {ticks.map(({ angle, isMajor }) => {
            const w = isMajor ? 8 : 2;
            const h = 18;
            return (
              <rect
                key={angle}
                x={-w / 2}
                y={-RADIUS}
                width={w}
                height={h}
                rx={1}
                ry={1}
                fill={isMajor ? "#b5e5ff" : "#3fa8ff"}
                transform={`rotate(${angle})`}
              />
            );
          })}
        </g>
      </svg>
      <span className="tick-label">F R A N Z</span>
    </div>
  );
}
