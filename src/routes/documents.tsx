import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { FileUp, Pause, Play, SkipBack, SkipForward } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/documents")({
  head: () => ({
    meta: [
      { title: "Document Intelligence — OmniMind" },
      {
        name: "description",
        content:
          "Translate PDF and DOCX documents side by side, with narrated audio playback and chapter markers for enterprise review workflows.",
      },
      { property: "og:title", content: "Document Intelligence — OmniMind" },
      {
        property: "og:description",
        content: "Side-by-side document translation with narration and chapter markers.",
      },
    ],
  }),
  component: DocumentIntelligence,
});

const LANGS = ["English", "Hindi", "French", "Japanese", "Arabic", "Spanish", "German"];

const PARAGRAPHS = [
  {
    source:
      "This addendum sets out the revised customer due diligence obligations applicable to tier-2 branches from the next reporting quarter.",
    target:
      "यह परिशिष्ट अगली रिपोर्टिंग तिमाही से टियर-2 शाखाओं पर लागू संशोधित ग्राहक सम्यक तत्परता दायित्वों को निर्धारित करता है।",
  },
  {
    source:
      "Re-verification of customer identity records must be completed within forty-five calendar days of the trigger event.",
    target:
      "ग्राहक पहचान अभिलेखों का पुनः सत्यापन ट्रिगर घटना के पैंतालीस कैलेंडर दिनों के भीतर पूरा किया जाना चाहिए।",
  },
  {
    source:
      "An automated exception report shall be generated weekly and retained for a period of seven years.",
    target:
      "एक स्वचालित अपवाद रिपोर्ट साप्ताहिक रूप से तैयार की जाएगी और सात वर्षों की अवधि तक संरक्षित रखी जाएगी।",
  },
];

const CHAPTERS = [
  { label: "Scope & applicability", at: "00:00", pct: 0 },
  { label: "Due diligence timeline", at: "01:24", pct: 28 },
  { label: "Exception reporting", at: "03:10", pct: 62 },
  { label: "Retention", at: "04:35", pct: 88 },
];

function DocumentIntelligence() {
  const [uploaded, setUploaded] = useState(true);
  const [source, setSource] = useState("English");
  const [target, setTarget] = useState("Hindi");
  const [playing, setPlaying] = useState(false);
  const [chapter, setChapter] = useState(0);

  return (
    <AppShell
      title="Document Intelligence"
      subtitle="Upload a policy document, choose a language pair, and review the translation side by side with narrated audio."
    >
      <div className="flex flex-col gap-6">
        <div className="panel flex flex-wrap items-end gap-4 px-5 py-4">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-md bg-secondary text-primary">
              <FileUp className="h-4 w-4" />
            </span>
            <div>
              <p className="text-sm font-medium">
                {uploaded ? "kyc-addendum-2026.pdf" : "No document selected"}
              </p>
              <p className="text-xs text-muted-foreground">PDF or DOCX · max 100 MB</p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={() => setUploaded(true)}>
            Replace document
          </Button>

          <div className="ml-auto flex flex-wrap items-end gap-3">
            <label className="flex flex-col gap-1.5">
              <span className="text-[11px] uppercase tracking-widest text-muted-foreground">
                Source
              </span>
              <Select value={source} onValueChange={setSource}>
                <SelectTrigger className="w-40">
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
            </label>
            <label className="flex flex-col gap-1.5">
              <span className="text-[11px] uppercase tracking-widest text-muted-foreground">
                Target
              </span>
              <Select value={target} onValueChange={setTarget}>
                <SelectTrigger className="w-40">
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
            </label>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {[
            { title: `Original · ${source}`, key: "source" as const },
            { title: `Translated · ${target}`, key: "target" as const },
          ].map((col) => (
            <section key={col.key} className="panel">
              <div className="border-b border-border px-5 py-3.5">
                <h2 className="text-sm font-medium">{col.title}</h2>
              </div>
              <div className="flex flex-col gap-4 px-5 py-5">
                {PARAGRAPHS.map((p, i) => (
                  <p
                    key={i}
                    className={cn(
                      "rounded-md px-3 py-2.5 text-sm leading-relaxed transition-colors",
                      chapter === i ? "bg-mint/25" : "bg-transparent",
                    )}
                  >
                    {p[col.key]}
                  </p>
                ))}
              </div>
            </section>
          ))}
        </div>

        <section className="panel px-5 py-4">
          <div className="flex items-center gap-3">
            <Button
              size="icon"
              variant="outline"
              onClick={() => setChapter((c) => Math.max(0, c - 1))}
            >
              <SkipBack className="h-4 w-4" />
            </Button>
            <Button size="icon" onClick={() => setPlaying((p) => !p)}>
              {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </Button>
            <Button
              size="icon"
              variant="outline"
              onClick={() => setChapter((c) => Math.min(CHAPTERS.length - 1, c + 1))}
            >
              <SkipForward className="h-4 w-4" />
            </Button>
            <div className="ml-2 min-w-0 flex-1">
              <div className="relative h-1.5 rounded-full bg-secondary">
                <div
                  className="absolute inset-y-0 left-0 rounded-full bg-accent"
                  style={{ width: `${CHAPTERS[chapter].pct + 6}%` }}
                />
                {CHAPTERS.map((c, i) => (
                  <button
                    key={c.label}
                    type="button"
                    onClick={() => setChapter(i)}
                    aria-label={`Jump to ${c.label}`}
                    className={cn(
                      "absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-card",
                      i === chapter ? "bg-primary" : "bg-muted-foreground/60",
                    )}
                    style={{ left: `${c.pct + 3}%` }}
                  />
                ))}
              </div>
              <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1">
                {CHAPTERS.map((c, i) => (
                  <button
                    key={c.label}
                    type="button"
                    onClick={() => setChapter(i)}
                    className={cn(
                      "text-xs transition-colors",
                      i === chapter ? "text-foreground" : "text-muted-foreground",
                    )}
                  >
                    <span className="font-mono">{c.at}</span> · {c.label}
                  </button>
                ))}
              </div>
            </div>
            <span className="font-mono text-xs text-muted-foreground">05:12</span>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
