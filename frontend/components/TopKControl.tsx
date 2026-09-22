type TopKControlProps = {
  value: number;
  onChange: (value: number) => void;
};

export default function TopKControl({ value, onChange }: TopKControlProps) {
  return (
    <label className="flex items-center gap-3 text-xs text-ink/70">
      <span>検索精度（TOP_K）</span>
      <input
        type="range"
        min={1}
        max={10}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-1 w-28 cursor-pointer accent-pine"
      />
      <span className="w-4 text-right font-medium text-ink">{value}</span>
    </label>
  );
}
