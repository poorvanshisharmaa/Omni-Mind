import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Mic, Square, Volume2 } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/translator")({
  head: () => ({
    meta: [
      { title: "Universal Translator — OmniMind" },
      {
        name: "description",
        content:
          "Live two-way speech translation with per-side language selection, waveform capture and inline translated text and audio.",
      },
      { property: "og:title", content: "Universal Translator — OmniMind" },
      {
        property: "og:description",
        content: "Two-way live speech translation for cross-border enterprise conversations.",
      },
    ],
  }),
  component: UniversalTranslator,
});

const LANGS = ["English", "Hindi", "French", "Japanese", "Arabic", "Spanish", "German"];

const TURNS = [
  {
    side: "left" as const,
    original: "Can you confirm the settlement window for the cross-border tranche?",
    translated: "Pouvez-vous confirmer la fenêtre de règlement pour la tranche transfrontalière ?",
  },
  {
    side: "right" as const,
    original: "Oui, le règlement est fixé à T+2 à partir du mois prochain.",
    translated: "Yes, settlement is set to T+2 starting next month.",
  },
  {
    side: "left" as const,
    original: "Understood — I'll update the operations runbook accordingly.",
    translated: "Compris — je mettrai à jour le manuel des opérations en conséquence.",
  },
];

function Waveform({ active }: { active: boolean }) {
  return (
    <div className="flex h-10 items-center justify-center gap-[3px]">
      {Array.from({ length: 28 }).map((_, i) => (
        <span
          key={i}
          className={cn(
            "w-[3px] rounded-full bg-accent",
            active ? "wave-bar h-8" : "h-1.5 opacity-40",
          )}
          style={active ? { animationDelay: `${(i % 9) * 70}ms` } : undefined}
        />
      ))}
    </div>
  );
}

function Side({
  label,
  lang,
  setLang,
  recording,
  onToggle,
  turns,
}: {
  label: string;
  lang: string;
  setLang: (v: string) => void;
  recording: boolean;
  onToggle: () => void;
  turns: typeof TURNS;
}) {
  return (
    <section className="panel flex min-h-[520px] flex-col">
      <div className="flex items-center gap-3 border-b border-border px-5 py-3.5">
        <span className="text-sm font-medium">{label}</span>
        <Select value={lang} onValueChange={setLang}>
          <SelectTrigger className="ml-auto w-36">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {LANGS.map((l) => (
              <SelectItem key={l} value={l}>
                {l}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex flex-1 flex-col gap-4 px-5 py-5">
        {turns.map((t, i) => (
          <div key={i} className="rounded-lg border border-border px-3.5 py-3">
            <p className="text-sm leading-relaxed">{t.original}</p>
            <p className="mt-2 border-t border-dashed border-border pt-2 text-sm leading-relaxed text-muted-foreground">
              {t.translated}
            </p>
            <button
              type="button"
              className="mt-2.5 inline-flex items-center gap-1.5 text-xs text-accent"
            >
              <Volume2 className="h-3.5 w-3.5" />
              Play translated audio
            </button>
          </div>
        ))}
      </div>

      <div className="border-t border-border px-5 py-5">
        <Waveform active={recording} />
        <button
          type="button"
          onClick={onToggle}
          className={cn(
            "mt-4 flex w-full items-center justify-center gap-2 rounded-md px-4 py-2.5 text-sm font-medium transition-colors",
            recording
              ? "bg-destructive text-destructive-foreground"
              : "bg-primary text-primary-foreground hover:bg-primary/90",
          )}
        >
          {recording ? <Square className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          {recording ? "Stop recording" : `Speak ${lang}`}
        </button>
      </div>
    </section>
  );
}

function UniversalTranslator() {
  const [leftLang, setLeftLang] = useState("English");
  const [rightLang, setRightLang] = useState("French");
  const [recording, setRecording] = useState<"left" | "right" | null>(null);

  return (
    <AppShell
      title="Universal Translator"
      subtitle="A two-way live conversation surface. Each side selects its own language; speech is transcribed, translated and spoken back inline."
    >
      <div className="grid gap-6 lg:grid-cols-2">
        <Side
          label="Participant A"
          lang={leftLang}
          setLang={setLeftLang}
          recording={recording === "left"}
          onToggle={() => setRecording(recording === "left" ? null : "left")}
          turns={TURNS.filter((t) => t.side === "left")}
        />
        <Side
          label="Participant B"
          lang={rightLang}
          setLang={setRightLang}
          recording={recording === "right"}
          onToggle={() => setRecording(recording === "right" ? null : "right")}
          turns={TURNS.filter((t) => t.side === "right")}
        />
      </div>
    </AppShell>
  );
}
