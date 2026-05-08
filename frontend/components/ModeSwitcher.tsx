type ModeSwitcherProps = {
  modes: string[];
  selectedMode: string;
};

export default function ModeSwitcher({ modes, selectedMode }: ModeSwitcherProps) {
  return (
    <section className="rounded-xl border p-4 shadow-sm">
      <h2 className="text-lg font-semibold">Learning Modes</h2>
      <div className="flex flex-wrap gap-2">
        {modes.map((mode) => (
          <span
            key={mode}
            className={`rounded-full px-3 py-1 text-sm ${
              mode === selectedMode ? "bg-black text-white" : "bg-gray-100 text-gray-700"
            }`}
          >
            {mode}
          </span>
        ))}
      </div>
    </section>
  );
}

