import type { ReactNode } from "react";

interface ReadonlyFieldProps {
  label: string;
  value?: string | number | null;
  icon?: ReactNode;
  placeholder?: string;
  wide?: boolean;
}

export function ReadonlyField({
  label,
  value,
  icon,
  placeholder = "Not captured yet",
  wide = false,
}: ReadonlyFieldProps) {
  const displayValue = value === null || value === undefined || value === ""
    ? placeholder
    : String(value);

  return (
    <div className={`readonly-field${wide ? " readonly-field--wide" : ""}`}>
      <span className="field-label">{label}</span>
      <div className={`field-value${displayValue === placeholder ? " is-empty" : ""}`}>
        {icon ? <span className="field-icon">{icon}</span> : null}
        <span>{displayValue}</span>
      </div>
    </div>
  );
}
