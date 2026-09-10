"use client";

import { FormEvent, useEffect, useState } from "react";

import { askBIS, AssistantResponse, Citation, Language } from "../services/api";

type ThemeMode = "light" | "dark";

type SupportedLanguage = Exclude<Language, "unknown">;

type TaskItem = {
  id: string;
  label: string;
  kicker: string;
  helper: string;
  example: string;
};

const tasksByLanguage: Record<SupportedLanguage, TaskItem[]> = {
  en: [
    {
      id: "assistant",
      label: "Ask BIS Sahayak",
      kicker: "Evidence desk",
      helper: "Ask for guidance using official BIS documentation.",
      example: "Which BIS standard may apply to my product?",
    },
    {
      id: "standards",
      label: "Find a standard",
      kicker: "Product mapping",
      helper: "Match your product to the right Indian standard.",
      example: "I am manufacturing a 20-litre domestic water heater. Which standard applies?",
    },
    {
      id: "certification",
      label: "Certification guide",
      kicker: "Status and process",
      helper: "Understand certification steps and compliance requirements.",
      example: "What is the certification process for a new electrical appliance?",
    },
    {
      id: "laboratories",
      label: "Find a laboratory",
      kicker: "Verified facilities",
      helper: "Locate accredited testing and inspection facilities.",
      example: "Where can I find a verified BIS-recognized testing laboratory for my product?",
    },
    {
      id: "hallmarking",
      label: "Hallmarking",
      kicker: "Consumer guidance",
      helper: "Understand hallmarking and consumer protection rules.",
      example: "What are the hallmarking requirements for precious metal products?",
    },
  ],
  hi: [
    {
      id: "assistant",
      label: "BIS सहायक पूछें",
      kicker: "साक्ष्य डेस्क",
      helper: "आधिकारिक BIS दस्तावेज़ के आधार पर मार्गदर्शन लें।",
      example: "मेरे उत्पाद पर कौन सा BIS मानक लागू हो सकता है?",
    },
    {
      id: "standards",
      label: "मानक खोजें",
      kicker: "उत्पाद मैपिंग",
      helper: "अपने उत्पाद के लिए सही भारतीय मानक पहचानें।",
      example: "मैं एक 20-लीटर घरेलू वाटर हीटर का निर्माण कर रहा हूँ। कौन सा मानक लागू होता है?",
    },
    {
      id: "certification",
      label: "प्रमाणीकरण मार्गदर्शिका",
      kicker: "स्थिति और प्रक्रिया",
      helper: "प्रमाणीकरण के चरण और अनुपालन आवश्यकताओं को समझें।",
      example: "नए विद्युत उपकरण के लिए प्रमाणीकरण प्रक्रिया क्या है?",
    },
    {
      id: "laboratories",
      label: "प्रयोगशाला खोजें",
      kicker: "सत्यापित सुविधाएँ",
      helper: "मान्यता प्राप्त परीक्षण और निरीक्षण सुविधाओं का पता लगाएँ।",
      example: "मेरे उत्पाद के लिए सत्यापित BIS प्रयोगशाला कहाँ मिलेगी?",
    },
    {
      id: "hallmarking",
      label: "हॉलमार्किंग",
      kicker: "उपभोक्ता मार्गदर्शन",
      helper: "हॉलमार्किंग और उपभोक्ता संरक्षण नियम समझें।",
      example: "कीमती धातु उत्पादों के लिए हॉलमार्किंग आवश्यकताएँ क्या हैं?",
    },
  ],
  te: [
    {
      id: "assistant",
      label: "BIS సహాయకుడిని అడగండి",
      kicker: "సాక్ష్య డెస్క్",
      helper: "అధికార BIS డాక్యుమెంటేషన్ ఆధారంగా మార్గదర్శనం పొందండి.",
      example: "నా ఉత్పత్తికి ఏ BIS ప్రమాణం వర్తించవచ్చు?",
    },
    {
      id: "standards",
      label: "ప్రమాణాన్ని కనుగొనండి",
      kicker: "ఉత్పత్తి మ్యాపింగ్",
      helper: "మీ ఉత్పత్తికి సరిపోయే భారతీయ ప్రమాణాన్ని కనుగొనండి.",
      example: "నేను 20-లీటర్ల గృహ వాడకం ఉన్న ఎలక్ట్రిక్ వాటర్ హీటర్ను తయారు చేస్తున్నాను. ఏ ప్రమాణం వర్తిస్తుంది?",
    },
    {
      id: "certification",
      label: "సర్టిఫికేషన్ గైడ్",
      kicker: "స్థితి మరియు పద్ధతి",
      helper: "సర్టిఫికేషన్ దశలు మరియు కంప్లైయన్స్ అవసరాలను అర్థం చేసుకోండి.",
      example: "కొత్త ఎలక్ట్రికల్ పరికరం కోసం సర్టిఫికేషన్ ప్రక్రియ ఏమిటి?",
    },
    {
      id: "laboratories",
      label: "ప్రయోగశాల కనుగొనండి",
      kicker: "ధృవీకరించబడిన సౌకర్యాలు",
      helper: "మాన్యుస్క్రిప్ట్ పరీక్ష మరియు తనిఖీ సౌకర్యాలను కనుగొనండి.",
      example: "నా ఉత్పత్తి కోసం ధృవీకరించబడిన BIS పరీక్షా ప్రయోగశాలను ఎక్కడ కనుగొనవచ్చు?",
    },
    {
      id: "hallmarking",
      label: "హాల్మార్కింగ్",
      kicker: "వినియోగదారు మార్గదర్శనం",
      helper: "హాల్మార్కింగ్ మరియు వినియోగదారు రక్షణ నియమాలను అర్థం చేసుకోండి.",
      example: "విలువైన లోహ ఉత్పత్తుల కోసం హాల్మార్కింగ్ అవసరాలు ఏమిటి?",
    },
  ],
} as const;

