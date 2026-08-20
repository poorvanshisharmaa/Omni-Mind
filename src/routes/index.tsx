import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  AudioLines,
  CheckCircle2,
  Download,
  FileAudio,
  Pause,
  Play,
  ShieldAlert,
  UploadCloud,
} from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Meeting Intelligence — OmniMind" },
      {
        name: "description",
        content:
          "Diarized multilingual meeting transcripts with decisions, action items, risks and an auditable provenance log for enterprise and BFSI teams.",
      },
      { property: "og:title", content: "Meeting Intelligence — OmniMind" },
      {
        property: "og:description",
        content:
          "Upload meeting audio and get diarized transcripts, decisions, action items and an auditable provenance log.",
      },
    ],
  }),
  component: MeetingIntelligence,
});

const TRANSCRIPT = [
  {
    speaker: "Ananya Rao",
    role: "Risk Lead",
    tone: "speaker-1",
    time: "00:41",
    lang: "EN",
    text: "We need a final call on the KYC re-verification window before the audit cycle closes.",
  },
  {
    speaker: "Marc Dubois",
    role: "Compliance",
    tone: "speaker-2",
    time: "01:07",
    lang: "FR → EN",
    text: "Thirty days is too aggressive for tier-2 branches. I'd propose forty-five with a weekly exception report.",
  },
  {
    speaker: "Ravi Menon",
    role: "Operations",
    tone: "speaker-3",
    time: "02:15",
    lang: "HI → EN",
    text: "Operations can support forty-five days if the exception report is auto-generated, not manual.",
  },
  {
    speaker: "Ananya Rao",
    role: "Risk Lead",
    tone: "speaker-1",
    time: "03:02",
    lang: "EN",
    text: "Agreed. We lock forty-five days, automated weekly exceptions, effective next quarter.",
  },
];

const ACTIONS = [
  {
    task: "Automate weekly KYC exception report",
    owner: "Ravi Menon",
    deadline: "12 Sep 2026",
    status: "In progress",
  },
  {
    task: "Update tier-2 branch SOP to 45-day window",
    owner: "Marc Dubois",
    deadline: "28 Aug 2026",
    status: "Pending",
  },
  {
    task: "Circulate revised audit calendar",
    owner: "Ananya Rao",
    deadline: "22 Aug 2026",
    status: "Done",
  },
];

const RISKS = [
  {
    title: "Regulatory exposure on tier-2 branches",
    level: "High",
    note: "Extended window may conflict with local circular 14/2026 pending clarification.",
  },
  {
    title: "Manual fallback for exception reporting",
    level: "Medium",
    note: "Automation not yet scoped; manual process risks missed weekly cutoffs.",
  },
  {
    title: "Translation confidence on Hindi segments",
    level: "Low",
    note: "Two segments below 0.85 confidence — flagged for human review.",
  },
];

const PROVENANCE = [
  { time: "01:07", clip: "clip_0107.wav", decision: "45-day window proposed", by: "Marc Dubois" },
  { time: "02:15", clip: "clip_0215.wav", decision: "Operations conditional approval", by: "Ravi Menon" },
  { time: "03:02", clip: "clip_0302.wav", decision: "45-day window locked", by: "Ananya Rao" },
];

