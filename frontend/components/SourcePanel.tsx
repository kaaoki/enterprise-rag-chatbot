type SourcePanelProps = {
  sources: string[];
  isLoading: boolean;
  error: string | null;
};

export default function SourcePanel({ sources, isLoading, error }: SourcePanelProps) {
  return (
    <aside className="w-full shrink-0 border-t border-line pt-6 md:w-64 md:border-l md:border-t-0 md:pl-6 md:pt-0">
      <h2 className="font-serif text-sm tracking-wide text-ink">検索対象の資料</h2>
      <div className="mt-3 space-y-2">
        {isLoading && <p className="text-sm text-ink/60">読み込み中…</p>}
        {error && <p className="text-sm text-red-700/80">{error}</p>}
        {!isLoading && !error && sources.length === 0 && (
          <p className="text-sm leading-relaxed text-ink/60">
            まだ資料が登録されていません。
            <br />
            <code className="text-xs">POST /api/documents/ingest</code> を実行してください。
          </p>
        )}
        {sources.map((s) => (
          <div key={s} className="rounded-sm border border-line bg-white px-3 py-2 text-sm text-ink">
            {s}
          </div>
        ))}
      </div>
    </aside>
  );
}
