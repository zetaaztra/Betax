export function ConcentricBackground() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative w-[200vmax] h-[200vmax] animate-rotate-slow">
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className="absolute inset-0 rounded-full border border-spike/5 dark:border-spike/5"
              style={{
                width: `${20 + i * 12}%`,
                height: `${20 + i * 12}%`,
                left: `${40 - i * 6}%`,
                top: `${40 - i * 6}%`,
              }}
            />
          ))}
          {[...Array(8)].map((_, i) => (
            <div
              key={`alt-${i}`}
              className="absolute inset-0 rounded-full border border-bullish/5 dark:border-bullish/5"
              style={{
                width: `${26 + i * 12}%`,
                height: `${26 + i * 12}%`,
                left: `${37 - i * 6}%`,
                top: `${37 - i * 6}%`,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
