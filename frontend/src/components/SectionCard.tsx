import type { ReactNode } from "react";

interface SectionCardProps {
  title: string;
  subtitle?: string;
  icon: ReactNode;
  children: ReactNode;
}

export function SectionCard({
  title,
  subtitle,
  icon,
  children,
}: SectionCardProps) {
  return (
    <section className="section-card">
      <div className="section-heading">
        <span className="section-icon">{icon}</span>
        <div>
          <h2>{title}</h2>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
      </div>
      <div className="section-content">{children}</div>
    </section>
  );
}