type TaskId = (typeof tasksByLanguage.en)[number]["id"];

const navItems: Array<{ id: TaskId; label: string }> = [
  { id: "assistant", label: "Overview" },
  { id: "standards", label: "Standards" },
  { id: "certification", label: "Compliance" },
];

const suggestionsByLanguage: Record<Language, string[]> = {
  en: [
    "Which BIS standard may apply to my product?",
    "I need to understand certification for a new product.",
    "Where can I find a verified laboratory?",
  ],
  hi: [
    "मेरे उत्पाद पर कौन सा BIS मानक लागू हो सकता है?",
    "मैं नए उत्पाद के लिए प्रमाणीकरण समझना चाहता हूँ।",
    "मैं सत्यापित प्रयोगशाला कहाँ पा सकता हूँ?",
  ],
  te: [
    "నా ఉత్పత్తికి ఏ BIS ప్రమాణం వర్తించవచ్చు?",
    "కొత్త ఉత్పత్తి కోసం సర్టిఫికేషన్ గురించి నాకు అర్థం కావాలంటే?",
    "నాకు ధృవీకరించబడిన ప్రయోగశాల ఎక్కడ దొరుకుతుంది?",
  ],
  unknown: [
    "Which BIS standard may apply to my product?",
    "I need to understand certification for a new product.",
    "Where can I find a verified laboratory?",
  ],
};

const experienceHighlights = [
  {
    icon: "⚡",
    title: "Fast product mapping",
    text: "Match your product with the most relevant BIS standards in seconds.",
  },
  {
    icon: "✅",
    title: "Clear compliance steps",
    text: "Understand certification requirements and the next actions to take.",
  },
  {
    icon: "📚",
    title: "Evidence-backed guidance",
    text: "Answers stay tied to official BIS source material and references.",
  },
  {
    icon: "🌐",
    title: "Easy for every user",
    text: "Supports English, Hindi, and Telugu for wider accessibility.",
  },
] as const;

const quickUseCases = [
  "Domestic appliances",
  "Electrical safety",
  "Certification roadmap",
  "Laboratory search",
  "Consumer product checks",
] as const;

const copyByLanguage: Record<Language, {
  language: string;
  workAreas: string;
  askQuestion: string;
  askBIS: string;
  searching: string;
  evidenceFirst: string;
  evidenceNote: string;
  tryQuestion: string;
}> = {
  en: {
    language: "Language",
    workAreas: "Work areas",
    askQuestion: "What do you need to understand?",
    askBIS: "Ask BIS",
    searching: "Searching...",
    evidenceFirst: "Evidence-first mode",
    evidenceNote: "Claims stay tied to official BIS source material.",
    tryQuestion: "Try a question",
  },
  hi: {
    language: "भाषा",
    workAreas: "कार्य क्षेत्र",
    askQuestion: "आपको क्या समझना है?",
    askBIS: "BIS पूछें",
    searching: "खोजा जा रहा है...",
    evidenceFirst: "साक्ष्य-आधारित मोड",
    evidenceNote: "दावे आधिकारिक BIS स्रोत सामग्री से जुड़े रहते हैं।",
    tryQuestion: "प्रश्न आज़माएँ",
  },
  te: {
    language: "భాష",
    workAreas: "పని področాలు",
    askQuestion: "మీకు ఏమి అర్థం కావాలి?",
    askBIS: "BIS అడగండి",
    searching: "శోధిస్తోంది...",
    evidenceFirst: "సాక్ష్య-ఆధారిత మోడ్",
    evidenceNote: "వాదనలు అధికార BIS మూల వనరులతో ముడిపడి ఉంటాయి.",
    tryQuestion: "ప్రశ్నను ప్రయత్నించండి",
  },
  unknown: {
    language: "Language",
    workAreas: "Work areas",
    askQuestion: "What do you need to understand?",
    askBIS: "Ask BIS",
    searching: "Searching...",
    evidenceFirst: "Evidence-first mode",
    evidenceNote: "Claims stay tied to official BIS source material.",
    tryQuestion: "Try a question",
  },
};

