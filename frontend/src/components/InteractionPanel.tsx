import {
  Building2,
  CalendarDays,
  Check,
  ClipboardList,
  FileText,
  HeartPulse,
  PackageOpen,
  Stethoscope,
  UserRound,
} from "lucide-react";
import { useAppSelector } from "../app/hooks";
import type { Sentiment } from "../types/crm";
import { ChipList } from "./ChipList";
import { ReadonlyField } from "./ReadonlyField";
import { SectionCard } from "./SectionCard";

const sentiments: Sentiment[] = ["Positive", "Neutral", "Negative"];

function formatDate(value: string | null): string {
  if (!value) {
    return "";
  }

  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

export function InteractionPanel() {
  const form = useAppSelector((state) => state.crm.currentForm);

  return (
    <main className="interaction-panel" aria-label="Interaction details">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Interaction details</p>
          <h1>Log HCP interaction</h1>
          <p className="panel-description">
            Describe the interaction in the assistant. The AI will populate and
            correct this form for you.
          </p>
        </div>
        <div className="record-badge">
          <span>Record</span>
          <strong>{form.interaction_id ? `#${form.interaction_id}` : "Draft"}</strong>
        </div>
      </div>

      <div className="ai-only-notice">
        <HeartPulse size={18} />
        <div>
          <strong>AI-controlled form</strong>
          <span>Fields are read-only and cannot be changed manually.</span>
        </div>
      </div>

      <div className="sections-stack">
        <SectionCard
          title="Healthcare professional"
          subtitle="The HCP selected or detected from the conversation"
          icon={<UserRound size={18} />}
        >
          <div className="form-grid">
            <ReadonlyField
              label="HCP name"
              value={form.hcp_name}
              icon={<UserRound size={16} />}
            />
            <ReadonlyField
              label="Specialty"
              value={form.specialty}
              icon={<Stethoscope size={16} />}
            />
            <ReadonlyField
              label="Organization"
              value={form.organization}
              icon={<Building2 size={16} />}
              wide
            />
          </div>
        </SectionCard>

        <SectionCard
          title="Interaction information"
          subtitle="Date, channel, discussion and overall outcome"
          icon={<ClipboardList size={18} />}
        >
          <div className="form-grid">
            <ReadonlyField
              label="Interaction date"
              value={formatDate(form.interaction_date)}
              icon={<CalendarDays size={16} />}
            />
            <ReadonlyField
              label="Interaction type"
              value={form.interaction_type}
              icon={<ClipboardList size={16} />}
            />
          </div>

          <div className="sentiment-field">
            <span className="field-label">HCP sentiment</span>
            <div className="sentiment-options" aria-label="HCP sentiment">
              {sentiments.map((sentiment) => {
                const selected = form.sentiment === sentiment;
                return (
                  <div
                    className={`sentiment-option sentiment-${sentiment.toLowerCase()}${
                      selected ? " is-selected" : ""
                    }`}
                    key={sentiment}
                  >
                    <span className="sentiment-radio">
                      {selected ? <Check size={12} strokeWidth={3} /> : null}
                    </span>
                    {sentiment}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="chip-grid">
            <ChipList
              label="Products discussed"
              values={form.products_discussed}
              emptyText="No products captured"
            />
            <ChipList
              label="Topics discussed"
              values={form.topics_discussed}
              emptyText="No topics captured"
            />
          </div>

          <div className="notes-field">
            <span className="field-label">Interaction notes</span>
            <div className={`notes-box${form.notes ? "" : " is-empty"}`}>
              <FileText size={17} />
              <p>{form.notes || "The AI-generated summary will appear here."}</p>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Materials and follow-up"
          subtitle="Resources shared and the next planned action"
          icon={<PackageOpen size={18} />}
        >
          <ChipList
            label="Materials shared"
            values={form.materials_shared}
            emptyText="No materials recorded"
          />

          <div className="follow-up-row">
            <div className="follow-up-status">
              <span className="field-label">Follow-up required</span>
              <div className={`readonly-toggle${form.follow_up_required ? " is-on" : ""}`}>
                <span className="toggle-track">
                  <span className="toggle-thumb" />
                </span>
                <strong>{form.follow_up_required ? "Yes" : "No"}</strong>
              </div>
            </div>
            <ReadonlyField
              label="Follow-up date"
              value={formatDate(form.follow_up_date)}
              icon={<CalendarDays size={16} />}
            />
          </div>
        </SectionCard>
      </div>
    </main>
  );
}