function MeetingIntelligence() {
  const [analyzed, setAnalyzed] = useState(false);
  const [playing, setPlaying] = useState<string | null>(null);

  return (
    <AppShell
      title="Meeting Intelligence"
      subtitle="Upload multilingual meeting audio to produce a diarized transcript, extracted decisions, owned action items and an auditable provenance trail."
    >
      {!analyzed ? (
        <div className="panel px-8 py-16">
          <div className="mx-auto flex max-w-md flex-col items-center text-center">
            <span className="flex h-12 w-12 items-center justify-center rounded-lg bg-secondary text-primary">
              <UploadCloud className="h-5 w-5" />
            </span>
            <h2 className="mt-5 text-base font-medium">Upload meeting audio</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              WAV, MP3 or M4A up to 2 GB. Speaker diarization and language detection run
              automatically.
            </p>
            <div className="mt-7 flex w-full flex-col gap-2 rounded-lg border border-dashed border-border bg-secondary/40 px-6 py-8">
              <FileAudio className="mx-auto h-5 w-5 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Drag a file here, or</p>
              <Button className="mx-auto mt-1" onClick={() => setAnalyzed(true)}>
                Select audio file
              </Button>
            </div>
            <p className="mt-5 text-xs text-muted-foreground">
              Processing stays within your data residency region.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)]">
          <section className="panel flex flex-col">
            <div className="flex items-center justify-between border-b border-border px-5 py-3.5">
              <div>
                <h2 className="text-sm font-medium">Diarized transcript</h2>
                <p className="text-xs text-muted-foreground">
                  Q3-risk-committee.wav · 41:22 · 3 speakers
                </p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setAnalyzed(false)}>
                New upload
              </Button>
            </div>
            <div className="flex flex-col gap-5 px-5 py-5">
              {TRANSCRIPT.map((t, i) => (
                <article key={i} className="flex gap-3">
                  <span
                    className="mt-1 h-8 w-8 shrink-0 rounded-full text-center text-[11px] font-medium leading-8 text-background"
                    style={{ backgroundColor: `var(--${t.tone})` }}
                  >
                    {t.speaker
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </span>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-baseline gap-2">
                      <span className="text-sm font-medium">{t.speaker}</span>
                      <span className="text-xs text-muted-foreground">{t.role}</span>
                      <span className="font-mono text-[11px] text-muted-foreground">{t.time}</span>
                      <Badge variant="outline" className="text-[10px]">
                        {t.lang}
                      </Badge>
                    </div>
                    <p
                      className="mt-1.5 rounded-lg rounded-tl-sm border-l-2 bg-secondary/60 px-3.5 py-2.5 text-sm leading-relaxed"
                      style={{ borderColor: `var(--${t.tone})` }}
                    >
                      {t.text}
                    </p>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="panel">
            <Tabs defaultValue="decisions">
              <div className="border-b border-border px-5 pt-3.5">
                <TabsList className="bg-transparent p-0">
                  <TabsTrigger value="decisions">Decisions</TabsTrigger>
                  <TabsTrigger value="actions">Action Items</TabsTrigger>
                  <TabsTrigger value="risks">Risks</TabsTrigger>
                  <TabsTrigger value="provenance">Provenance Log</TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="decisions" className="mt-0 flex flex-col gap-3 px-5 py-5">
                {[
                  "KYC re-verification window fixed at 45 days for tier-2 branches.",
                  "Weekly exception reporting becomes automated, effective next quarter.",
                  "Audit calendar reissued with revised cutoffs.",
                ].map((d) => (
                  <div key={d} className="flex gap-2.5 rounded-md bg-secondary/60 px-3.5 py-3">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
                    <p className="text-sm leading-relaxed">{d}</p>
                  </div>
                ))}
              </TabsContent>

              <TabsContent value="actions" className="mt-0 px-1 py-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Task</TableHead>
                      <TableHead>Owner</TableHead>
                      <TableHead>Deadline</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {ACTIONS.map((a) => (
                      <TableRow key={a.task}>
                        <TableCell className="max-w-[220px] text-sm">{a.task}</TableCell>
                        <TableCell className="text-sm text-muted-foreground">{a.owner}</TableCell>
                        <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
                          {a.deadline}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className={cn(
                              "text-[11px]",
                              a.status === "Done" && "border-mint text-mint-foreground bg-mint/40",
                              a.status === "In progress" && "border-accent text-accent",
                            )}
                          >
                            {a.status}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TabsContent>

              <TabsContent value="risks" className="mt-0 flex flex-col gap-3 px-5 py-5">
                {RISKS.map((r) => (
                  <div key={r.title} className="rounded-md border border-border px-3.5 py-3">
                    <div className="flex items-center gap-2">
                      <ShieldAlert className="h-4 w-4 text-warning" />
                      <p className="text-sm font-medium">{r.title}</p>
                      <span className="ml-auto text-[11px] uppercase tracking-wide text-muted-foreground">
                        {r.level}
                      </span>
                    </div>
                    <p className="mt-1.5 text-sm text-muted-foreground">{r.note}</p>
                  </div>
                ))}
              </TabsContent>

              <TabsContent value="provenance" className="mt-0 px-5 py-5">
                <div className="flex items-center justify-between pb-4">
                  <p className="text-xs text-muted-foreground">
                    Every decision linked to its source audio segment.
                  </p>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4" />
                    Export PDF
                  </Button>
                </div>
                <ol className="relative flex flex-col gap-4 border-l border-border pl-5">
                  {PROVENANCE.map((p) => (
                    <li key={p.time} className="relative">
                      <span className="absolute -left-[26px] top-2 h-2 w-2 rounded-full bg-accent" />
                      <div className="rounded-md bg-secondary/60 px-3.5 py-3">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[11px] text-muted-foreground">
                            {p.time}
                          </span>
                          <p className="text-sm font-medium">{p.decision}</p>
                        </div>
                        <p className="mt-1 text-xs text-muted-foreground">Attributed to {p.by}</p>
                        <button
                          type="button"
                          onClick={() => setPlaying(playing === p.clip ? null : p.clip)}
                          className="mt-2.5 inline-flex items-center gap-2 rounded-md border border-border bg-card px-2.5 py-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
                        >
                          {playing === p.clip ? (
                            <Pause className="h-3.5 w-3.5" />
                          ) : (
                            <Play className="h-3.5 w-3.5" />
                          )}
                          <AudioLines className="h-3.5 w-3.5 text-accent" />
                          <span className="font-mono">{p.clip}</span>
                        </button>
                      </div>
                    </li>
                  ))}
                </ol>
              </TabsContent>
            </Tabs>
          </section>
        </div>
      )}
    </AppShell>
  );
}
