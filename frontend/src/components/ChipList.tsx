interface ChipListProps {
  label: string;
  values: string[];
  emptyText: string;
}

export function ChipList({ label, values, emptyText }: ChipListProps) {
  return (
    <div className="chip-field">
      <span className="field-label">{label}</span>
      <div className="chip-list">
        {values.length > 0 ? (
          values.map((value, index) => (
            <span className="data-chip" key={`${value}-${index}`}>
              {value}
            </span>
          ))
        ) : (
          <span className="empty-chip-value">{emptyText}</span>
        )}
      </div>
    </div>
  );
}