export default function Home() {
  const [activeTask, setActiveTask] = useState<TaskId>("assistant");
  const [language, setLanguage] = useState<Language>("en");
  const [theme, setTheme] = useState<ThemeMode>("light");
  const [question, setQuestion] = useState<string>(tasksByLanguage.en[0].example);
  const [response, setResponse] = useState<AssistantResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const savedTheme = window.localStorage.getItem("bis-sahayak-theme");
    if (savedTheme === "light" || savedTheme === "dark") {
      setTheme(savedTheme);
      return;
    }

    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setTheme(prefersDark ? "dark" : "light");
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("bis-sahayak-theme", theme);
  }, [theme]);

  const resolvedLanguage: SupportedLanguage = language === "unknown" ? "en" : language;
  const tasks = tasksByLanguage[resolvedLanguage];
  const activeTaskConfig = tasks.find((task) => task.id === activeTask) ?? tasks[0];
  const copy = copyByLanguage[resolvedLanguage];
  const suggestions = suggestionsByLanguage[resolvedLanguage];

  async function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) return;

    setError(null);
    setLoading(true);
    try {
      setResponse(await askBIS(trimmedQuestion, language));
    } catch (requestError) {
      setResponse(null);
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The BIS service is temporarily unavailable."
      );
    } finally {
      setLoading(false);
    }
  }

  function selectTask(task: TaskId) {
    const selected = tasks.find((item) => item.id === task) ?? tasks[0];
    setActiveTask(task);
    setQuestion(selected.example);
    setError(null);
    setResponse(null);
  }

  function handleLanguageChange(nextLanguage: Language) {
    const safeLanguage: SupportedLanguage = nextLanguage === "unknown" ? "en" : nextLanguage;
    const nextTasks = tasksByLanguage[safeLanguage];
    const selected = nextTasks.find((item) => item.id === activeTask) ?? nextTasks[0];
    setLanguage(safeLanguage);
    setQuestion(selected.example);
    setError(null);
    setResponse(null);
  }

  return (
    <main className="shell" data-theme={theme}>
      <header className="topbar">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">
            <img src="/assets/bis-logo.png" alt="Bureau of Indian Standards logo" className="brand-image" />
          </span>
          <div>
            <p className="eyebrow">Bureau of Indian Standards</p>
            <p className="brand-name">BIS Sahayak</p>
          </div>
        </div>

        <nav className="main-nav" aria-label="Main navigation">
          {navItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`nav-pill ${activeTask === item.id ? "active" : ""}`}
              onClick={() => selectTask(item.id)}
              aria-pressed={activeTask === item.id}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="toolbar">
          <label className="language-picker">
            <span>{copy.language}</span>
            <select
              value={language}
              onChange={(event) => handleLanguageChange(event.target.value as Language)}
            >
              <option value="en">English</option>
              <option value="hi">हिन्दी</option>
              <option value="te">తెలుగు</option>
            </select>
          </label>

          <button
            type="button"
            className="theme-toggle"
            onClick={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
            aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          >
            {theme === "dark" ? "☀️ Light" : "🌙 Dark"}
          </button>
        </div>
      </header>

      <div className="app-grid">
        <aside className="sidebar" aria-label="BIS Sahayak work areas">
          <p className="sidebar-label">{copy.workAreas}</p>
          <nav className="task-nav">
            {tasks.map((task) => (
              <button
                key={task.id}
                type="button"
                className={`task-button ${activeTask === task.id ? "active" : ""}`}
                onClick={() => selectTask(task.id)}
              >
                <span>
                  <small>{task.kicker}</small>
                  {task.label}
                </span>
                <span aria-hidden="true">→</span>
              </button>
            ))}
          </nav>

          <div className="sidebar-note">
            <span className="status-dot" aria-hidden="true" />
            <div>
              <strong>{copy.evidenceFirst}</strong>
              <p>{copy.evidenceNote}</p>
            </div>
          </div>
        </aside>

        <section className="workspace" aria-labelledby="workspace-title">
          <div className="workspace-heading">
            <div>
              <p className="eyebrow">{activeTaskConfig.kicker}</p>
              <h1 id="workspace-title">{activeTaskConfig.label}</h1>
            </div>
            <span className="phase-tag">LIVE</span>
          </div>

          <p className="lede">{activeTaskConfig.helper}</p>

          <div className="info-bar" aria-label="BIS guidance highlights">
            <div className="info-item">
              <strong>8k+</strong>
              <span>standards indexed</span>
            </div>
            <div className="info-item">
              <strong>Source-backed</strong>
              <span>official BIS evidence</span>
            </div>
            <div className="info-item">
              <strong>English / Hindi / Telugu</strong>
              <span>multi-language support</span>
            </div>
          </div>

          <form className="query-form" onSubmit={submitQuestion}>
            <label htmlFor="question">{copy.askQuestion}</label>
            <div className="input-row">
              <textarea
                id="question"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                rows={3}
                maxLength={4000}
                placeholder={resolvedLanguage === "en" ? "Type your BIS question here..." : resolvedLanguage === "hi" ? "अपना BIS प्रश्न यहाँ लिखें..." : "మీ BIS ప్రశ్నను ఇక్కడ నమోదు చేయండి..."}
              />
              <button type="submit" className="submit-button" disabled={loading || !question.trim()}>
                {loading ? copy.searching : copy.askBIS}
                <span aria-hidden="true">→</span>
              </button>
            </div>
          </form>

          <div className="suggestions">
            <span>{copy.tryQuestion}</span>
            {suggestions.map((suggestion) => (
              <button key={suggestion} type="button" onClick={() => setQuestion(suggestion)}>
                {suggestion}
              </button>
            ))}
          </div>

          <div className="feature-strip" aria-label="BIS Sahayak highlights">
            {experienceHighlights.map((item) => (
              <article key={item.title} className="feature-card">
                <span className="feature-icon" aria-hidden="true">{item.icon}</span>
                <div>
                  <strong>{item.title}</strong>
                  <p>{item.text}</p>
                </div>
              </article>
            ))}
          </div>

          <div className="insight-rail">
            <div className="trust-banner">
              <div>
                <p className="mini-label">Why users trust BIS Sahayak</p>
                <h3>Guidance built for standards, safety, and compliance.</h3>
              </div>
              <div className="mini-metrics">
                <span><strong>8k+</strong> standards</span>
                <span><strong>3</strong> languages</span>
                <span><strong>24/7</strong> access</span>
              </div>
            </div>

            <div className="quick-actions" aria-label="Popular use cases">
              {quickUseCases.map((item) => (
                <button key={item} type="button" onClick={() => setQuestion(`Tell me about ${item.toLowerCase()} in the BIS context.`)}>
                  {item}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="notice error-notice" role="alert">
              <strong>Service note</strong>
              <span>{error}</span>
            </div>
          )}

          {response && <AnswerPanel response={response} />}

          <footer>Official-source grounding is still being expanded, but the app flow is now interactive, elegant, and user-friendly.</footer>
        </section>
      </div>
    </main>
  );
}

function AnswerPanel({ response }: { response: AssistantResponse }) {
  return (
    <section className="answer-panel" aria-live="polite">
      <div className="answer-meta">
        <span className={`confidence ${response.evidence_sufficient ? "verified" : "unverified"}`}>
          {response.evidence_sufficient ? "Evidence found" : "Needs verification"}
        </span>
        <span>{response.confidence} confidence</span>
      </div>

      <h2>Answer</h2>
      <p className="answer-copy">{response.answer}</p>

      {response.unknowns.length > 0 && (
        <div className="unknowns">
          <strong>Details still needed</strong>
          <p>{response.unknowns.join("; ")}</p>
        </div>
      )}

      {response.warnings.map((warning) => (
        <p className="warning" key={warning}>
          {warning}
        </p>
      ))}

      {response.citations.length > 0 ? (
        <div className="evidence-section">
          <div className="section-heading">
            <h3>Source evidence</h3>
            <span>
              {response.citations.length} reference{response.citations.length === 1 ? "" : "s"}
            </span>
          </div>

          <div className="citation-grid">
            {response.citations.map((citation) => (
              <CitationCard citation={citation} key={citation.evidence_id} />
            ))}
          </div>
        </div>
      ) : (
        <div className="notice">
          <strong>No verified evidence returned</strong>
          <span>The current knowledge base cannot support a BIS claim for this question yet.</span>
        </div>
      )}
    </section>
  );
}

function CitationCard({ citation }: { citation: Citation }) {
  return (
    <article className="citation-card">
      <div className="citation-topline">
        <span>Evidence</span>
        <span>{citation.page_number ? `Page ${citation.page_number}` : "Page unavailable"}</span>
      </div>
      <h4>{citation.standard_number ?? "Standard not identified"}</h4>
      <p className="citation-document">{citation.document_title ?? "Document title unavailable"}</p>
      <p className="citation-excerpt">“{citation.excerpt}”</p>
      <div className="citation-footer">
        <span>{citation.clause_number ? `Clause ${citation.clause_number}` : "Clause unavailable"}</span>
        {citation.source_url && (
          <a href={citation.source_url} target="_blank" rel="noreferrer">
            View source ↗
          </a>
        )}
      </div>
    </article>
  );
}
